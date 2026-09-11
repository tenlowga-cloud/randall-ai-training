#!/usr/bin/env python3
"""Portable, conservative installer for Randall AI Training.

The repository remains the canonical source.  Installation only creates skill
symlinks, small managed instruction blocks, hook entries, and local personal
state.  It never replaces an existing configuration file wholesale.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Iterable


OWNER = "randall-ai-training"
VERSION = 1
BLOCK_START = "<!-- BEGIN RANDALL AI TRAINING (managed by installer) -->"
BLOCK_END = "<!-- END RANDALL AI TRAINING (managed by installer) -->"


class InstallError(RuntimeError):
    """A safe, user-actionable installer failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: str(item.relative_to(root))):
        relative = str(path.relative_to(root)).replace(os.sep, "/").encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read valid JSON from {path}: {exc}") from exc


def _atomic_write_bytes_raw(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_bytes(path: Path, data: bytes, mode: int | None = None) -> None:
    """Patch point used by tests to prove transaction rollback."""
    _atomic_write_bytes_raw(path, data, mode)


def atomic_write_text(path: Path, text: str, mode: int | None = None) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), mode)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def command_for(script: Path, platform: str, state_dir: Path) -> str:
    parts = [sys.executable, str(script), "--platform", platform, "--state", str(state_dir)]
    if os.name == "nt":
        return subprocess.list2cmdline(parts)
    return shlex.join(parts)


def managed_block(runtime: Path, pointer: Path) -> str:
    return (
        f"{BLOCK_START}\n"
        "## Randall AI Training\n\n"
        f"Follow the runtime instructions in `{runtime}`.\n"
        f"Personal state is owned by `{pointer}`.\n"
        f"{BLOCK_END}"
    )


def append_block(original: str, block: str) -> str:
    if not original:
        return block + "\n"
    return original.rstrip() + "\n\n" + block + "\n"


def block_region(text: str) -> str | None:
    start = text.find(BLOCK_START)
    end = text.find(BLOCK_END)
    if start < 0 and end < 0:
        return None
    if start < 0 or end < 0 or end < start:
        return "__MALFORMED__"
    end += len(BLOCK_END)
    if text.find(BLOCK_START, start + len(BLOCK_START)) >= 0 or text.find(BLOCK_END, end) >= 0:
        return "__MALFORMED__"
    return text[start:end]


def remove_exact_block(text: str, expected: str) -> str:
    region = block_region(text)
    if region != expected:
        raise InstallError("managed instruction block has drifted")
    before, after = text.split(expected, 1)
    if before.strip() and after.strip():
        return before.rstrip() + "\n\n" + after.lstrip()
    return (before + after).strip() + ("\n" if (before + after).strip() else "")


def iter_skill_sources(skills_dir: Path) -> list[Path]:
    if not skills_dir.is_dir():
        raise InstallError(f"missing canonical skills directory: {skills_dir}")
    return sorted(
        (item for item in skills_dir.iterdir() if item.is_dir() and (item / "SKILL.md").is_file()),
        key=lambda item: item.name,
    )


def iter_personal_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise InstallError(f"personal template source is not a directory: {root}")
    return sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: str(item))


def load_object_json(path: Path, *, missing: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path_exists(path):
        return copy.deepcopy(missing if missing is not None else {})
    value = read_json(path)
    if not isinstance(value, dict):
        raise InstallError(f"expected a JSON object in {path}")
    return value


def event_groups(config: dict[str, Any], path: Path) -> list[Any]:
    hooks = config.get("hooks")
    if hooks is None:
        return []
    if not isinstance(hooks, dict):
        raise InstallError(f"hooks must be an object in {path}")
    groups = hooks.get("UserPromptSubmit")
    if groups is None:
        return []
    if not isinstance(groups, list):
        raise InstallError(f"hooks.UserPromptSubmit must be an array in {path}")
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            raise InstallError(f"each UserPromptSubmit group must contain a hooks array in {path}")
        if not all(isinstance(hook, dict) for hook in group["hooks"]):
            raise InstallError(f"each hook must be an object in {path}")
    return groups


def hook_group(command: str) -> dict[str, Any]:
    return {"hooks": [{"type": "command", "command": command, "timeout": 5}]}


def own_hook_collision(groups: list[Any], script: Path, expected: dict[str, Any]) -> bool:
    needle = str(script)
    for group in groups:
        for hook in group["hooks"]:
            command = hook.get("command")
            if isinstance(command, str) and needle in command and group != expected:
                return True
    return False


class Transaction:
    """On-disk before-images plus in-process rollback."""

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.ident = uuid.uuid4().hex
        self.backup_dir = state_dir / "backups" / self.ident
        self.index_path = self.backup_dir / "transaction.json"
        self.snapshots: list[dict[str, Any]] = []
        self.created_dirs: list[Path] = []
        self.ensure_dir(self.backup_dir)
        self._persist()

    def ensure_dir(self, path: Path) -> None:
        missing: list[Path] = []
        cursor = path
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        for item in reversed(missing):
            item.mkdir()
            self.created_dirs.append(item)

    def capture(self, path: Path) -> None:
        if any(item["path"] == str(path) for item in self.snapshots):
            return
        entry: dict[str, Any] = {"path": str(path)}
        if path.is_symlink():
            entry.update(kind="symlink", target=os.readlink(path))
        elif path.is_file():
            data = path.read_bytes()
            backup_name = f"{len(self.snapshots):04d}.bin"
            _atomic_write_bytes_raw(self.backup_dir / backup_name, data, 0o600)
            entry.update(kind="file", backup=backup_name, mode=stat.S_IMODE(path.stat().st_mode))
        elif path.exists():
            raise InstallError(f"refusing to replace non-file path: {path}")
        else:
            entry.update(kind="absent")
        self.snapshots.append(entry)
        self._persist()

    def secure_directory(self, path: Path) -> None:
        self.ensure_dir(path)
        if not any(item["path"] == str(path) for item in self.snapshots):
            self.snapshots.append(
                {"path": str(path), "kind": "dirmode", "mode": stat.S_IMODE(path.stat().st_mode)}
            )
            self._persist()
        os.chmod(path, 0o700)

    def _persist(self) -> None:
        payload = {
            "owner": OWNER,
            "version": VERSION,
            "status": "in-progress",
            "snapshots": self.snapshots,
            "created_dirs": [str(path) for path in self.created_dirs],
        }
        _atomic_write_bytes_raw(self.index_path, json_bytes(payload), 0o600)

    def complete(self) -> None:
        payload = {
            "owner": OWNER,
            "version": VERSION,
            "status": "complete",
            "snapshots": self.snapshots,
            "created_dirs": [str(path) for path in self.created_dirs],
        }
        _atomic_write_bytes_raw(self.index_path, json_bytes(payload), 0o600)

    def rollback(self) -> None:
        failures: list[str] = []
        for entry in reversed(self.snapshots):
            path = Path(entry["path"])
            try:
                if path_exists(path):
                    if entry["kind"] == "dirmode":
                        os.chmod(path, entry["mode"])
                        continue
                    if path.is_dir() and not path.is_symlink():
                        raise OSError("unexpected directory at rollback target")
                    path.unlink()
                if entry["kind"] == "file":
                    data = (self.backup_dir / entry["backup"]).read_bytes()
                    _atomic_write_bytes_raw(path, data, entry["mode"])
                elif entry["kind"] == "symlink":
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(entry["target"])
            except OSError as exc:
                failures.append(f"{path}: {exc}")
        shutil.rmtree(self.backup_dir, ignore_errors=True)
        for directory in reversed(self.created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        if failures:
            raise InstallError("rollback was incomplete: " + "; ".join(failures))


class Installer:
    def __init__(self, home: Path, source: Path) -> None:
        self.home = home.expanduser().resolve()
        self.source = source.expanduser().resolve()
        self.skills_source = self.source / "skills"
        self.personal_source = self.source / "templates" / "personal"
        self.runtime = self.source / "runtime.md"
        self.gate = self.source / "scripts" / "prompt_gate.py"
        self.state_dir = self.home / ".local" / "share" / "randall-ai"
        self.personal_dir = self.state_dir / "personal"
        self.pointer = self.state_dir / "LOCAL-STATE.md"
        self.manifest_path = self.state_dir / "install.json"
        self.docs = [self.home / ".codex" / "AGENTS.md", self.home / ".claude" / "CLAUDE.md"]
        self.hook_files = {
            "codex": self.home / ".codex" / "hooks.json",
            "claude": self.home / ".claude" / "settings.json",
        }

    def desired_pointer(self) -> str:
        return (
            "# Randall AI local state\n\n"
            f"Personal templates and state for this machine live in `{self.personal_dir}`.\n"
            f"The canonical runtime is `{self.runtime}`.\n"
        )

    def existing_manifest(self) -> dict[str, Any] | None:
        if not path_exists(self.manifest_path):
            return None
        value = load_object_json(self.manifest_path)
        if value.get("owner") != OWNER or value.get("version") != VERSION:
            raise InstallError(f"unrecognized installer manifest: {self.manifest_path}")
        if not isinstance(value.get("source"), str):
            raise InstallError(f"installer manifest has an invalid source: {self.manifest_path}")
        if not isinstance(value.get("python"), str):
            raise InstallError(f"installer manifest has an invalid Python executable: {self.manifest_path}")
        schemas: dict[str, dict[str, type]] = {
            "skills": {"target": str, "source": str, "sha256": str},
            "templates": {"path": str, "sha256": str},
            "blocks": {"path": str, "block": str},
            "hooks": {"path": str, "platform": str, "group": dict},
        }
        for key, required in schemas.items():
            entries = value.get(key)
            if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
                raise InstallError(f"installer manifest has an invalid {key} list: {self.manifest_path}")
            for entry in entries:
                if any(not isinstance(entry.get(field), expected) for field, expected in required.items()):
                    raise InstallError(f"installer manifest has an incomplete {key} entry: {self.manifest_path}")
        pointer = value.get("pointer")
        if not isinstance(pointer, dict) or not isinstance(pointer.get("path"), str) or not isinstance(pointer.get("sha256"), str):
            raise InstallError(f"installer manifest has an invalid pointer record: {self.manifest_path}")
        for item in value["skills"]:
            target, source = Path(item["target"]), Path(item["source"])
            allowed_parents = {self.home / ".claude" / "skills", self.home / ".agents" / "skills"}
            if target.parent not in allowed_parents or source.parent != self.skills_source:
                raise InstallError(f"installer manifest contains an out-of-scope skill record: {self.manifest_path}")
        for item in value["templates"]:
            path = Path(item["path"])
            if path != self.personal_dir and self.personal_dir not in path.parents:
                raise InstallError(f"installer manifest contains an out-of-scope personal record: {self.manifest_path}")
        if any(Path(item["path"]) not in self.docs for item in value["blocks"]):
            raise InstallError(f"installer manifest contains an out-of-scope instruction record: {self.manifest_path}")
        for item in value["hooks"]:
            if item["platform"] not in self.hook_files or Path(item["path"]) != self.hook_files[item["platform"]]:
                raise InstallError(f"installer manifest contains an out-of-scope hook record: {self.manifest_path}")
        if Path(pointer["path"]) != self.pointer:
            raise InstallError(f"installer manifest contains an out-of-scope pointer record: {self.manifest_path}")
        source_files = value.get("source_files")
        if not isinstance(source_files, dict):
            raise InstallError(f"installer manifest has invalid source hashes: {self.manifest_path}")
        for key, expected_path in (("runtime", self.runtime), ("prompt_gate", self.gate)):
            record = source_files.get(key)
            if not isinstance(record, dict) or record.get("path") != str(expected_path) or not isinstance(record.get("sha256"), str):
                raise InstallError(f"installer manifest has an invalid {key} hash: {self.manifest_path}")
        return value

    def _validate_source(self) -> list[Path]:
        if not self.source.is_dir():
            raise InstallError(f"source repository does not exist: {self.source}")
        if not self.runtime.is_file():
            raise InstallError(f"missing runtime instructions: {self.runtime}")
        if not self.gate.is_file():
            raise InstallError(f"missing prompt gate: {self.gate}")
        python = Path(sys.executable)
        if not python.is_file() or not os.access(python, os.X_OK):
            raise InstallError(f"hook Python executable is unavailable: {python}")
        return iter_skill_sources(self.skills_source)

    def _pending_transactions(self) -> tuple[list[Path], list[str]]:
        pending: list[Path] = []
        conflicts: list[str] = []
        backup_root = self.state_dir / "backups"
        if not backup_root.is_dir():
            return pending, conflicts
        for index_path in sorted(backup_root.glob("*/transaction.json")):
            try:
                payload = read_json(index_path)
                if not isinstance(payload, dict) or payload.get("owner") != OWNER or payload.get("version") != VERSION:
                    raise InstallError("unrecognized transaction metadata")
                if payload.get("status") != "in-progress":
                    continue
                snapshots = payload.get("snapshots")
                if not isinstance(snapshots, list) or not all(isinstance(item, dict) for item in snapshots):
                    raise InstallError("invalid snapshot list")
                # realpath normalizes platform aliases such as macOS /var -> /private/var.
                home_text = os.path.realpath(str(self.home))
                for item in snapshots:
                    path_text = item.get("path")
                    kind = item.get("kind")
                    if not isinstance(path_text, str) or kind not in {"absent", "file", "symlink", "dirmode"}:
                        raise InstallError("invalid snapshot entry")
                    candidate = os.path.realpath(path_text)
                    if os.path.commonpath((home_text, candidate)) != home_text:
                        raise InstallError("snapshot target is outside the selected home")
                    if kind == "file":
                        backup = item.get("backup")
                        if not isinstance(backup, str) or Path(backup).name != backup or not (index_path.parent / backup).is_file():
                            raise InstallError("snapshot backup is missing or invalid")
                        if not isinstance(item.get("mode"), int) or not 0 <= item["mode"] <= 0o7777:
                            raise InstallError("snapshot mode is invalid")
                    if kind == "symlink" and not isinstance(item.get("target"), str):
                        raise InstallError("snapshot symlink target is invalid")
                    if kind == "dirmode" and (not isinstance(item.get("mode"), int) or not 0 <= item["mode"] <= 0o7777):
                        raise InstallError("directory mode snapshot is invalid")
                created_dirs = payload.get("created_dirs", [])
                if not isinstance(created_dirs, list) or not all(isinstance(item, str) for item in created_dirs):
                    raise InstallError("invalid created directory list")
                for directory in created_dirs:
                    if os.path.commonpath((home_text, os.path.realpath(directory))) != home_text:
                        raise InstallError("created directory record is outside the selected home")
                pending.append(index_path)
            except (InstallError, OSError, ValueError) as exc:
                conflicts.append(f"cannot safely recover interrupted transaction {index_path}: {exc}")
        return pending, conflicts

    def _recover_transaction(self, index_path: Path) -> None:
        payload = read_json(index_path)
        for item in reversed(payload["snapshots"]):
            path = Path(item["path"])
            if path_exists(path):
                if item["kind"] == "dirmode":
                    if not path.is_dir() or path.is_symlink():
                        raise InstallError(f"directory mode recovery target changed: {path}")
                    os.chmod(path, item["mode"])
                    continue
                if path.is_dir() and not path.is_symlink():
                    raise InstallError(f"unexpected directory blocks recovery: {path}")
                path.unlink()
            if item["kind"] == "file":
                _atomic_write_bytes_raw(path, (index_path.parent / item["backup"]).read_bytes(), item.get("mode"))
            elif item["kind"] == "symlink":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(item["target"])
        for directory_text in reversed(payload.get("created_dirs", [])):
            directory = Path(directory_text)
            if directory == index_path.parent or directory in index_path.parents:
                continue
            try:
                directory.rmdir()
            except OSError:
                pass
        payload["status"] = "recovered"
        payload["recovered_at"] = int(time.time())
        _atomic_write_bytes_raw(index_path, json_bytes(payload), 0o600)

    def _recover_pending(self) -> list[str]:
        pending, conflicts = self._pending_transactions()
        if conflicts:
            raise InstallError("; ".join(conflicts))
        if pending:
            raise InstallError(
                "interrupted transaction needs scoped manual recovery; refusing to overwrite potentially newer user edits: "
                + ", ".join(str(path) for path in pending)
            )
        recovered: list[str] = []
        for index_path in pending:
            self._recover_transaction(index_path)
            recovered.append(str(index_path))
        return recovered

    def inspect_install(self) -> dict[str, Any]:
        conflicts: list[str] = []
        warnings: list[str] = []
        actions: list[str] = []
        if os.name == "nt":
            return {
                "ok": False,
                "conflicts": ["native Windows installation is not supported safely; use WSL"],
                "warnings": warnings,
                "actions": actions,
            }
        pending, transaction_conflicts = self._pending_transactions()
        conflicts.extend(transaction_conflicts)
        conflicts.extend(
            f"interrupted transaction requires scoped manual recovery because intervening edits cannot be ruled out: {path}"
            for path in pending
        )
        if pending or transaction_conflicts:
            warnings.append("use transaction before-images for review; the installer will not overwrite current files blindly")
            return {"ok": not conflicts, "conflicts": conflicts, "warnings": warnings, "actions": actions}
        try:
            skills = self._validate_source()
            manifest = self.existing_manifest()
        except InstallError as exc:
            return {"ok": False, "conflicts": [str(exc)], "warnings": warnings, "actions": actions}
        if manifest and Path(manifest.get("source", "")).resolve() != self.source:
            conflicts.append(f"manifest is owned by a different source: {manifest.get('source')}")
        previously_owned = {item["target"] for item in (manifest or {}).get("skills", [])}
        for skill in skills:
            for root in (self.home / ".claude" / "skills", self.home / ".agents" / "skills"):
                target = root / skill.name
                if path_exists(target):
                    if not target.is_symlink() or target.resolve() != skill.resolve():
                        conflicts.append(f"skill target collision: {target}")
                    elif manifest is None and str(target) not in previously_owned:
                        conflicts.append(f"orphaned Randall skill link without manifest: {target}")
                else:
                    actions.append(f"link {target} -> {skill}")
        if manifest:
            recorded_skills = {item["source"]: item["sha256"] for item in manifest["skills"]}
            for skill in skills:
                if str(skill) in recorded_skills and sha256_tree(skill) != recorded_skills[str(skill)]:
                    conflicts.append(f"canonical skill changed since install; review before update: {skill}")
            for key, path in (("runtime", self.runtime), ("prompt_gate", self.gate)):
                if sha256_bytes(path.read_bytes()) != manifest["source_files"][key]["sha256"]:
                    conflicts.append(f"canonical {key} changed since install; review before update: {path}")
        try:
            for source_file in iter_personal_files(self.personal_source):
                target = self.personal_dir / source_file.relative_to(self.personal_source)
                if not path_exists(target):
                    actions.append(f"copy personal template without overwrite: {target}")
        except InstallError as exc:
            conflicts.append(str(exc))
        block = managed_block(self.runtime, self.pointer)
        for doc in self.docs:
            if path_exists(doc) and not doc.is_file():
                conflicts.append(f"instruction target is not a file: {doc}")
                continue
            text = doc.read_text(encoding="utf-8") if doc.exists() else ""
            region = block_region(text)
            if region == "__MALFORMED__":
                conflicts.append(f"malformed or duplicate managed block: {doc}")
            elif region is not None and region != block:
                conflicts.append(f"managed block drift: {doc}")
            elif region is None:
                actions.append(f"append managed block to {doc}")
        for platform, path in self.hook_files.items():
            try:
                config = load_object_json(path)
                groups = event_groups(config, path)
            except InstallError as exc:
                conflicts.append(str(exc))
                continue
            group = hook_group(command_for(self.gate, platform, self.state_dir))
            if own_hook_collision(groups, self.gate, group):
                conflicts.append(f"colliding Randall prompt hook in {path}")
            elif group not in groups:
                actions.append(f"add {platform} UserPromptSubmit hook to {path}")
        if path_exists(self.pointer):
            if not self.pointer.is_file():
                conflicts.append(f"local state pointer target is not a file: {self.pointer}")
        else:
            actions.append(f"create local state pointer {self.pointer}")
        if (self.home / ".codex" / "AGENTS.override.md").exists():
            warnings.append("~/.codex/AGENTS.override.md exists and may shadow ~/.codex/AGENTS.md")
        return {"ok": not conflicts, "conflicts": conflicts, "warnings": warnings, "actions": actions}

    def apply(self) -> dict[str, Any]:
        try:
            recovered = self._recover_pending()
        except InstallError as exc:
            return {"status": "conflict", "ok": False, "conflicts": [str(exc)], "actions": []}
        inspection = self.inspect_install()
        if not inspection["ok"]:
            return {"status": "conflict", **inspection}
        skills = self._validate_source()
        existing_manifest = self.existing_manifest()
        if existing_manifest is not None and not inspection["actions"]:
            return {
                "status": "already-installed",
                "ok": True,
                "warnings": inspection["warnings"],
                "manifest": str(self.manifest_path),
                "recovered_transactions": recovered,
            }
        old_manifest = existing_manifest or {}
        transaction: Transaction | None = None
        created_skills = list(old_manifest.get("skills", []))
        created_templates = list(old_manifest.get("templates", []))
        block_records = list(old_manifest.get("blocks", []))
        hook_records = list(old_manifest.get("hooks", []))
        try:
            transaction = Transaction(self.state_dir)
            transaction.secure_directory(self.state_dir)
            owned_skill_targets = {item["target"] for item in created_skills}
            for skill in skills:
                for root in (self.home / ".claude" / "skills", self.home / ".agents" / "skills"):
                    target = root / skill.name
                    if not path_exists(target):
                        transaction.ensure_dir(target.parent)
                        transaction.capture(target)
                        target.symlink_to(skill, target_is_directory=True)
                        created_skills.append({"target": str(target), "source": str(skill), "sha256": sha256_tree(skill)})
                        owned_skill_targets.add(str(target))
            for source_file in iter_personal_files(self.personal_source):
                relative = source_file.relative_to(self.personal_source)
                target = self.personal_dir / relative
                if not path_exists(target):
                    transaction.ensure_dir(target.parent)
                    transaction.secure_directory(self.personal_dir)
                    transaction.secure_directory(target.parent)
                    transaction.capture(target)
                    data = source_file.read_bytes()
                    atomic_write_bytes(target, data, 0o600)
                    created_templates.append({"path": str(target), "sha256": sha256_bytes(data)})
            block = managed_block(self.runtime, self.pointer)
            recorded_docs = {item["path"] for item in block_records}
            for doc in self.docs:
                text = doc.read_text(encoding="utf-8") if doc.exists() else ""
                if block_region(text) is None:
                    existed_before = doc.exists()
                    transaction.ensure_dir(doc.parent)
                    transaction.capture(doc)
                    atomic_write_text(doc, append_block(text, block))
                    if str(doc) not in recorded_docs:
                        block_records.append({"path": str(doc), "block": block, "existed_before": existed_before})
            recorded_hooks = {item["path"] for item in hook_records}
            for platform, path in self.hook_files.items():
                existed_before = path.exists()
                config = load_object_json(path)
                groups = event_groups(config, path)
                group = hook_group(command_for(self.gate, platform, self.state_dir))
                if group not in groups:
                    updated = copy.deepcopy(config)
                    updated.setdefault("hooks", {}).setdefault("UserPromptSubmit", []).append(group)
                    transaction.ensure_dir(path.parent)
                    transaction.capture(path)
                    atomic_write_bytes(path, json_bytes(updated))
                    if str(path) not in recorded_hooks:
                        hook_records.append(
                            {"path": str(path), "platform": platform, "group": group, "existed_before": existed_before}
                        )
            pointer_existed = self.pointer.exists()
            if not pointer_existed:
                transaction.capture(self.pointer)
                atomic_write_text(self.pointer, self.desired_pointer(), 0o600)
            manifest = {
                "owner": OWNER,
                "version": VERSION,
                "source": str(self.source),
                "installed_at": int(time.time()),
                "python": sys.executable,
                "source_files": {
                    "runtime": {"path": str(self.runtime), "sha256": sha256_bytes(self.runtime.read_bytes())},
                    "prompt_gate": {"path": str(self.gate), "sha256": sha256_bytes(self.gate.read_bytes())},
                },
                "backup_transaction": str(transaction.index_path),
                "skills": created_skills,
                "templates": created_templates,
                "blocks": block_records,
                "hooks": hook_records,
                "pointer": {
                    "path": str(self.pointer),
                    "sha256": sha256_bytes(self.desired_pointer().encode("utf-8")),
                    "existed_before": bool(old_manifest.get("pointer", {}).get("existed_before", pointer_existed)),
                },
            }
            transaction.capture(self.manifest_path)
            atomic_write_bytes(self.manifest_path, json_bytes(manifest), 0o600)
            transaction.complete()
            return {
                "status": "installed",
                "ok": True,
                "warnings": inspection["warnings"],
                "manifest": str(self.manifest_path),
                "recovered_transactions": recovered,
            }
        except Exception as exc:
            rollback_error = None
            if transaction is not None:
                try:
                    transaction.rollback()
                except Exception as rollback_exc:  # pragma: no cover - exceptional disk failure
                    rollback_error = str(rollback_exc)
            message = f"installation failed and was rolled back: {exc}"
            if rollback_error:
                message += f"; {rollback_error}"
            return {"status": "error", "ok": False, "errors": [message]}

    def doctor(self) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        verified_hooks = 0
        pending, transaction_conflicts = self._pending_transactions()
        findings.extend({"level": "error", "message": message} for message in transaction_conflicts)
        findings.extend(
            {"level": "error", "message": f"interrupted transaction needs recovery: {path}"} for path in pending
        )
        try:
            manifest = self.existing_manifest()
        except InstallError as exc:
            return {"status": "unhealthy", "ok": False, "findings": [{"level": "error", "message": str(exc)}]}
        if manifest is None:
            findings.append({"level": "error", "message": "installer manifest is missing"})
            return {"status": "unhealthy", "ok": False, "findings": findings}
        if Path(manifest.get("source", "")).resolve() != self.source:
            findings.append({"level": "error", "message": "manifest source does not match requested source"})
        python = Path(manifest.get("python", ""))
        if not python.is_file() or not os.access(python, os.X_OK):
            findings.append({"level": "error", "message": f"hook Python executable is unavailable: {python}"})
        for key, path in (("runtime", self.runtime), ("prompt_gate", self.gate)):
            record = manifest["source_files"][key]
            if not path.is_file() or sha256_bytes(path.read_bytes()) != record["sha256"]:
                findings.append(
                    {"level": "error", "message": f"canonical {key} drifted; review before uninstall and re-apply: {path}"}
                )
        for item in manifest.get("skills", []):
            target, source = Path(item["target"]), Path(item["source"])
            if not source.is_dir() or not (source / "SKILL.md").is_file():
                findings.append({"level": "error", "message": f"canonical skill source is missing: {source}"})
            elif sha256_tree(source) != item["sha256"]:
                findings.append(
                    {"level": "error", "message": f"canonical skill drifted; review before uninstall and re-apply: {source}"}
                )
            elif not target.is_symlink() or target.resolve() != source.resolve():
                findings.append({"level": "error", "message": f"skill link drift: {target}"})
        pointer = Path(manifest["pointer"]["path"])
        if not pointer.is_file():
            findings.append({"level": "error", "message": f"local state pointer is missing or unusable: {pointer}"})
        for item in manifest.get("blocks", []):
            path = Path(item["path"])
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            if block_region(text) != item["block"]:
                findings.append({"level": "error", "message": f"managed block drift: {path}"})
        for item in manifest.get("hooks", []):
            path = Path(item["path"])
            try:
                groups = event_groups(load_object_json(path), path)
            except InstallError as exc:
                findings.append({"level": "error", "message": str(exc)})
                continue
            if item["group"] not in groups:
                findings.append({"level": "error", "message": f"configured hook missing or changed: {path}"})
            receipt = self.state_dir / "receipts" / f"{item['platform']}.json"
            if receipt.is_file():
                try:
                    receipt_data = load_object_json(receipt)
                    observations = receipt_data.get("observations")
                    latest = observations[-1] if isinstance(observations, list) and observations else None
                    if (
                        isinstance(latest, dict)
                        and latest.get("event") == "UserPromptSubmit"
                        and latest.get("platform") == item["platform"]
                        and isinstance(latest.get("observed_at_ns"), int)
                    ):
                        verified_hooks += 1
                        findings.append({"level": "info", "message": f"{item['platform']} hook has an execution receipt"})
                    else:
                        findings.append({"level": "warning", "message": f"{item['platform']} receipt is invalid"})
                except InstallError:
                    findings.append({"level": "warning", "message": f"{item['platform']} receipt is unreadable"})
            else:
                findings.append(
                    {
                        "level": "warning",
                        "message": f"{item['platform']} hook structure is configured; runtime execution is not verified",
                    }
                )
        override = self.home / ".codex" / "AGENTS.override.md"
        if override.exists():
            findings.append({"level": "warning", "message": f"{override} may shadow the managed AGENTS.md block"})
        ok = not any(item["level"] == "error" for item in findings)
        if not ok:
            status = "unhealthy"
        elif verified_hooks < len(manifest.get("hooks", [])):
            status = "configured-unverified"
        else:
            status = "healthy"
        return {"status": status, "ok": ok, "findings": findings}

    def inspect_uninstall(self) -> dict[str, Any]:
        conflicts: list[str] = []
        actions: list[str] = []
        try:
            manifest = self.existing_manifest()
        except InstallError as exc:
            return {"ok": False, "conflicts": [str(exc)], "actions": actions}
        if manifest is None:
            return {"ok": True, "conflicts": [], "actions": [], "status": "not-installed"}
        for item in manifest.get("skills", []):
            target, source = Path(item["target"]), Path(item["source"])
            if not target.is_symlink() or target.resolve() != source.resolve():
                conflicts.append(f"owned skill link changed or missing: {target}")
            else:
                actions.append(f"remove skill link {target}")
        for item in manifest.get("blocks", []):
            path = Path(item["path"])
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            if block_region(text) != item["block"]:
                conflicts.append(f"owned instruction block changed or missing: {path}")
            else:
                actions.append(f"remove managed block from {path}")
        for item in manifest.get("hooks", []):
            path = Path(item["path"])
            try:
                groups = event_groups(load_object_json(path), path)
            except InstallError as exc:
                conflicts.append(str(exc))
                continue
            if item["group"] not in groups:
                conflicts.append(f"owned hook changed or missing: {path}")
            else:
                actions.append(f"remove managed hook from {path}")
        return {"ok": not conflicts, "conflicts": conflicts, "actions": actions}

    def uninstall(self) -> dict[str, Any]:
        try:
            self._recover_pending()
        except InstallError as exc:
            return {"status": "conflict", "ok": False, "conflicts": [str(exc)], "actions": []}
        inspection = self.inspect_uninstall()
        if inspection.get("status") == "not-installed":
            return {"status": "not-installed", "ok": True}
        if not inspection["ok"]:
            return {"status": "conflict", **inspection}
        manifest = self.existing_manifest()
        assert manifest is not None
        transaction: Transaction | None = None
        try:
            transaction = Transaction(self.state_dir)
            for item in manifest.get("skills", []):
                target = Path(item["target"])
                transaction.capture(target)
                target.unlink()
            for item in manifest.get("blocks", []):
                path = Path(item["path"])
                original = path.read_text(encoding="utf-8")
                updated = remove_exact_block(original, item["block"])
                transaction.capture(path)
                if not updated and not item.get("existed_before", True):
                    path.unlink()
                else:
                    atomic_write_text(path, updated)
            for item in manifest.get("hooks", []):
                path = Path(item["path"])
                config = load_object_json(path)
                updated = copy.deepcopy(config)
                groups = updated["hooks"]["UserPromptSubmit"]
                groups.remove(item["group"])
                if not groups:
                    del updated["hooks"]["UserPromptSubmit"]
                if not updated["hooks"]:
                    del updated["hooks"]
                transaction.capture(path)
                if not updated and not item.get("existed_before", True):
                    path.unlink()
                else:
                    atomic_write_bytes(path, json_bytes(updated))
            transaction.capture(self.manifest_path)
            self.manifest_path.unlink()
            transaction.complete()
            return {"status": "uninstalled", "ok": True, "backup_transaction": str(transaction.index_path)}
        except Exception as exc:
            rollback_error = None
            if transaction is not None:
                try:
                    transaction.rollback()
                except Exception as rollback_exc:  # pragma: no cover
                    rollback_error = str(rollback_exc)
            message = f"uninstall failed and was rolled back: {exc}"
            if rollback_error:
                message += f"; {rollback_error}"
            return {"status": "error", "ok": False, "errors": [message]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    default_source = Path(__file__).resolve().parents[1]
    for name in ("plan", "apply", "doctor", "uninstall"):
        command = subparsers.add_parser(name)
        command.add_argument("--home", type=Path, default=Path.home(), help="target home (defaults to current user)")
        command.add_argument("--source", type=Path, default=default_source, help="retained canonical repository root")
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 11):
        print(
            json.dumps(
                {
                    "status": "unsupported-python",
                    "ok": False,
                    "errors": ["Randall AI Training requires Python 3.11 or newer; no changes were made"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    args = build_parser().parse_args(argv)
    installer = Installer(args.home, args.source)
    if args.action == "plan":
        result = installer.inspect_install()
        result["status"] = "ready" if result["ok"] else "conflict"
    elif args.action == "apply":
        result = installer.apply()
    elif args.action == "doctor":
        result = installer.doctor()
    else:
        result = installer.uninstall()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())

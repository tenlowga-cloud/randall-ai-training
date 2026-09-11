from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("randall_install", MODULE_PATH)
assert SPEC and SPEC.loader
install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install)


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.home = root / "Home With Spaces"
        self.source = root / "Retained Repo With Spaces"
        (self.source / "scripts").mkdir(parents=True)
        (self.source / "skills" / "sample-skill").mkdir(parents=True)
        (self.source / "templates" / "personal" / "nested").mkdir(parents=True)
        (self.source / "runtime.md").write_text("# Runtime\n", encoding="utf-8")
        (self.source / "scripts" / "prompt_gate.py").write_text("# gate\n", encoding="utf-8")
        (self.source / "skills" / "sample-skill" / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        (self.source / "templates" / "personal" / "nested" / "owner.md").write_text(
            "personal template\n", encoding="utf-8"
        )
        self.installer = install.Installer(self.home, self.source)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_apply_preserves_existing_hooks_quotes_paths_and_is_idempotent(self) -> None:
        codex = self.home / ".codex"
        claude = self.home / ".claude"
        codex.mkdir(parents=True)
        claude.mkdir(parents=True)
        existing_group = {"matcher": "anything", "hooks": [{"type": "command", "command": "existing-hook"}]}
        (codex / "hooks.json").write_text(
            json.dumps({"unrelated": {"keep": True}, "hooks": {"UserPromptSubmit": [existing_group]}}),
            encoding="utf-8",
        )
        (claude / "settings.json").write_text(json.dumps({"theme": "dark"}), encoding="utf-8")
        (codex / "AGENTS.md").write_text("User Codex instructions.\n", encoding="utf-8")
        (claude / "CLAUDE.md").write_text("User Claude instructions.\n", encoding="utf-8")

        plan = self.installer.inspect_install()
        self.assertTrue(plan["ok"], plan)
        result = self.installer.apply()
        self.assertTrue(result["ok"], result)

        codex_config = json.loads((codex / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(codex_config["unrelated"], {"keep": True})
        self.assertEqual(codex_config["hooks"]["UserPromptSubmit"][0], existing_group)
        command = codex_config["hooks"]["UserPromptSubmit"][1]["hooks"][0]["command"]
        if os.name != "nt":
            self.assertEqual(
                shlex.split(command),
                [
                    install.sys.executable,
                    str(self.installer.gate),
                    "--platform",
                    "codex",
                    "--state",
                    str(self.installer.state_dir),
                ],
            )
        self.assertTrue((self.home / ".claude" / "skills" / "sample-skill").is_symlink())
        self.assertTrue((self.home / ".agents" / "skills" / "sample-skill").is_symlink())
        self.assertFalse((self.home / ".codex" / "skills" / "sample-skill").exists())
        self.assertEqual(
            (self.home / ".local" / "share" / "randall-ai" / "personal" / "nested" / "owner.md").read_text(),
            "personal template\n",
        )
        first_config = (codex / "hooks.json").read_bytes()
        second = self.installer.apply()
        self.assertTrue(second["ok"], second)
        self.assertEqual(first_config, (codex / "hooks.json").read_bytes())
        self.assertEqual((codex / "AGENTS.md").read_text().count(install.BLOCK_START), 1)

    def test_uninstall_removes_only_owned_fragments_and_keeps_later_edits(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        hooks_path = self.home / ".codex" / "hooks.json"
        config = json.loads(hooks_path.read_text(encoding="utf-8"))
        config["later_user_setting"] = 42
        hooks_path.write_text(json.dumps(config), encoding="utf-8")
        agents = self.home / ".codex" / "AGENTS.md"
        agents.write_text(agents.read_text() + "Later user instruction.\n", encoding="utf-8")
        personal = self.home / ".local" / "share" / "randall-ai" / "personal" / "nested" / "owner.md"
        personal.write_text("evolved personal knowledge\n", encoding="utf-8")
        pointer = self.installer.pointer
        pointer.write_text("# Migrated\n\nCanonical personal owner: vault://new-owner\n", encoding="utf-8")

        result = self.installer.uninstall()
        self.assertTrue(result["ok"], result)
        remaining = json.loads(hooks_path.read_text(encoding="utf-8"))
        self.assertEqual(remaining, {"later_user_setting": 42})
        self.assertEqual(agents.read_text(encoding="utf-8"), "Later user instruction.\n")
        self.assertFalse((self.home / ".agents" / "skills" / "sample-skill").exists())
        self.assertEqual(personal.read_text(), "evolved personal knowledge\n")
        self.assertIn("vault://new-owner", pointer.read_text())

    def test_uninstall_refuses_managed_block_drift_without_changes(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        agents = self.home / ".codex" / "AGENTS.md"
        agents.write_text(agents.read_text().replace("Randall AI Training", "Changed Randall"), encoding="utf-8")
        link = self.home / ".agents" / "skills" / "sample-skill"

        result = self.installer.uninstall()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "conflict")
        self.assertTrue(link.is_symlink())
        self.assertTrue(self.installer.manifest_path.exists())

    def test_wrong_symlink_is_a_preflight_conflict(self) -> None:
        wrong = self.home / "wrong"
        wrong.mkdir(parents=True)
        target = self.home / ".agents" / "skills" / "sample-skill"
        target.parent.mkdir(parents=True)
        target.symlink_to(wrong, target_is_directory=True)

        result = self.installer.apply()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(target.resolve(), wrong.resolve())
        self.assertFalse(self.installer.manifest_path.exists())

    def test_malformed_existing_json_is_refused_before_mutation(self) -> None:
        settings = self.home / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{broken", encoding="utf-8")

        result = self.installer.apply()
        self.assertFalse(result["ok"])
        self.assertEqual(settings.read_text(), "{broken")
        self.assertFalse((self.home / ".agents" / "skills" / "sample-skill").exists())

    def test_personal_copy_never_overwrites_or_claims_existing_file(self) -> None:
        target = self.home / ".local" / "share" / "randall-ai" / "personal" / "nested" / "owner.md"
        target.parent.mkdir(parents=True)
        target.write_text("user-owned\n", encoding="utf-8")
        result = self.installer.apply()
        self.assertTrue(result["ok"], result)
        self.assertEqual(target.read_text(), "user-owned\n")
        manifest = json.loads(self.installer.manifest_path.read_text())
        self.assertNotIn(str(target), {item["path"] for item in manifest["templates"]})

    def test_cli_plan_has_stable_machine_readable_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "plan", "--home", str(self.home), "--source", str(self.source)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["ok"])
        self.assertFalse(self.installer.manifest_path.exists())

    def test_write_failure_rolls_back_prior_writes(self) -> None:
        original = install.atomic_write_bytes
        calls = 0

        def fail_after_first(path: Path, data: bytes, mode: int | None = None) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected write failure")
            original(path, data, mode)

        with mock.patch.object(install, "atomic_write_bytes", side_effect=fail_after_first):
            result = self.installer.apply()

        self.assertFalse(result["ok"])
        self.assertIn("rolled back", result["errors"][0])
        self.assertFalse((self.home / ".agents" / "skills" / "sample-skill").exists())
        self.assertFalse((self.home / ".claude" / "skills" / "sample-skill").exists())
        self.assertFalse(self.installer.manifest_path.exists())

    def test_doctor_distinguishes_configuration_from_execution_receipt(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        before = self.installer.doctor()
        messages = [item["message"] for item in before["findings"]]
        self.assertEqual(before["status"], "configured-unverified")
        self.assertTrue(any("runtime execution is not verified" in message for message in messages))
        receipt = self.installer.state_dir / "receipts" / "codex.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            json.dumps(
                {
                    "version": 1,
                    "observations": [
                        {"event": "UserPromptSubmit", "platform": "codex", "observed_at_ns": 123}
                    ],
                }
            ),
            encoding="utf-8",
        )
        after = self.installer.doctor()
        messages = [item["message"] for item in after["findings"]]
        self.assertIn("codex hook has an execution receipt", messages)

    def test_fresh_local_state_and_seeded_personal_files_are_private(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        personal = self.installer.personal_dir / "nested" / "owner.md"
        self.assertEqual(self.installer.state_dir.stat().st_mode & 0o777, 0o700)
        self.assertEqual(personal.stat().st_mode & 0o777, 0o600)

    def test_doctor_reports_runtime_hash_drift_before_rebaseline(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        (self.source / "runtime.md").write_text("# Reviewed new runtime\n", encoding="utf-8")
        result = self.installer.doctor()
        self.assertFalse(result["ok"])
        self.assertTrue(any("canonical runtime drifted" in item["message"] for item in result["findings"]))

    def test_interrupted_transaction_refuses_blind_recovery(self) -> None:
        interrupted = install.Transaction(self.installer.state_dir)
        partial = self.home / ".codex" / "hooks.json"
        interrupted.ensure_dir(partial.parent)
        interrupted.capture(partial)
        install.atomic_write_text(partial, '{"partial": true}\n')
        plan = self.installer.inspect_install()
        self.assertFalse(plan["ok"])
        self.assertTrue(any("scoped manual recovery" in conflict for conflict in plan["conflicts"]))

        result = self.installer.apply()
        self.assertFalse(result["ok"])
        self.assertEqual(json.loads(partial.read_text()), {"partial": True})
        self.assertEqual(json.loads(interrupted.index_path.read_text())["status"], "in-progress")

    def test_doctor_flags_missing_canonical_skill_even_when_link_text_matches(self) -> None:
        self.assertTrue(self.installer.apply()["ok"])
        skill_source = self.source / "skills" / "sample-skill"
        moved = self.source / "skills" / "sample-skill-moved"
        skill_source.rename(moved)
        result = self.installer.doctor()
        self.assertFalse(result["ok"])
        self.assertTrue(any("canonical skill source is missing" in item["message"] for item in result["findings"]))

    def test_unsupported_python_exits_before_writing(self) -> None:
        output = io.StringIO()
        with mock.patch.object(install.sys, "version_info", (3, 10, 9)), contextlib.redirect_stdout(output):
            code = install.main(["apply", "--home", str(self.home), "--source", str(self.source)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "unsupported-python")
        self.assertFalse(self.home.exists())


if __name__ == "__main__":
    unittest.main()

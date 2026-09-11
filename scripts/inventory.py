#!/usr/bin/env python3
"""Print a bounded, read-only AI workstation inventory as JSON.

The report deliberately omits hostnames, addresses, serial numbers,
environment variables, secrets, network state, SSH state, and source paths.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
MAX_DIRECTORY_ENTRIES = 512
MAX_SCANNED_ENTRIES = 2_048
MAX_GPU_DEVICES = 32
GPU_TIMEOUT_SECONDS = 3

CLI_NAMES = (
    "python3",
    "git",
    "codex",
    "claude",
    "docker",
    "podman",
    "ollama",
    "nvidia-smi",
)

SKILL_LOCATIONS = (
    ("agents", Path(".agents") / "skills", False),
    ("claude", Path(".claude") / "skills", False),
    ("codex_legacy", Path(".codex") / "skills", True),
)


def known_text(value: str | None) -> str:
    """Use a visible unknown marker instead of an empty value."""
    if value is None:
        return "unknown"
    cleaned = value.strip()
    return cleaned if cleaned else "unknown"


def available_ram_bytes() -> int | None:
    """Return currently available RAM when POSIX exposes it safely."""
    try:
        pages = os.sysconf("SC_AVPHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (AttributeError, KeyError, OSError, TypeError, ValueError):
        return None
    if not isinstance(pages, int) or not isinstance(page_size, int):
        return None
    if pages < 0 or page_size <= 0:
        return None
    return pages * page_size


def disk_free_bytes(home: Path) -> int | None:
    """Return free bytes on the filesystem containing the selected home."""
    try:
        free = shutil.disk_usage(home).free
    except OSError:
        return None
    return free if isinstance(free, int) and free >= 0 else None


def bounded_directory_names(directory: Path) -> dict[str, Any]:
    """List immediate directory or symlink names without opening their files."""
    try:
        if not directory.is_dir():
            return {"status": "unknown", "names": None, "truncated": False}
        names: list[str] = []
        scanned = 0
        truncated = False
        with os.scandir(directory) as entries:
            for entry in entries:
                scanned += 1
                if scanned > MAX_SCANNED_ENTRIES:
                    truncated = True
                    break
                try:
                    eligible = entry.is_dir(follow_symlinks=False) or entry.is_symlink()
                except OSError:
                    continue
                if not eligible:
                    continue
                if len(names) >= MAX_DIRECTORY_ENTRIES:
                    truncated = True
                    break
                names.append(entry.name)
    except OSError:
        return {"status": "unknown", "names": None, "truncated": False}
    return {"status": "available", "names": sorted(names), "truncated": truncated}


def cli_inventory() -> dict[str, str]:
    """Report fixed CLI discovery without exposing executable paths."""
    return {
        name: "available" if shutil.which(name) is not None else "not_found_in_path"
        for name in CLI_NAMES
    }


def parse_mib(value: str, *, allow_zero: bool) -> int | str:
    """Parse nvidia-smi MiB output while preserving a real zero."""
    try:
        number = int(value.strip())
    except (TypeError, ValueError):
        return "unknown"
    if number < 0 or (number == 0 and not allow_zero):
        return "unknown"
    return number


def gpu_inventory() -> dict[str, Any]:
    """Run one fixed, timeout-bounded nvidia-smi query when available."""
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return {"status": "unknown", "reason": "nvidia-smi_not_found", "devices": None}

    command = [
        executable,
        "--query-gpu=name,memory.total,memory.free,driver_version",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GPU_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "unknown", "reason": "query_timed_out", "devices": None}
    except OSError:
        return {"status": "unknown", "reason": "query_failed", "devices": None}

    if result.returncode != 0:
        return {"status": "unknown", "reason": "query_failed", "devices": None}

    rows = list(csv.reader(result.stdout.splitlines()))
    if not rows:
        return {"status": "unknown", "reason": "no_devices_reported", "devices": None}

    devices: list[dict[str, Any]] = []
    malformed = 0
    for row in rows[:MAX_GPU_DEVICES]:
        if len(row) != 4:
            malformed += 1
            continue
        model, total, free, driver = row
        devices.append(
            {
                "model": known_text(model),
                "vram_total_mib": parse_mib(total, allow_zero=False),
                "vram_free_mib": parse_mib(free, allow_zero=True),
                "driver_version": known_text(driver),
            }
        )

    if not devices:
        return {"status": "unknown", "reason": "unrecognized_output", "devices": None}

    status = "partial" if malformed else "available"
    return {
        "status": status,
        "devices": devices,
        "truncated": len(rows) > MAX_GPU_DEVICES,
    }


def skill_inventory(home: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label, relative_path, legacy in SKILL_LOCATIONS:
        item = bounded_directory_names(home / relative_path)
        item["legacy"] = legacy
        result[label] = item
    return result


def vault_inventory(vault: Path | None) -> dict[str, Any]:
    """Inspect only immediate Obsidian plugin directory names when requested."""
    if vault is None:
        return {"status": "not_requested", "obsidian_plugin_names": None}
    try:
        if not vault.is_dir():
            return {"status": "unknown", "obsidian_plugin_names": None}
    except OSError:
        return {"status": "unknown", "obsidian_plugin_names": None}

    plugins = bounded_directory_names(vault / ".obsidian" / "plugins")
    return {
        "status": plugins["status"],
        "obsidian_plugin_names": plugins["names"],
        "truncated": plugins["truncated"],
    }


def collect_inventory(home: Path, vault: Path | None = None) -> dict[str, Any]:
    ram = available_ram_bytes()
    disk = disk_free_bytes(home)
    return {
        "schema_version": SCHEMA_VERSION,
        "privacy": {
            "paths_omitted": True,
            "host_and_network_identifiers_omitted": True,
            "secrets_and_process_context_omitted": True,
            "read_only": True,
        },
        "system": {
            "os": known_text(platform.system()),
            "cpu_architecture": known_text(platform.machine()),
            "ram_available_bytes": ram if ram is not None else "unknown",
            "disk_free_bytes": disk if disk is not None else "unknown",
        },
        "gpu": gpu_inventory(),
        "cli": cli_inventory(),
        "skills": skill_inventory(home),
        "vault": vault_inventory(vault),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--home",
        type=Path,
        help="Use this home directory for bounded fixture or alternate-home inspection.",
    )
    parser.add_argument(
        "--vault",
        type=Path,
        help="Inspect only .obsidian plugin directory names in this explicitly selected vault.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    home = args.home.expanduser() if args.home is not None else Path.home()
    vault = args.vault.expanduser() if args.vault is not None else None
    payload = collect_inventory(home, vault)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "inventory.py"
SPEC = importlib.util.spec_from_file_location("randall_inventory", MODULE_PATH)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_collects_bounded_names_and_fixed_gpu_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "Private Home"
            vault = root / "Private Vault"
            for path in (
                home / ".agents" / "skills" / "alpha-skill",
                home / ".claude" / "skills" / "beta-skill",
                home / ".codex" / "skills" / "legacy-skill",
                vault / ".obsidian" / "plugins" / "approved-plugin",
            ):
                path.mkdir(parents=True)

            secret = "DO-NOT-REPORT-private-note-token"
            (vault / "Private Note.md").write_text(secret, encoding="utf-8")
            (vault / ".obsidian" / "app.json").write_text(secret, encoding="utf-8")

            def which(name: str) -> str | None:
                return f"/private/bin/{name}" if name in {"python3", "nvidia-smi"} else None

            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="NVIDIA Test GPU, 24576, 0, 555.42\n",
                stderr="",
            )
            disk = mock.Mock(free=250)

            with (
                mock.patch.object(inventory.platform, "system", return_value="Linux"),
                mock.patch.object(inventory.platform, "machine", return_value="x86_64"),
                mock.patch.object(inventory, "available_ram_bytes", return_value=8_589_934_592),
                mock.patch.object(inventory.shutil, "disk_usage", return_value=disk),
                mock.patch.object(inventory.shutil, "which", side_effect=which),
                mock.patch.object(inventory.subprocess, "run", return_value=completed) as run,
            ):
                payload = inventory.collect_inventory(home, vault)

            self.assertEqual(payload["system"]["ram_available_bytes"], 8_589_934_592)
            self.assertEqual(payload["system"]["disk_free_bytes"], 250)
            self.assertEqual(payload["skills"]["agents"]["names"], ["alpha-skill"])
            self.assertEqual(payload["skills"]["claude"]["names"], ["beta-skill"])
            self.assertEqual(payload["skills"]["codex_legacy"]["names"], ["legacy-skill"])
            self.assertTrue(payload["skills"]["codex_legacy"]["legacy"])
            self.assertEqual(payload["vault"]["obsidian_plugin_names"], ["approved-plugin"])
            self.assertEqual(payload["gpu"]["devices"][0]["vram_total_mib"], 24576)
            self.assertEqual(payload["gpu"]["devices"][0]["vram_free_mib"], 0)
            self.assertEqual(payload["cli"]["python3"], "available")
            self.assertEqual(payload["cli"]["claude"], "not_found_in_path")

            command = run.call_args.args[0]
            self.assertEqual(
                command[1:],
                [
                    "--query-gpu=name,memory.total,memory.free,driver_version",
                    "--format=csv,noheader,nounits",
                ],
            )
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertEqual(run.call_args.kwargs["timeout"], inventory.GPU_TIMEOUT_SECONDS)

            rendered = json.dumps(payload)
            self.assertNotIn(str(home), rendered)
            self.assertNotIn(str(vault), rendered)
            self.assertNotIn("/private/bin", rendered)
            self.assertNotIn(secret, rendered)
            for forbidden in ("hostname", "ip_address", "serial", "environment", "ssh"):
                self.assertNotIn(forbidden, rendered.lower())

    def test_missing_values_are_unknown_instead_of_zero_or_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "missing-home"
            with (
                mock.patch.object(inventory.platform, "system", return_value=""),
                mock.patch.object(inventory.platform, "machine", return_value=""),
                mock.patch.object(inventory, "available_ram_bytes", return_value=None),
                mock.patch.object(inventory.shutil, "disk_usage", side_effect=OSError("not available")),
                mock.patch.object(inventory.shutil, "which", return_value=None),
            ):
                payload = inventory.collect_inventory(home)

            self.assertEqual(payload["system"]["os"], "unknown")
            self.assertEqual(payload["system"]["cpu_architecture"], "unknown")
            self.assertEqual(payload["system"]["ram_available_bytes"], "unknown")
            self.assertEqual(payload["system"]["disk_free_bytes"], "unknown")
            self.assertEqual(payload["gpu"]["status"], "unknown")
            self.assertIsNone(payload["gpu"]["devices"])
            self.assertEqual(payload["skills"]["agents"]["status"], "unknown")
            self.assertIsNone(payload["skills"]["agents"]["names"])
            self.assertEqual(payload["vault"]["status"], "not_requested")
            self.assertIsNone(payload["vault"]["obsidian_plugin_names"])

    def test_gpu_timeout_returns_unknown_without_exposing_error_details(self) -> None:
        with (
            mock.patch.object(inventory.shutil, "which", return_value="/private/nvidia-smi"),
            mock.patch.object(
                inventory.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd="private command", timeout=3, stderr="secret"),
            ),
        ):
            payload = inventory.gpu_inventory()

        self.assertEqual(
            payload,
            {"status": "unknown", "reason": "query_timed_out", "devices": None},
        )
        self.assertNotIn("private", json.dumps(payload))
        self.assertNotIn("secret", json.dumps(payload))

    def test_vault_is_never_discovered_without_explicit_argument(self) -> None:
        with mock.patch.object(inventory, "bounded_directory_names") as list_names:
            payload = inventory.vault_inventory(None)

        self.assertEqual(
            payload,
            {"status": "not_requested", "obsidian_plugin_names": None},
        )
        list_names.assert_not_called()

    def test_main_prints_json_to_stdout_and_has_no_output_option(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            expected = {
                "schema_version": 1,
                "privacy": {"read_only": True},
            }
            stream = io.StringIO()
            with (
                mock.patch.object(inventory, "collect_inventory", return_value=expected) as collect,
                redirect_stdout(stream),
            ):
                result = inventory.main(["--home", str(home)])

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stream.getvalue()), expected)
        collect.assert_called_once_with(home, None)
        option_strings = {
            option
            for action in inventory.build_parser()._actions
            for option in action.option_strings
        }
        self.assertNotIn("--output", option_strings)


if __name__ == "__main__":
    unittest.main()

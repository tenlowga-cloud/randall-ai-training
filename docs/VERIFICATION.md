# Verification and supported scope

This package's automated tests use temporary homes and synthetic packets. They must not install into the maintainer's real Codex/Claude configuration, call paid models, SSH to another machine, or read real network configuration.

Run:
```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

Tests cover the installer, hook protocol, bounded inventory and Claude task planning. Installation fixtures prove files and preservation behavior. They do not prove Randall's actual app discovers the skills, trusts a hook, selects the requested model, or accesses his GPU server.

## First-use proof on Randall's system

1. Installation plan names exact paths and conflicts.
2. Apply preserves unrelated settings and adds one shared skill source.
3. Doctor verifies current links and managed artifacts.
4. Fresh Codex and Claude sessions discover the skills separately.
5. Normal trust flow enables the hook; two real prompts create new metadata receipts.
6. A harmless task follows silent improvement and the supplied example without exposing internal reasoning.
7. A native Sol task supplies actual runtime/model evidence and a usable result.
8. Claude CLI completes an approved synthetic packet with a result and usable artifact.
9. Inventory correctly distinguishes laptop from server and missing from unavailable information.
10. An approved work sample produces a sourced observation, then a confirmed working rule.
11. The Obsidian owner is readable from a fresh task; a captured correction changes behavior.
12. A disposable file restores without keys available only on the lost server.

If any gate fails, record the specific failure and continue independent work. Never replace a trust block with bypass flags or a missing model with an unreported substitute.

## Platform matrix

- Linux/macOS/WSL: intended POSIX installation path; verify Python 3.11+, symlinks and actual app versions.
- Native Windows: not automatically configured by this release. Use WSL for CLI tools, or have the agent build and test an explicit Windows-native adapter after inspecting app discovery paths and symlink policy.
- Claude/ChatGPT web: portable instructions can be supplied through supported features; local hooks and filesystem access do not follow automatically.
- Separate GPU host: requires its own approved access and local installation where needed.

See the repository Actions results for package-test evidence. Actual Randall-device tests remain pending until his setup session performs them.


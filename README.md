# Randall's AI workbench

A private starter kit for a network engineer who wants Codex, Claude, Obsidian, and a GPU server to work together.

**Give this repository link to your local Codex or Claude Code agent and say:**

> Install this repository for me. Read `BOOTSTRAP.md` and follow its three stages. I am Randall. Preserve my existing setup, install the shared skills first, then give me the exact fresh-chat instruction before starting discovery.

Repository: https://github.com/tenlowga-cloud/randall-ai-training

Accept the GitHub invitation first. A private link will appear missing to an account without access. A plain web chat may not have filesystem or terminal access; use a local coding agent for installation. Do not paste a GitHub token into chat.

Your agent should clone this repo into a permanent user-owned project folder before installing. If anything stops, follow [recovery](docs/RECOVERY.md); preserve the completed stages.

## What happens

1. **Install.** Your agent reads the package and previews the installer, checks conflicts, then installs shared skill links, persistent instructions, a small prompt hook, and private starter notes. Existing configuration is preserved.
2. **Open a fresh chat.** The agent gives you a ready-to-paste message. Review/trust the new hook in the app if requested, then verify the skills and a real prompt receipt. Installation is not execution proof.
3. **Make it yours.** Astra supervises bounded Sol 5.6 agents and uses Claude CLI for suitable independent work. They ask what you need while inspecting approved hardware, tools, files, and examples. They build your evolving working agreement and a tested plan for your knowledge base and local AI.

No hardware, employer access, model entitlement, voice preference, or cloud-data permission is assumed.

## Included

- Portable **prompt-improver-silent, prompt-improver, wrap, simple-talk, ghost-mode, project-cleanup, and planning-mode** skills.
- A [network-engineering procedure](docs/NETWORK-WORKFLOW.md) for source-backed config review, lab validation, change plans, and rollback.
- A shared skill source linked to current Codex and Claude Code discovery locations.
- A standard-library Python installer with preview, conflict checks, backups, doctor, and conservative uninstall.
- Read-only inventory and a bounded Claude CLI bridge.
- A [complete training guide](docs/TRAINING.md), [setup protocol](BOOTSTRAP.md), [model selection guide](docs/MODELS.md), [integration guide](docs/INTEGRATIONS.md), and [verification](docs/VERIFICATION.md).

## Requirements

Python 3.11+, a supported local coding-agent installation, and permission to read/write your user-level agent configuration. The first release targets Linux, macOS, and WSL. Use WSL for the shared POSIX installation on Windows; Windows-native app paths and cross-host links require separate configuration and verification. A WSL link does not install a Windows-native app's skills.

The installer does not buy subscriptions, authenticate on your behalf, install system packages, change your network, start model training, or ingest personal history. Those choices happen with you in Stage 3.

## Manual commands, if needed

Run from the retained repository checkout:

```sh
python3 scripts/install.py plan
python3 scripts/install.py apply
python3 scripts/install.py doctor
```

Read the plan before apply. If the installer reports a name conflict, your AI should compare the existing skill and offer a merge or a separate name; it must not delete your existing skill to make installation pass.

Keep this checkout at its installed location. Moving or deleting it breaks skill links. Updates are reviewed changes, not an automatic pull on every prompt. The agent must run doctor after an update and recheck hook trust if its definition changed.

## Your files stay yours

The repository contains the reusable kit. Your profile, hardware reports, source approvals, lessons, and work live outside it in the private personal area created by the installer, then in your chosen Obsidian vault. The installer writes a local pointer identifying that owner. Never push the personal area into this repository.

See [BOOTSTRAP.md](BOOTSTRAP.md) for the complete starting instructions and [docs/VERIFICATION.md](docs/VERIFICATION.md) for the difference between package tests and proof on your machine.

# Randall: complete setup protocol

This file is for the agent Randall asks to install this repository. Follow the stages in order. The goal is a useful, personal AI workflow, not maximal plugin installation.

## Stage 1 — read and install

1. Confirm you are in a local coding agent with filesystem/shell tools. Identify OS, Python version, current app, and the retained clone's absolute path. Clone into a permanent user-owned project folder if this is only a link; avoid temporary folders and Downloads. If Git or Python 3.11+ is absent, use the OS's supported installation route before running scripts. If the repository is private and unavailable, explain invitation acceptance and normal GitHub authentication; never request a token in chat. Follow docs/RECOVERY.md for partial setup.
2. Read README.md, runtime.md, scripts/install.py and scripts/prompt_gate.py before execution. Read the seven core SKILL.md entry points, plus network-engineering if present. Do not import configuration from the author's computer.
3. Run `python3 scripts/install.py plan`. Explain actual affected paths in one concise paragraph. Randall's request to install authorizes the package's reviewed user-level adapter/link changes; continue to apply when conflict-free. Refuse to overwrite colliding skills, malformed settings, or unknown managed blocks. Compare conflicts and ask Randall only for the material resolution.
4. Run `python3 scripts/install.py apply`, then `doctor`. The single source is this retained checkout's skills directory. Both Codex and Claude adapters are prepared as requested, even if one app is absent; preparation does not install or connect that app. Private personal templates are separate from this repo. Keep unrelated settings, hooks, instructions and skills unchanged.
5. Do not modify global model/provider/sandbox defaults to fake compatibility. If the installed app does not support current hook/skill locations, record the version, check official documentation, and adapt only the relevant user-authorized mechanism. Never turn off existing security checks.
6. Record the actual installation result. Doctor is structural proof only. Current Codex requires review/trust of non-managed hook definitions through its normal UI such as `/hooks`; do not bypass trust. Claude may require accepting changed settings or restarting. A blocked hook remains unverified.
7. Record the OS/runtime surface and actual executable locations. On WSL, confirm the next agent runs inside the same WSL distribution; if Randall intends a Windows-native app, resolve that separate adapter before calling it installed for that app. Give Randall the exact fresh-chat message below with the clone and personal paths resolved to real paths and the precise app/environment to open. **Stop here and tell him to open a new chat in that project.** No deep history scan or hardware tuning in this old session.

### Fresh-chat message to give Randall

> Continue Stage 2 and Stage 3 of BOOTSTRAP.md in my installed Randall AI training repository at [resolve the actual clone path]. Read my LOCAL-STATE.md pointer at [resolve the actual personal-state path]. Verify the skills and prompt hook in this new chat, then use Astra to supervise bounded GPT-5.6 Sol builders and Claude CLI where useful. Ask me the material setup questions as you work. Begin with my real goals, approved sources, available tools, and hardware. Preserve my current setup.

Substitute the bracketed directions before giving the message. Do not leave Randall guessing a path.

## Stage 2 — verify the fresh session

- Read the local installation receipt and pointer. Confirm symlinks resolve to the same canonical skill files; inspect available skill discovery in each installed app. Avoid duplicate skill names in legacy locations.
- Verify a new prompt-hook receipt with this session/time, then ask a harmless task that requires preserving an example and an unknown. Confirm the answer follows the silent prompt-improver behavior without exposing its internal rewrite. Check a second prompt and a model switch if available. Do not claim every-prompt coverage based solely on running the hook manually.
- Confirm actual selected Astra and supported `gpt-5.6-sol` worker availability. If starting from Claude, finish installation there, then explain how to open Codex/Astra for supervision if available. Never impersonate a different model.
- Use a harmless native Sol task with one output file outside the shared package. Capture requested/resolved model metadata if exposed and verify its result. Instructions can request routing; only the host selects models. If a model or native agent tool is unavailable, keep independent discovery moving and present the supported alternative for Randall to choose.
- Read current CLI help and docs before setting agent config. Do not edit configuration using guessed keys. Do not start large paid calls merely as installation checks.
- Record status for each installed surface separately: files installed, skill discovered, hook trusted/enabled, hook executed, behavior tested, model route verified. Absent Claude is an install question, not a reason to claim it is linked.

## Stage 3 — learn Randall and build the useful system

### A. Ask while inspecting

Ask at most three closely related questions in a round and continue independent authorized work while waiting. Do not ask for hardware values a read-only command can obtain.

First round:
1. Which two recurring network-engineering tasks would you most like help with, and what wastes the most time today?
2. Is this personal home-lab work, employer/client work, or both? Which material may each cloud provider receive?
3. Which computer runs Codex/Claude, where is the GPU server, and do you already use Obsidian?

As evidence develops, ask about vendor platforms/versions, configuration automation, source-of-truth tools, on-call expectations, budget, acceptable latency, remote/mobile needs, and preferred explanations. Ask Randall to identify two or three approved examples of past work; do not scan every chat, employer share, home directory, or configuration backup by default.

Record source scope before reading. Approved examples might be a sanitized change request, a lab runbook, an Ansible role, or a troubleshooting explanation. Extract working preferences and reusable lessons; retain originals in their proper systems. Do not infer personality or permission from a job title.

### B. Inventory before buying or installing

Run `scripts/inventory.py` only in the approved environment. It reports bounded local metadata; it does not SSH automatically, scan networks, or read secrets. Use an explicit vault path only after Randall selects it. Save reports outside this repository.

Map plugins/skills/CLIs as: detected, configured, authenticated, task-tested, needed, deferred, or unavailable. Installed names do not prove login or permissions. Ask permission for required official package installation and account authentication, then verify the actual tool with a harmless read. Use docs/INTEGRATIONS.md for the decision framework.

If the server is separate, prepare a precise read-only inventory command for its supported OS and use an existing authorized connection. Do not change GPU drivers, hypervisor, ports, SMB, or VLANs during discovery.

### C. Build “How to Work With Randall”

Use the private template as the initial owner. Seed only known facts. Capture goals, expertise, current projects, communication examples, decision boundaries, source permissions, model routes, and accepted success criteria. Label hypotheses as proposals. Randall's explicit correction can update the owner immediately; a broad new preference inferred from examples needs his confirmation.

Keep a dated observation with source ID/path and the concrete behavior it changed. If nothing durable changed, do not manufacture a lesson. Do not silently raise authority or relax privacy as the AI “learns.” See docs/LEARNING.md.

### D. Select files and Obsidian architecture

Preserve any existing vault and naming convention that works. Identify accepted notes, raw sources, code, backups, derived indexes, and private state. Treat tags as grouping and links as relationships. Use the training guide's server/replica choices; ask whether Randall permits local copies.

Propose one owner and one sync system. If separately protected accepted knowledge is required, use editing/proposal staging and reviewed promotion with hash checks. Show a scoped migration manifest and recoverable plan before moving real files. No whole-drive cleanup.

Create the AI setup project and pointers in the selected vault, reconcile staged private notes, and update the local pointer. If absent, scaffold in the private personal area as staging and mark pending-vault status. Do not duplicate live truth. Code stays in its repo; all durable decisions, sources, work state and proof are reachable from the vault.

### E. Coordinate real useful work

Astra owns integration. Delegate one independent task to Sol, and one suitable task to Claude only when it improves this milestone. Examples: Sol builds a local inventory parser and tests it; Claude turns approved network design facts into a runbook and identifies missing validation cases. Give each separate files and source packets.

For Claude CLI, inspect installation/auth status without printing credentials. If absent, use current official installation instructions after Randall authorizes it. Authentication is completed in his normal login flow. Follow docs/INTEGRATIONS.md and the bridge preview before a cloud call. Use explicit permission mode and bounded tool availability. Do not use bypass flags, assume that subscriptions share quotas, or allow recursive orchestrator calls.

### F. Recommend local models from evidence

Use docs/MODELS.md. Record actual GPU model/VRAM per device, system memory, usable storage, drivers, runtime, interconnect, concurrency, context needs, modalities, and power/latency constraints. Search current official model cards and runtime compatibility. Present a primary choice, a smaller fallback, and why each fits Randall's tasks. Include download size, license/use limits, estimates versus measurements, and cloud/local route.

Get approval for model downloads and actual compute budget, benchmark on synthetic tasks, then choose from measured quality/latency/resource use. Never say a large model fits just because raw weights fit VRAM. Start with retrieval and examples; weight training is a later separately justified experiment.

### G. Prove the whole loop

Choose one network-engineering workflow Randall values. Use synthetic or explicitly approved material. Build a usable artifact, validate it, capture a correction, retrieve it in a fresh task, and demonstrate a restore of a disposable note. Show the next action without making Randall retype the context.

Finish with a plain dashboard of known facts, working routes, failed/unverified tests, approved next steps, and remaining questions. Keep it in his vault. Use up to three meaningful repair passes; a staged plan is never “system optimized.” Stop at real access/budget gates while completing independent work.

## Ongoing behavior

Future prompts invoke silent improvement through supported hooks and instructions. Future material work uses the shared skills and the current personal owner. Start small, capture while working, verify fresh retrieval, measure cost per accepted result, and update narrow skills from repeated evidence. No background monitoring, bulk history capture, or auto-training is installed by this kit.

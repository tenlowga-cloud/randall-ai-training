# If setup stops

Ask your agent to diagnose the named stage and continue from there. You should not have to start over or delete existing settings.

| Symptom | Next action |
|---|---|
| GitHub says 404 | Accept the invitation using the invited account. Verify that account can open the private repo, then authenticate the local Git client normally. |
| The agent cannot clone or run commands | Open a local Codex project or Claude Code session. Web chat alone cannot install into your machine. |
| Git or Python is missing | Have the agent identify your OS and offer the official supported installation route. Install Python 3.11+ before running the installer. On Windows, choose the actual Windows or WSL agent surface first. |
| A skill name already exists | Compare the two versions. Preserve yours; select a reviewed merge or rename. Do not force-install. |
| Settings JSON is invalid | Save a backup, identify the syntax error and repair that error. Do not replace the entire file with the kit's defaults. |
| Hook is configured but never runs | Open a fresh session, check the app version, hook enablement and normal trust UI. Managed policy may block it. Use explicit runtime instructions while marking automatic coverage unverified. |
| Astra or Sol is missing | Report actual available models and propose a substitute. Continue independent setup without claiming the requested routing works. |
| Claude is missing or signed out | Follow official Claude Code installation/login. Keep other setup moving. Never paste credentials into chat. |
| Server is offline | Keep approved notes in private staging, mark pending-vault and continue local learning. Reconcile by a reviewed manifest when the server returns. |
| Installed folder was moved | Restore it to the recorded location first. Use the original installer to uninstall managed adapters, retain personal state, then review installation from the new permanent path. Never delete personal notes to repair links. |
| Installation was interrupted | Inspect the installer receipt and the transaction journal under the private state's backups directory. A normal exception rolls back; a killed process or power loss may leave partial state. Compare the journal with current files, restore only unchanged task-owned changes, then rerun plan. Do not force-overwrite orphaned links. |

Keep the repository in a stable, user-owned folder, not Downloads or a temporary directory. Clone it before installation; opening a GitHub webpage does not create local files. Symlinks depend on this retained folder.

To remove the package's adapters, first preview your current installation with `python3 scripts/install.py doctor`, then run `python3 scripts/install.py uninstall`. Personal notes and their pointer must remain. Keep them until their knowledge is safely reconciled with the vault.

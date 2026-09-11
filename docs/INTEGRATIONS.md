# Tools, plugins, and the Claude bridge

## Discover first

Use the package inventory plus the installed app's own tool lists. A filename means detected, not authenticated or operational. Keep configured, connected, task-tested, needed, and deferred separate. Don't print raw settings, environment variables, API keys, authentication databases or secret-bearing endpoints.

| Need | Initial route | Add only if |
|---|---|---|
| File knowledge | Obsidian core + exact file search | Semantic retrieval demonstrably helps |
| Current vendor documentation | Existing web search + official vendor pages | Firecrawl extraction adds value to repeated research |
| OpenAI configuration | [Official Docs MCP](https://developers.openai.com/learn/docs-mcp) or official pages | A connector is useful and supported on the installed surface |
| Code/version history | Existing Git/CLI | Remote GitHub access is needed and scoped |
| Network source of truth | Existing NetBox/Nautobot/system, if Randall uses one | Read access is explicitly authorized and tested |
| Network automation | Existing Ansible/Nornir/Netmiko workflow, if present | Exact vendor/module/version fit and lab tests pass |
| Local inference | One selected runtime | Hardware and task benchmark justify it |
| Local chat UI | Optional Open WebUI | It simplifies Randall's actual workflow |

This is a decision table, not a list of plugins known to be installed. Do not assume a community MCP server with a familiar name is maintained, official, or trustworthy. Inspect publisher/source, license, version, permissions, network destinations and uninstall path. Prefer built-in APIs/CLIs. Treat plugins as code with the host user's access; prompts are not sandboxes.

## Link Claude through its CLI

Use an installed official Claude Code CLI. Inspect `claude --version`, `claude --help`, and `claude auth status` only when relevant; summarize auth status without credentials/account details. If absent, fetch [official setup instructions](https://code.claude.com/docs/en/setup), get Randall's scoped install approval, and verify the result. Randall handles normal login; never ask him to paste a key.

The packaged `scripts/claude_bridge.py` previews a bounded task and invokes Claude only with `--execute`. The task packet must be public or explicitly cloud-approved and the approved workspace must exist. It supports no-tool review and file-only authoring; no shell/network/device tools or recursive Agent tool are exposed by the bridge.

Use `dontAsk` for the no-tool review path and `acceptEdits` for explicitly approved file-only authoring. Retain existing user-level safety settings. This is a scoped tool contract, not an OS sandbox: use a dedicated account/container for strict isolation. Inspect user hooks/plugins before invoking, since they may run outside the model tool allowlist. No unreviewed project hook/MCP configuration should enter a headless call.

Preview:
```sh
python3 scripts/claude_bridge.py --packet /absolute/private/task.json
```

Execute only after the packet's data route, tools, workspace and budget are approved:
```sh
python3 scripts/claude_bridge.py --packet /absolute/private/task.json --execute
```

The packet shape is in `examples/claude-task.json`. Replace its workspace with a real isolated path and choose an available Claude model after live verification. Review the brief, record cloud/customization approval, and set the approved `max_budget_usd`; the example amount is not authorization. Verify the installed CLI supports the flags before execution. Runtime budget controls and subscription limits are different; record actual usage when exposed. Results are printed for the supervising agent to save in the private evidence owner. Do not upload them to this starter repo. Review a nonzero/is_error result as failure; success still needs artifact verification. Requested model and model-use metadata are separate fields.

Claude should return bounded work to Astra; it must not launch Codex or recursively build a new team. For executable work needing shell tests, the supervising Sol worker can run the relevant authorized tests against the returned candidate. Add broader execution only through a separately reviewed task route.

## Hooks and platform limits

[Codex hooks](https://learn.chatgpt.com/docs/hooks) and [Claude hooks](https://code.claude.com/docs/en/hooks) provide UserPromptSubmit. Our hook adds compact silent-rewrite instructions and records metadata; it does not call another model or store raw prompts.

Codex non-managed hooks require normal trust review; configurations can be disabled or overridden by managed policy. Desktop/cloud/chat surfaces differ. Plain ChatGPT or Claude web does not inherit local symlinks or CLI hooks. Use supported project instructions/skill uploads there and explicitly mark that per-prompt local-hook enforcement does not apply.

Codex currently documents `~/.agents/skills` and symlink discovery; Claude Code uses `~/.claude/skills`. The package uses one skill source. A separate machine needs its own local installation; symlinks do not cross machines. Never duplicate the same skill into multiple scanned locations just to make it appear.

Sources checked 2026-09-11: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Claude headless](https://code.claude.com/docs/en/headless), [CLI flags](https://code.claude.com/docs/en/cli-reference), [Claude memory](https://code.claude.com/docs/en/memory). Recheck actual installed-version behavior before adaptation.

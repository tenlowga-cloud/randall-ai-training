# Recipient walkthrough and repairs

Reviewed 2026-09-11 from a fresh recipient's perspective. This is package review, not a claim of installation on Randall's machine.

| Failure discovered | Resolution |
|---|---|
| Personal edits/migration treated as installer damage | Personal state is retained and may evolve independently of the kit. |
| Uninstall could remove learning records | Personal records and owner pointer survive removal of adapters. |
| Templates hidden by ignore rules | Packaged templates explicitly remain tracked. |
| Missing Python, inaccessible private repo, wrong app surface | Entry protocol now checks prerequisites, account access and runtime environment before setup. Recovery instructions name the next action. |
| Two environments mistaken for one installation | WSL and Windows-native consumers are explicitly separate; fresh-chat handoff names the actual environment. |
| Private notes inherit public-readable file modes | New private state directories use 0700 and seeded personal files use 0600. |
| One prompt receipt overwrites the previous proof | The hook retains the last two bounded metadata observations without storing prompts. |
| A crash journal could overwrite later edits | Interrupted setup stops for scoped recovery; normal in-process failures still roll back. |
| Prepared files mistaken for a connected AI | Per-surface discovery, trust, real hook execution and actual model routing are separate proof states. |
| Live links make updates immediate | Keep a stable installation folder; review changes elsewhere before updating it. Doctor and normal hook trust are rechecked. No automatic updater. |
| Missing or inaccessible server blocks all value | Private staging supports useful tasks while approved server access is resolved, followed by one-owner reconciliation. |
| Network workflow promised but hard to find | README links the dedicated network workflow and its synthetic first exercise. |
| Claude call expands into another orchestrator | Packet uses a bounded model/tools/turns/budget contract and requires approved context. No recursive Agent or shell tools. |

The first CI run passed on Linux and exposed macOS path-alias assumptions in two installer tests. Those failures are part of the repair work; consult the current CI result rather than treating an earlier run as release proof.

Remaining real-machine checks: account access, actual app versions, hook trust and execution, available model routes, Claude authentication, WSL if used, server access, GPU benchmarks, vault synchronization and restore. The bootstrap performs these with Randall. They cannot be proven from a repository on someone else's computer.

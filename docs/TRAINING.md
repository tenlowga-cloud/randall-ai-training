---
type: reference
status: active
authority: project-only
verified: 2026-09-11
tags: [ai, home-lab, learning, obsidian]
---

# Randall: build an AI system that remembers your work

A practical starter guide for a network engineer using Claude, ChatGPT, Codex, Obsidian, and a home GPU server.

Prepared September 11, 2026. This is a standalone, shareable design and onboarding brief. It contains no private source-library dependencies. Nothing described here is already installed on your server. Product documentation was checked on the preparation date; your AI must verify versions, model access, hardware, and supported configuration before setup.

## Start here

You do not need to become an AI researcher before this becomes useful. Start with a system that can find your approved network documentation, explain its sources, help build a tested change, and remember a correction in the next session.

Use Astra as the architect and supervisor. Use GPT-5.6 Sol as the main builder, as requested. Give local AI a small, measurable first job: answer questions about your own home-lab runbooks with accurate file citations. Expand after this works.

**To begin:** follow [BOOTSTRAP.md](../BOOTSTRAP.md). Its install → fresh chat → discovery sequence is the authoritative entry point for this repository.

Your GPU server will host open-weight models supported by its hardware. This guide does not assume Astra or Sol weights can be downloaded and run there. Cloud models and local models are separate routes.

## 1. The six parts of the system

| Part | Plain meaning | Your implementation |
|---|---|---|
| Model | The engine doing reasoning and generation | Astra, Sol, Claude, or a locally hosted model |
| Agent runtime | Runs the model's tool calls, tasks, and checks | Begin with Codex; Claude Code is an alternate working surface |
| Knowledge | Files containing what you know and why | A server-owned Markdown knowledge base |
| Retrieval | Finds the relevant parts of those files | Exact text search first; local semantic retrieval when needed |
| Tools | Read files, test code, inspect approved systems | Scoped filesystem, shell, Git, browser, later selected connectors |
| Skills | Repeatable instructions for a kind of job | A small set of procedures built from this guide |

A plugin bundles capabilities. An MCP server exposes tools through a common interface. Neither guarantees that a task is correct or makes the model permanently learn your files.

Think like an engineer: separate the control plane, data plane, access boundary, and observability. Then prove a useful transaction through the whole system.

## 2. A small architecture that can grow

```text
You: intent, decisions, authorization
                 |
        Codex / Astra supervisor
        brief, route, accept, explain
                 |
        Sol builder, one write owner
        implement, test, repair
                 |
        isolated workspace -> reviewed change
                 |
        server accepted knowledge and projects
          |             |               |
    Obsidian view   local retrieval   versioned backup
                         |
                  local model endpoint
```

That diagram describes coordination, not a blanket data flow. Cloud agents receive only approved material. Local-only knowledge uses a separate local model path whose private content is never passed to Astra or Sol. A cloud supervisor may receive a sanitized completion status if you approve it.

Start with the native Codex delegation tools. Do not build a custom agent framework merely to route one builder. If the installed runtime cannot select the worker model, record that limit and prepare a supported configuration or manual builder handoff. Never label an Astra run “Sol” to make the plan look complete.

## 3. Where files should live

The paths below are proposed Linux paths, not commands to run blindly. On a NAS or hypervisor, use an approved VM/container and the platform's supported storage mounts. Preserve its existing operating system and workloads.

```text
/srv/ai/
  knowledge/                  Accepted, curated Markdown vault
    START-HERE.md
    How-We-Work.md
    Projects/
      Home-Lab-AI/
        PROJECT.md
        DECISIONS.md
        HANDOFF.md
        EVIDENCE.md
    Systems/
    Runbooks/
    Lessons/
    Templates/
    Inbox/
  editing/                    Sync landing area for human Obsidian edits
  workspaces/                 One task-owned workspace per writer
  proposals/                  Candidate note changes awaiting integration
  sources/                    Approved raw documents, separate access rules
  indexes/                    Rebuildable retrieval databases
  models/                     Model and embedding files
  services/                   Versioned nonsecret service definitions
  logs/                       Scoped operational receipts with retention
```

Backups need a separate destination; a `/srv/ai/backups` folder on the same failed disk is insufficient. Secrets live in your chosen credential store, outside the vault and repositories. Avoid storing model downloads, vector databases, raw chat archives, or secrets inside Obsidian.

| Item | Why it goes there |
|---|---|
| `START-HERE.md` | A short map that identifies current owners and what to read first |
| `How-We-Work.md` | The single owner of shared collaboration rules |
| `PROJECT.md` | Outcome, scope, acceptance, owner, links, and current milestone |
| `DECISIONS.md` | Decision, reason, source, rejected alternatives, revisit condition |
| `HANDOFF.md` | Current moving state and the next action; keep it short |
| `EVIDENCE.md` | Tests, observed results, failures, versions, and exact delivery state |
| `Systems/` and `Runbooks/` | Accepted configuration explanations and recovery procedures |
| `Lessons/` | Reusable corrections with sources and prevention checks |
| `Inbox/` | Temporary unclassified material with an owner and review action |
| `sources/` | Original approved material; preserve its identity rather than rewriting it |
| `indexes/` | Search acceleration; the files remain authoritative |

Keep source code in its own project repository. Link the repo from the knowledge base. Use Git for reviewed checkpoints and transport. Local files are saved even before a commit; sync and backup are separate obligations.

## 4. Obsidian with the server as the source

Obsidian is an editor over files. The server can own the durable files without running the desktop GUI. Desktop clients still need a file-access strategy. Obsidian's documented local/remote vault model distinguishes a device's vault from a Sync remote. [Obsidian vault types](https://obsidian.md/help/sync/vault-types).

### Recommended starter: one active human editor, server copy, one sync tool

Use a local Obsidian working copy on your computer with a single sync mechanism connecting it to the server's `editing/` area. Keep server-side snapshots and backups. Enable only one human editing device initially. AI reads accepted server material from `knowledge/` and writes candidate changes into `proposals/` or an isolated project workspace. The sync account cannot write `knowledge/`.

“Server-owned” means the server retains protected accepted state, access controls, and recovery history. Human edits sync into a staging area and become accepted through promotion. A two-way sync tool is still a replica system, not a central transaction lock. It cannot decide which conflicting edit is correct.

The integration rule applies to human and AI edits: confirm sync is caught up, pause editing of affected files, compare their accepted hashes to the proposal's starting hashes, and inspect the diff. One integrator promotes an approved batch atomically where supported, records its revision/manifest, and updates the editing copy from that accepted revision. If a starting hash changed, create a merge task; do not overwrite it. A client deletion is a proposed deletion, never automatic accepted-state removal. Preserve prior accepted revisions in protected history. Resume editing after sync converges. Begin with an agent-assisted batch; automate promotion only after the conflict and deletion tests pass.

This adds a deliberate “accept edits” step. If you prefer immediate two-way editing later, simplify to a canonical synced replica with protected recovery history and describe it honestly; it will no longer be a separately protected accepted-state store.

### Choose one of these paths

| Path | When it fits | Tradeoff |
|---|---|---|
| Syncthing between supported desktop/server platforms | Self-hosted file replication is the priority | You own device setup, conflicts, versioning, and monitoring; verify mobile client support separately |
| Obsidian Sync with a supported headless server client | Convenient supported device sync is more important than keeping the sync service entirely self-hosted | A separate service/subscription and vendor-hosted remote; check account and current headless requirements |
| Direct SMB/NFS-mounted vault | One always-connected LAN desktop and no offline requirement | Depends on network and filesystem behavior; test interruption, permissions, file watching, and recovery |
| Server-hosted desktop accessed remotely | Absolutely no vault working copy should remain on the client computer | More desktop administration and requires connectivity |

For an initial desktop/Linux setup, I would evaluate Syncthing first, subject to the actual client operating systems. If phone support is central, evaluate Obsidian Sync before choosing. Do not run both on the same vault. Headless Sync is a documented option, not proof of compatibility with your server. [Obsidian Headless Sync](https://obsidian.md/help/sync/headless).

Syncthing can preserve conflict copies; its versioning is not a backup of every local edit. Configure versioning deliberately and test it. Keep `.git`, caches, credentials, and device-specific workspace state out of live file replication. Share only reviewed plugin settings if needed. [Synchronization](https://docs.syncthing.net/users/syncing.html) and [file versioning](https://docs.syncthing.net/users/versioning.html).

### Acceptance before real notes

Use disposable notes. Edit offline and reconnect. Edit the same note on two clients and preserve both versions. Interrupt the server and recover. Rename a note and verify its links. Delete and corrupt a note, then restore both from a dated backup. Verify convergence by contents or hashes, not just a green icon.

If you require strict server-only storage, choose the direct mount or remote desktop path intentionally; the replica recommendation does keep a local working copy.

## 5. What to install, and what to postpone

You need a small working stack, not a shopping list of every AI plugin. The entries below are recommendations to verify and implement in stages; no automatic purchase is implied.

| Priority | Component | Source / installation route | Why and proof |
|---|---|---|---|
| First | Codex with your existing account | Official Codex distribution and installed model picker | Astra plans; one Sol worker completes a harmless file task |
| First | Obsidian | [Official download](https://obsidian.md/download) | Open, edit, link, search, and recover plain Markdown |
| First | Git and existing SSH tools | Supported OS packages | Review a diff; connect as a restricted user; recover a named checkpoint |
| First | One sync system | The selected path above | Server/client convergence and visible conflict recovery |
| First | Versioned encrypted backup | Existing server backup facility or [restic](https://restic.readthedocs.io/en/stable/) as a candidate | Restore to another folder/device; record what is excluded |
| Next | Ollama as the initial local runtime | [Official documentation](https://docs.ollama.com/) | Run one supported model locally and measure actual memory/latency |
| Optional | Open WebUI | [Official documentation](https://docs.openwebui.com/) | A convenient local chat interface if terminal access is insufficient |
| Next | Read-only knowledge search | Existing shell search, then a small local retrieval service | Correct file citations, freshness, access filtering, and “not found” behavior |
| When needed | Claude Code | [Official documentation](https://code.claude.com/docs/en/overview) | Alternate builder or a bounded independent review using the same approved files |
| When needed | Official documentation access | Built-in web search; [OpenAI Docs MCP](https://developers.openai.com/resources/docs-mcp) where useful | Fetch the current primary page before changing version-sensitive configuration |
| Later | GitHub integration | Native CLI or official connector, if you use GitHub | Access only selected repositories; local Git does not require GitHub |
| Later | Firecrawl | [Official documentation](https://docs.firecrawl.dev/) | Add when ordinary web research needs reliable multi-page extraction; check credits and data destinations |
| Later | vLLM | [Official parallelism documentation](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/) | Evaluate when measured concurrent inference needs justify another runtime |

The download/documentation links are vendor entry points. Not every package's current installer or your hardware compatibility was tested for this guide. The setup agent must fetch the matching version instructions before installing.

Start Obsidian with core Search, Backlinks, Templates, and Properties. No community plugin is required for the first workflow. Consider Dataview or Templater only after a specific repeated need appears; the starter does not depend on them. An “AI Obsidian” plugin is also optional when your agent already has scoped file access.

Treat added plugins as executable software. Assume a community Obsidian plugin can access what the app user can access, including files and network; do not depend on a granular permission prompt. Maintain an allowlist, record version/hash where available, review publisher/source and outbound behavior, and exclude unreviewed plugins from local-only vaults. Apply the same capability review to coding-agent plugins and MCP servers. Do not paste secrets into plugin settings exported with the vault. Keep a documented way to open and recover the vault with community plugins disabled.

### Create these four small skills from this guide

These are proposed custom skill names, not marketplace packages. Ask the setup agent to create them in the current app's supported skill location and prove that a new session discovers them. Each gets a `SKILL.md` with a name, description, trigger, steps, and acceptance check. [Codex skill format](https://learn.chatgpt.com/docs/build-skills).

| Skill | Trigger and procedure | Finished proof |
|---|---|---|
| `task-brief` | Before substantial work: outcome, source paths, owner, boundaries, acceptance, next action | Builder can start without reconstructing the conversation |
| `knowledge-capture` | A durable decision/correction occurs: find its owner, preserve source/date, write rationale, link evidence | Fresh session locates and uses the accepted record |
| `verify-and-recover` | A change is ready: test promised behavior, error path, and proportionate rollback | Saved evidence distinguishes actual outcome from attempted action |
| `resume-work` | A new session continues a project: read START-HERE, project and handoff, then relevant lesson | Correct next action without rereading raw history |

Do not begin with an automatic capture daemon. Make the manual/agent-assisted loop work before scheduling it. Add a schedule only when it has a defined owner, deduplication, failure behavior, budget, and stop control.

## 6. Make Astra supervise and Sol build

Requested routing:

| Role | Requested model | Responsibility | Context |
|---|---|---|---|
| Supervisor | `gpt-6-astra`, if available | Plan, resolve tradeoffs, set acceptance, integrate and report | Brief, key evidence, bounded worker receipts |
| Builder | `gpt-5.6-sol`, if available | Investigate assigned scope, implement, test, repair | Only the relevant source files and task packet |
| Local helper | Hardware-tested open-weight model | Private retrieval and a small set of evaluated tasks | Local authorized collection only |
| Optional reviewer | A separate capable session | Challenge one named risk or verify a consequential candidate | Frozen candidate and acceptance tests |

Model names and availability are account/runtime dependent. Native subagents can use model-specific configurations, but the exact supported setup must be checked on your installed version. Delegation can increase total tokens, so savings are a hypothesis to measure. [Official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

### Dispatch contract

```text
Goal: Produce the named usable result.
Owner: One builder; list writable files and workspace.
Sources: Exact approved paths/versions; no entire-vault dump.
Constraints: Existing interfaces, data class, permissions, exclusions.
Acceptance: Observable tests and required artifact.
Budget: Approved runtime/usage checkpoint; no silent spend expansion.
Return: Files, result, tests, limitations, next action, runtime model evidence.
```

Astra does not repeat all builder work. It checks the important evidence and sends back a precise defect when a check fails. The same builder repairs it. Begin with one builder and no recursive agent spawning. A second worker needs independent scope and nonoverlapping ownership.

Before claiming routing works, perform a harmless trial and inspect actual runtime/provider metadata or trusted task configuration. A model's self-description is not proof. Record the installed app version, requested/resolved model, effort if supported, task ID, and usage when exposed. If resolved identity is unavailable, label it unverified.

For a trivial job, measure whether the supervisory call is worth the overhead. For larger work, compact receipts and continued builder context are often more useful than frequent new agents. Set hard caps where the platform supports them; a budget sentence in Markdown is only a soft instruction. Subscription quotas, API charges, and local electricity are different costs.

## 7. Share knowledge across Claude, ChatGPT, and local AI

Keep common rules in `How-We-Work.md`. Use small app-specific adapters that point to that owner. Codex uses its supported `AGENTS.md` discovery; Claude Code uses `CLAUDE.md` and its supported imports/context mechanisms. Verify a fresh session actually reads the owner rather than assuming a filename is magic.

Claude Code also has auto memory. It is useful context, but it is machine-local and should not become the sole owner of facts another app needs. [Claude memory documentation](https://code.claude.com/docs/en/memory).

Plain ChatGPT or Claude web chat does not gain server filesystem access because a path appears in a prompt. Give it an approved export or a supported authenticated connector. Uploaded files are snapshots and need freshness labels. A network share reachable from your laptop is not automatically reachable from a vendor cloud session.

The same accepted knowledge can serve multiple models through approved access paths. Their private conversation states and built-in memories do not merge automatically. If a useful correction occurs in a web chat, capture its approved conclusion and source pointer in the owning project, then prove a different surface can retrieve it.

## 8. Local AI: inventory first, benchmark second

Have the agent inspect these without collecting credentials or unrelated personal files:

- Server OS/hypervisor, intended VM/container, and supported GPU passthrough.
- Exact GPU model/count, VRAM per GPU, driver/runtime compatibility, and interconnect.
- System RAM, CPU, free SSD space, storage pool limits, network path, and existing workloads.
- Power/thermal envelope, desired concurrent users, acceptable response time, and monthly budget.
- Whether text-only tasks suffice or you need image, audio, or code capabilities.

Do not infer that multiple GPUs form one seamless memory pool. Model/runtime support and interconnect matter. vLLM documents distinct parallelism strategies; choosing one needs hardware and workload evidence. [vLLM parallelism](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/).

As a rough illustration, 8 billion parameters at 4 bits use about 4 GB for raw weights alone; 32 billion use about 16 GB. These are arithmetic estimates, not deployment requirements. Quantization metadata, runtime buffers, KV cache, context length, and concurrent requests consume more memory. Leave headroom and measure the actual workload.

Begin with one modest supported instruction model and a smaller alternative, selected after inventory and license review. Record exact model ID/digest, license, quantization, context setting, runtime version, and measured performance. Do not choose the largest model merely because it loads. Try the same ten representative tasks and score usefulness, source accuracy, latency, memory, and failures.

Ollama is a reasonable first runtime to evaluate. Keep its endpoint private. Its documented default binds to localhost; it also has a documented local-only setting to disable its cloud features. Verify the resulting logs/configuration instead of assuming every model route is local. [Ollama FAQ](https://docs.ollama.com/faq).

Open WebUI is an optional interface, not the knowledge owner or a requirement for routing. Its documentation describes support for local/offline use and model backends. Validate authentication, storage, and the exact backend connection in your deployment. [Open WebUI](https://docs.openwebui.com/).

## 9. Teach the system in the right order

### First: good instructions and examples

Write a short working agreement and three good examples of finished work. Use synthetic network addresses and configurations. Define what the model must do when a fact is unknown or two sources conflict.

### Second: retrieval over approved files

Start with exact path/text search. Add semantic retrieval when users cannot remember the words used in the notes. RAG means the system retrieves relevant passages and gives them to the model for the current answer; it does not change model weights.

The retrieval service should return source path, heading, current version/hash, classification, and relevant text. Split by meaningful headings. Keep the embedding model and index version recorded. Apply access rules before retrieval and before returning content. Index updates must replace changed passages and remove deleted ones. A vector database is disposable and should rebuild from files.

For local-only material, keep parsing, embeddings, reranking, generation, and logging local. Sending private text to a cloud embedding service still sends private text out, even if final generation is local. Never silently fail over a restricted task to a cloud route.

### Third: corrections that affect the next task

```text
Lesson ID: LESSON-001
Source: task ID or approved source path; date/version
Owner: Home-Lab-AI
Mistake: A proposed service change was called installed.
Evidence: The live version was still the old one after restart.
Corrected rule: Read back the running version before reporting installation.
Applies when: Updating an actual service; not a draft-only specification.
Prevention test: Compare expected version to running version in the receipt.
Revisit when: The deployment mechanism changes.
```

Place a lesson in its project owner first. Promote it to a shared skill only when it is truly reusable. Test it in a fresh session with a new example; the AI should use the rule without being told the answer.

### Fourth: fine-tuning only for a demonstrated gap

Fine-tuning changes weights to improve stable behavior or repeated output patterns. Consider it only after you have approved examples, a held-out test set, an unresolved failure pattern, a compatible base model/license, a resource budget, and rollback.

Split training and evaluation data by source or task family to reduce leakage. Compare the tuned model against the same base model with good instructions and retrieval. Keep the original model available and test for regressions. Do not train on secrets, employer/customer data, or unreviewed conversation dumps.

Training a foundation model from scratch is a separate research project. It is not a prerequisite for a useful home server. A big VRAM budget does not make changing knowledge best stored in weights.

## 10. Security and recovery as practical engineering

Use a dedicated service account with access only to the intended directories. Run the first agents against synthetic fixtures and read-only real sources. Keep network/device configuration writes out of the starter workflow. When you later authorize them, require an exact candidate, validation, maintenance plan, and tested rollback.

Use your existing private access method, SSH tunnel, or an evaluated VPN. Do not publish SMB, an unauthenticated model endpoint, or an admin panel directly to the internet. A local service can still send data through connectors or tools; locality is a whole-path property.

Classify sources as public, internal/cloud-approved, local-only, or secret. Store route controls in a service-owned manifest that retrieved text cannot alter. For example: `source_id: LAB-001`, `owner: Home-Lab-AI`, `classification: local-only`, `allowed_routes: [local]`, `retention: owner-review`. Default unclassified material to local-only. Enforce this before reading into a cloud agent, retrieval, embeddings, tool output, logging, and fallback. Metadata alone is not enforcement. Credentials stay in the secret store; retrieval metadata and logs can also be sensitive. Retrieved documents are evidence, never instructions to ignore the operator or disclose other files.

Before real data enters a cloud route, verify the actual account's current data-use/training settings, retention, connector scope, and applicable organization rules against that provider's current documentation. Record the allowed use and source date in the local access inventory. This guide makes no blanket claim about provider retention or plan-specific privacy.

Back up accepted knowledge, approved source files, nonsecret service definitions, selected project work, and recovery instructions. Decide separately whether to retain raw conversations. Keep at least one protected copy away from the server and test restoration to a clean destination. Keep the restore credential in an owner-controlled recovery store independent of the server; prove a clean-device restore without a key available only on the failed machine. Record the backup's timestamp, covered paths, exclusions, and restore result. Sync, RAID, Git, and snapshots on the same machine each solve different problems.

## 11. Rollout by proof, not by calendar

| Stage | Deliverable | Go/no-go check |
|---|---|---|
| 0: discover | Hardware/access inventory and short architecture plan | Unknowns are named; no destructive assumptions |
| 1: organize | Small vault, working agreement, project and evidence files | New session finds owner and next action |
| 2: protect | One sync route and independent backup | Offline/conflict and delete/corruption restore tests pass |
| 3: delegate | Astra-supervised harmless Sol task | Actual worker model routing and file ownership are verified |
| 4: run locally | One local model on synthetic tasks | Memory, latency, locality, restart, and failure behavior recorded |
| 5: retrieve | Approved runbooks with cited answers | Freshness, deletion, unknown, and permission tests pass |
| 6: learn | One captured correction used in a fresh task | Behavior changes without repeating the answer |
| 7: expand | One useful repeated workflow | Measured time returned exceeds maintenance effort |

You can gain value from stages 1 and 3 before a GPU setup is complete. Hardware delays should not prevent learning how to brief, verify, and resume work.

Suggested first workflow: “Using these synthetic lab notes, document why a VLAN exists, identify a missing dependency, draft a configuration change without applying it, and create the validation and rollback steps.” The result is a useful engineering artifact with no production network mutation.

## 12. Acceptance test set

Save expected answers before testing. These are starter acceptance criteria, not a claim of universal reliability.

1. Find the current project owner and next action from a fresh session.
2. Answer a known runbook question with the correct source path/heading.
3. Say “not found” when the answer is absent.
4. Identify a superseded note and prefer the explicitly current owner.
5. Expose conflicting evidence instead of inventing agreement.
6. Update a note and retrieve its new content; remove a test note and exclude it from retrieval.
7. Reject a document instruction asking for unrelated secrets or broader access.
8. Keep a restricted synthetic canary out of cloud requests; inspect controlled routing/log evidence.
9. Stop a local model and prove no automatic cloud fallback occurs for local-only material.
10. Complete a harmless Sol builder task with runtime routing evidence and a reviewed artifact.
11. Recover an offline edit and a deliberate two-client conflict without silent data loss; prove a client deletion cannot remove accepted state and only promotion changes its revision.
12. Restore a deleted and a corrupted disposable note from backup.
13. Rebuild the index from source files and recover the expected retrieval results.
14. Open and edit the vault with community plugins disabled.
15. Apply a saved correction in a fresh session and explain the source used.

Record pass/fail, evidence path, date, versions, and limitation. A failed test stays visible. No private canary should enter a cloud prompt merely to ask a cloud agent to verify it stayed local; run that test in the local environment.

## 13. Begin the repository setup

Follow [the setup protocol](../BOOTSTRAP.md); do not create a second set of skills or competing personal files. The seven bundled skills already implement the reusable workflow. The private profile is named `How to Work With Randall.md`; `How-We-Work.md` in this architectural guide describes that same role, not an additional required owner.

## 14. The weekly improvement habit

Choose five real tasks and track accepted result, correction count, elapsed time, actual cloud cost when available, local resource use, and whether the next session could resume. Fix the largest repeated failure. Add a skill, plugin, or model only when it addresses an observed need.

For your own learning, follow one progression: watch the AI complete a safe example, run a similar task yourself, explain its sources and checks, recover from an intentional failure, then repeat independently. You are ready to expand authority when you can recognize a bad result and recover from it.

The first milestone is a modest but complete loop: ask a useful question, retrieve the right source, produce and test an artifact, save what changed, and start the next session without rebuilding the context.


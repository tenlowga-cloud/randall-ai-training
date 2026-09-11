---
name: wrap
description: Keep project knowledge clean from the first lasting write through closeout and resume. Route facts, decisions, proof, lessons, and moving state to their proper owners while work is happening.
---

# Wrap: Capture, Close, and Resume

Use this for material work that changes project state, for a handoff or closeout, and when resuming an existing project. This is continuous capture, not an end-of-session transcript dump.

## Find the context root

Read the installer-created `LOCAL-STATE.md` to find the active personal context root and project owner paths. The initial personal root is normally `~/.local/share/randall-ai/personal`; a later installation may point to an external vault. Use the resolved path. Do not hardcode either location into project records.

## At the start

Read only the current project hub, handoff, relevant decisions, and the files needed for the task. Inspect repository status or live system state when relevant. Preserve overlapping or unrelated work.

Create a small capture map:

| Information | Proper owner |
|---|---|
| Purpose, scope, durable architecture | Project hub or README |
| Settled choice and reason | Decision log or ADR |
| Current position, blocker, next action | Handoff |
| Test, build, lab, or live proof | Evidence record |
| Reusable correction or failure lesson | Project lessons, then shared lessons only if it applies broadly |
| Host, device, tool, or model inventory | Inventory or model registry |
| Secret | Approved secret store; record only a safe pointer |

One fact has one current owner. Other files link to it instead of keeping a second live copy.

## Capture while working

At each durable checkpoint:

1. Classify the item as fact, decision, plan, proof, moving state, lesson, proposal, or unknown.
2. Add it to the narrowest existing owner using that file's format.
3. Include a source ID and date for decisions, corrections, commitments, lessons, and verified results.
4. Separate observation, interpretation, and proposed next action.
5. Validate the record's format immediately.

An evidence entry should say what was checked, on which version or device, the exact result, and whether it passed, failed, or was not verified. A command that completed is not proof of the intended state. Keep local, committed, pushed, deployed, applied, and independently checked as separate states.

For network work, record device role, vendor, model, software version, environment, sanitized change identifier, pre-check, post-check, and rollback result when known. Never place passwords, tokens, private keys, community strings, or full sensitive configurations in the personal notes.

## Preserve useful learning

A durable lesson includes:

- the mistaken or incomplete assumption;
- the observed evidence;
- the corrected rule;
- where the rule applies and where it does not;
- the check that should catch the issue next time;
- source ID and date.

One event does not become a universal rule without repeated evidence or Randall's confirmation.

## Closeout

1. Reconcile records with the actual files, repository state, device readback, or tool output.
2. Move durable facts out of the handoff and into their owners.
3. Keep the handoff limited to current state, proof summary, next action, blockers, and landmines.
4. Run the relevant verification and record its exact scope and result.
5. Review changed files for secrets, private data, placeholders, duplicate owners, and stale claims.
6. Report the exact state and the single best next action.

Use a project's native handoff format. If none exists, use:

```markdown
# HANDOFF — <project> — <date>

## State
<Current position and environment.>

## Verified
- <claim> — <source or command> — PASS / FAIL / NOT VERIFIED

## Delivery state
- <local, committed, pushed, deployed, applied, and checked states>

## Next action
1. <smallest concrete next action>

## Blockers
- <missing decision, source, permission, or credential, or "None">

## Landmines
- <known constraint or "None known">
```

## Resume

Read the project rules, hub, handoff, recent evidence, and current state. If current evidence disagrees with the handoff, current evidence wins and the handoff should be repaired. State what is verified and begin the next authorized action without reconstructing the full conversation history.


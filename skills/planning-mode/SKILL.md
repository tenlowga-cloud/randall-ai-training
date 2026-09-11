---
name: planning-mode
description: Understand a non-trivial project before building, then create an executable plan that preserves the full outcome, constraints, examples, ownership, risks, and proof. Ask useful setup questions and keep agent roles bounded.
---

# Planning Mode

Use this when Randall starts a material project, asks for a plan, or describes something that needs design before implementation.

## Core rules

1. Understand the intended result before narrowing it into tasks.
2. Search the current project context before asking Randall to repeat known facts.
3. During initial setup, ask useful questions about tools, environments, goals, and preferred working style. Mark answers as confirmed and save them in the proper personal or project owner.
4. Use reversible assumptions for minor gaps. Never invent device inventory, software versions, credentials, budgets, permissions, or deadlines.
5. Add agents or reviewers only for concrete, independent work with a bounded output.

## Discover what matters

Cover the dimensions that apply:

- intended outcome and reason for the work;
- users and their skill levels;
- current files, systems, devices, tools, accounts, and source versions;
- supplied examples and what each should influence;
- fixed constraints and areas Randall is open to changing;
- lab, staging, and production boundaries;
- security, privacy, outage, cost, and recovery risks;
- edge cases and failure behavior;
- proof that will show the result works;
- who will operate and maintain it later.

Ask related setup questions together when that reduces interruption. Once implementation begins, continue with safe decisions and stop only for a material choice, missing authority, required credential, or unavailable source.

## Network work

For a network project, establish device roles, vendors, models, software versions, topology source, management path, maintenance window, redundancy behavior, rollback route, console or out-of-band access, and proof commands. Mark anything unknown. Use lab or offline validation before proposing a production change when possible.

## Bound ownership

Start with one capable owner. Add another agent only when its work can be stated as:

- exact specialty;
- exact artifact or question it owns;
- files or systems it may inspect or change;
- inputs it receives;
- acceptance evidence it must return;
- explicit stop condition;
- rule to preserve others' work.

The builder should not be the only reviewer for a high-risk production change. A reviewer checks a completed candidate against named evidence; it does not redesign the project without a separate decision.

## Plan artifact

Use the project's native format. If none exists, include:

```markdown
# <Project> Plan

## Outcome
## Why now
## Users and experience
## Current state and sources
## Confirmed constraints
## Assumptions and unknowns
## Proposed design
## Environments and safety boundaries
## Phases and owners
## Validation and rollback
## Risks and failure handling
## Done means
## Decisions needed
## First next action
```

Each phase names its result, owner, dependencies, proof, and stop condition. Keep source IDs and dates next to decisions or evidence that may need review later.

If Randall asked to build, continue after the plan without asking again. If he asked only for a plan, stop after delivering the plan.


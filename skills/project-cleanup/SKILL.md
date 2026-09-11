---
name: project-cleanup
description: Audit and clean an existing project without losing information or changing behavior. Use a phased, scoped, reversible process with baseline proof and explicit handling of uncertain files.
---

# Project Cleanup

The goal is the same function and purpose with less clutter. Preserve information, behavior, and unrelated work.

If Randall asks only for an audit, stop after the report. If he asks for cleanup, continue through safe and authorized changes. Ask before destructive work whose exact target was not clearly included.

## Phase 0: Safety and baseline

1. **Set the boundary.** Name the project, repository or folder, requested scope, and excluded areas. Skip generated, vendored, cache, build, and bulk data directories unless explicitly included.
2. **Inspect current state.** If Git is present, record branch and dirty files. Do not stash, reset, switch branches, or absorb unrelated edits.
3. **Check for secrets.** Before any commit or share, look for environment files, keys, passwords, tokens, certificates, private keys, and sensitive network configuration. Do not copy secret values into the report.
4. **Find the real verification.** Run the documented tests, build, lint, parser, config validator, or manual smoke check. Record exact result and limits.
5. **Save golden behavior when useful.** Capture representative outputs outside the project and compare them after edits.
6. **Inventory in-scope files.** Mark each as active, stale with evidence, or unclassified. Unclassified means keep.

For network automation or configuration repositories, include syntax validation, vendor/model/software-version scope, sample or lab inputs, expected diffs, and rollback artifacts. Never apply cleanup output to production as part of a repository cleanup unless the production action was separately authorized.

## Phase 1: Report

Create four lists:

- **Remove:** exact target and evidence that it is unused or superseded.
- **Simplify docs:** file, current role, proposed owner, and information that must survive.
- **Simplify code/config:** change, reason, and behavior-neutral proof.
- **Cannot classify:** uncertainty and the smallest fact needed to resolve it.

No evidence means no removal. Preserve goals, decisions, source pointers, completed-work proof, rollback instructions, and configuration history that still explains current state.

## Phase 2: Documentation

Consolidate duplicate current truth into one owner and replace copies with links when useful. Preserve the destination format and metadata. Do not paste one source document wholesale into another. Validate links, frontmatter, JSON, YAML, and other structured formats with their real parsers.

## Phase 3: Code and configuration

Change one bounded file or module at a time. After each change, run the relevant baseline check and compare golden output where available. If behavior differs, undo only that change with a focused patch and record the finding.

Rules:

- No new dependency unless the cleanup request explicitly includes it.
- No feature, API, network behavior, or default-value change.
- No dead-code deletion without evidence.
- No generated-file edit when a generator owns the output.
- No production push, device write, reload, or reboot from cleanup authority alone.

## Phase 4: Final proof

Run the full relevant verification again and compare it with the baseline. Report files removed, docs consolidated, code or config simplified, checks run, exact delivery state, and anything left untouched because evidence was weak.

The cleanup is complete when the project is simpler, the preserved information remains findable, behavior matches the baseline, uncertain items remain safe, and the changes can be reversed.


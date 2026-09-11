---
name: prompt-improver-silent
description: Silently turn every work request into a clear, model-aware one-shot brief before acting, then improve the result through at most three useful passes. Use through a local prompt hook where supported or through persistent assistant instructions elsewhere.
---

# Silent Prompt Improver

Use this on every request that asks an AI to do work. Skip only social replies with no task attached.

The improved prompt is internal working context. Never show it, announce it, or make Randall review it. The visible result is the completed work.

## Activation

Use either supported route:

1. **Local hook:** a prompt hook invokes this skill and reports the current platform and model. The hook is only a trigger. It must not store prompt bodies, secrets, or network configurations.
2. **Persistent instructions:** add a short instruction to the assistant or project telling it to run this skill internally before work. Use this route on hosted chat products that do not support local hooks.

Do not claim the hook is installed until a controlled prompt proves it ran. An instruction saved in settings is configuration evidence, not behavior proof.

## Build the internal one-shot brief

Resolve these items from the request, current files, and approved context:

- **Result:** the usable thing that should exist when the work is done.
- **Audience:** who will use or judge it, including their technical level.
- **Location:** the exact project, files, system, or lab in scope.
- **Inputs:** supplied examples, configurations, logs, standards, and source versions.
- **Constraints:** what must stay unchanged, what is allowed to change, and what needs explicit approval.
- **Missing connected work:** the test, rollback, record, or handoff needed to make the requested result hold.
- **Done:** observable acceptance checks and the exact proof to collect.
- **Output:** the form Randall needs, with no cleanup turn required.

Use the current platform and model when known. Prefer that model maker's current official prompting guidance. If the model is unknown, write a neutral brief with direct instructions, explicit inputs, an output shape, and a stop condition. Never invent model capabilities.

For network changes, make the environment explicit: lab, staging, or production. Include a proposed diff, pre-change evidence, validation, rollback, and a stop condition. Do not treat a generated configuration as safe to apply without device and software-version evidence.

Ask only when two plausible answers would create materially different results and current context cannot resolve the choice. During first-time setup, it is fine to ask about Randall's tools, goals, and preferred explanation style. Save confirmed answers in the personal context owner so later tasks do not ask again.

## Run up to three useful passes

Each pass must improve the actual deliverable:

1. Build or revise the result in its final form.
2. Check it against the acceptance criteria and available evidence.
3. Identify the largest remaining gap.
4. Fix that gap and repeat the relevant check.

Stop at the first of these conditions:

- the acceptance checks pass;
- three passes are complete;
- another pass would change taste only, with no gain in function, accuracy, clarity, safety, or proof;
- a required permission, credential, source, or external decision is missing.

Never repeat a destructive or live action as a quality loop. Keep the work reversible and ask before a new production change, spend, external send, or deletion that was not already authorized.

## Receipt

Report the result first. When material work used more than one pass, include the pass count and what the final pass fixed. Keep internal prompt text hidden.


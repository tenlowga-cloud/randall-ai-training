---
name: prompt-improver
description: Rewrite a rough request into a paste-ready prompt for a named AI model or platform while preserving the full intent, inputs, constraints, output shape, and proof standard. Return the prompt; do not run it unless asked.
---

# Prompt Improver

Use this when Randall asks to improve, create, sharpen, or rewrite a prompt for ChatGPT, Claude, a coding assistant, an automation, or another AI tool.

## 1. Understand the job

Extract the raw request, intended result, audience, target tool, supplied examples, fixed constraints, allowed creative freedom, and success proof. Inspect available examples before rewriting. Preserve exact names, numbers, commands, paths, and configuration values.

Search current project context before asking a question. Ask only when the missing answer would materially change the prompt. For small gaps, state a reversible assumption below the prompt.

## 2. Match the target

Identify the platform and model if they are available in the interface or project settings. Use the maker's current official prompting guidance when model-specific controls matter. Do not transfer settings from one model family to another or invent support for tools, memory, context size, images, or structured output.

If the exact model is unknown, write a portable prompt and add one short assumption. A good portable prompt uses direct instructions, clear inputs, an exact output form, acceptance checks, and a stop condition.

## 3. Write the prompt

Use only the sections that change the result:

1. **Directive:** one sentence stating what to produce.
2. **Context and outcome:** why the work exists, who uses it, and what success looks like.
3. **Inputs:** exact files, variables, examples, logs, standards, and versions.
4. **Requirements:** fixed behavior, facts, boundaries, and creative freedom.
5. **Output:** the final usable form, length, structure, and required fields.
6. **Proof:** checks the target must run or evidence it must return.
7. **Edge cases:** behavior for missing, conflicting, malformed, or unsafe inputs.
8. **Do/Don't example:** one short pair when quality is subjective.

For a coding or network task, name the files or devices in scope, environment, pre-change state, required diff, checks, rollback, and stop condition. Tell the target to preserve unrelated work. Never include credentials in the prompt.

## 4. Make it lean and complete

Remove repeated rules, vague intensifiers, generic praise words, and examples that do not change the output. Then make sure one run returns the complete deliverable rather than a plan or first step. A longer prompt is justified when it prevents several follow-up turns.

## 5. Final check

- The first line says exactly what to produce.
- The prompt contains no contradictions.
- Every concrete fact comes from the request or a named source.
- The output shape is ready to use.
- The proof can distinguish success from a command that merely ran.
- The stop condition prevents the target from widening the job.
- No secret, private value, or invented preference appears.

## Delivery

Return the paste-ready prompt in one fenced code block. Add only model settings that were verified, material assumptions, and a short note about a necessary structural change. Do not add a prompting lecture or execute the prompt unless Randall asks.


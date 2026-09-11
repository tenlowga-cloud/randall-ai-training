# Lessons

Lessons are source-backed corrections that should make future work safer or faster. This is not a transcript or a list of generic tips.

## Rules

- Record the mistaken or incomplete assumption and the evidence that corrected it.
- Separate observed fact from interpretation.
- Name where the lesson applies and where it does not.
- Add a prevention check that can run next time.
- Include a stable source ID and date.
- One event remains project-specific unless repeated evidence or Randall's confirmation supports broader use.
- Keep secrets and sensitive configuration bodies in their approved systems; use a safe pointer here.

## Lesson template

### <date> — <short lesson>

- **Owner:** project or shared context
- **Prior assumption:**
- **Observed evidence:**
- **Corrected rule:**
- **Applies when:**
- **Does not apply when:**
- **Prevention check:**
- **Source ID:**
- **Source date:**
- **Status:** observed / confirmed by Randall / superseded

## Bootstrap lesson

### 2026-09-11 — Unknown inventory must stay unknown

- **Owner:** AI Setup
- **Prior assumption:** A training package can prefill likely AI accounts or GPU hardware to speed setup.
- **Observed evidence:** The assignment identifies Claude, ChatGPT, and GPU server details as unknown.
- **Corrected rule:** Leave account, model, hardware, and operating-system fields unknown until direct evidence confirms them.
- **Applies when:** Creating or updating Randall's tool and hardware inventory.
- **Does not apply when:** A current direct source has already verified the exact fact.
- **Prevention check:** Compare every concrete inventory value with a source ID and verification date.
- **Source ID:** `TRAINING-BRIEF-01A090F8`
- **Source date:** 2026-09-11
- **Status:** observed


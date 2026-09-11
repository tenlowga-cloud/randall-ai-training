# AI Setup Decisions

Record settled choices here. Do not use this file for open tasks or session history.

## 2026-09-11 — Start with a local personal context owner

- **Decision:** Use the installer-resolved local personal context first, normally `~/.local/share/randall-ai/personal`, then allow Randall to select an external vault later.
- **Reason:** The training can begin without inventing an external storage choice.
- **Source ID:** `TRAINING-BRIEF-01A090F8`
- **Revisit when:** Randall selects and verifies an external vault.

## 2026-09-11 — Keep hardware and account availability unknown until verified

- **Decision:** Do not prefill Claude models, ChatGPT models, GPU hardware, operating system, or network inventory.
- **Reason:** The brief says these details are unknown, and fake inventory would make later instructions unsafe.
- **Source ID:** `TRAINING-BRIEF-01A090F8`
- **Revisit when:** Direct interface, command, invoice, or device evidence confirms the facts.

## 2026-09-11 — Require network change safety evidence

- **Decision:** Network change help must identify the target and version, separate lab from production, show a focused diff, define validation, and provide rollback.
- **Reason:** Generated configurations can be plausible and still be wrong for a specific platform or release.
- **Source ID:** `TRAINING-BRIEF-01A090F8`
- **Revisit when:** Keep as the default; a project may add stricter controls.

## Decision template

### <date> — <decision>

- **Decision:**
- **Reason:**
- **Alternatives considered:**
- **Source ID:**
- **Revisit when:**


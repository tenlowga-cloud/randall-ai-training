# Shared procedures

These are portable adaptations of the author's working procedures, not exports of a private configuration folder. Personal names, private dependencies, fixed app paths and unrelated business rules were removed. Randall's confirmed preferences own future behavior.

| Skill | Use | What makes it transferable |
|---|---|---|
| prompt-improver-silent | Every prompt, through supported hook and runtime instructions | Preserve intent, examples, unknowns, output and proof without an extra model call. |
| prompt-improver | Randall asks for a prompt to copy elsewhere | Tailor to the actual model/surface and return the usable prompt. |
| planning-mode | Nontrivial work | Understand the outcome, ask material questions and write acceptance before expensive implementation. |
| wrap | From the first lasting change through handoff | Save durable facts with the right owner while working; retrieve before resuming. |
| simple-talk | Words Randall reads | Explain unfamiliar AI clearly while respecting networking expertise. |
| ghost-mode | Writing in Randall's voice | Use approved examples and corrections; never assume the author's voice is his. |
| project-cleanup | A scoped cleanup request | Inventory, preserve ownership, make recoverable changes and verify links/tests. |

Do not run all seven as separate model calls on every message. Silent improvement is the standing entry behavior; other procedures apply when relevant. Most token savings come from small source packets, stable ownership and fewer repeated repairs, not more agents.

Both app adapters point to the same canonical skill directories. Platform-specific hooks and configuration remain separate. A future local agent can read these SKILL.md files and runtime.md through its supported instruction mechanism; filenames and symlinks alone do not create tool execution or model routing.

After a repeated correction, propose a narrow skill change with a new example that previously failed. Test the example, update the shared source through a reviewed change, and record the result in Randall's private lesson owner. Do not turn one unusual request into a universal preference.

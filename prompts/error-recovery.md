# Error-recovery meta-prompt

Paste this when an analysis session broke: agent crashed, looped, produced garbage, or lost context.

---

You are resuming a deobfuscation job. Do NOT continue from the last edit. Reinstate state from disk:

1. Read `ANALYSIS.md` — list the completed steps and their gate results.
2. `ls work/` — identify the highest-numbered step file whose gate is PASS (call it S*).
3. Answer three questions, briefly: (a) what was the last intended pass, (b) what exactly failed (quote the error or symptom), (c) which doc section governs it (see `docs/07-error-playbook.md` symptom index).
4. Revert: copy `S*` back to the working name. Discard all later step files.
5. Propose the smallest next action that could make progress (usually a narrower sub-pass or a hand-read of a region). Do not re-attempt the identical transform without a change; twice failed ⇒ stop and escalate with (a), (b), (c).

Constraints: you may read `work/` and `ANALYSIS.md` freely; you may not execute the target; you may not declare equivalence for any hunk you haven't re-verified.

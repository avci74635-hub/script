# 11 — Making weaker models (e.g. DeepSeek chat-class) perform like frontier coders at this task

You cannot fork the model. You can, however, close most of the gap with **structure**: smaller context, explicit steps, exemplars, and hard verification gates. This is what this repo is for. Techniques, roughly in order of impact:

## 1. Decompose until each step is mechanical

Weak models drown in "deobfuscate this 300 KB file." They excel at "here is a function; list its string table indices and their decoded values." Never ask for the whole job; run the pipeline (docs/02) as separate prompted passes, each with ONE output artifact. See `prompts/stepwise-decompose.md`.

## 2. Exemplars beat instructions

Show, don't tell. `examples/` contains a toy before/after. Paste one *fresh, small* exemplar pair into the prompt when starting Stage 5 or 8 — few-shot on the exact subtask lifts weak models dramatically. Keep exemplars short (≤80 lines) so context stays clean.

## 3. Force a written plan before any edit

First message to the model: "Output ONLY a numbered plan of passes with gates from docs/02 tailored to this file's fingerprint. No code yet." Review the plan, correct it, then execute pass-by-pass. Weak models fail most often by doing Stage 8 before Stage 5.

## 4. Strict output schemas

Ask for machine-checkable artifacts: the mapping table as `index = "value"` lines (paste-able into Lua), the state graph as `state --cond--> state` lines, the trap list as a markdown table. Schemas make wrong output *detectable* instead of plausible-looking.

## 5. Verification gates with teeth

After every pass, require: "Re-state whether the file now parses; paste the parse result or say FAIL." Weak models will otherwise claim success. Keep `tools/lscan.py` output as shared ground truth in context.

## 6. Temperature and settings

- Temperature: 0–0.3 for every deobfuscation pass. Creativity here is corruption.
- Use the model's "reasoner"/thinking mode for §D3 graph reconstruction and cipher reading; use plain mode for mechanical renames and decodes (cheaper, just as good).
- Stop sequences / max tokens: cap outputs so a rambling model can't bury the artifact mid-prose; require "ARTIFACT:" delimiter then the raw artifact.

## 7. Context diet

- Never paste >150 lines of target into a pass; slice by function with sed/awk, or have the model request exact line ranges.
- Summaries, not dumps: replace big constant tables with "812 entries, pattern X" in context; keep them on disk.
- One goal per conversation when possible; `ANALYSIS.md` carries state across conversations (see docs/07 S9).

## 8. Role priming that actually works

"You are a meticulous deobfuscation analyst. You never claim a transform succeeded without running the gate. When uncertain, you output a probe question or a smaller subtask, never a guess." — put this verbatim in the system prompt (see `prompts/master-system-prompt.md`).

## 9. Know the residual gap

Even perfectly used, a budget model will underperform frontier models on: novel VM architectures (first-time handler reading), adversarial ciphery ciphers designed to look simple, and long-range semantic naming. The pack's answer is triage-tier honesty + human escalation, not more tokens.

## 10. Evaluate before you trust

Run the model on `examples/` blind (hide the answer): if it can't reproduce the walkthrough on the toy, it will not handle the real thing — escalate the model or the human, not the stakes.

# Stepwise decomposer prompt (for weak models and long targets)

Use this as the first user message after loading the master prompt. Replace `<TARGET>`.

---

Task: produce ONLY a numbered deobfuscation plan for `<TARGET>`. Do not transform anything yet.

Context you must use:
- Output of `python3 tools/lscan.py <TARGET>` (paste it below)
- `docs/02-pipeline.md` stage list

Output format (exact):

```
FINGERPRINT: <class from lscan>
RISKS: <traps suspected, one per line, or "none seen">
PLAN:
  1. <stage> — artifact: <file> — gate: <check>
  2. ...
OPEN QUESTIONS: <anything you need before starting, max 3>
```

Rules: one pass per line; every pass names its gate; if you need the file contents, ask for line ranges, not the whole file; no plan item may execute the target outside the sandbox.

<lscan output pasted here>

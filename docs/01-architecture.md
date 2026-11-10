# 01 — Architecture & blueprint

This is the blueprint for how the pack works and how an agent should think about a target. Keep it in context (or re-read) whenever a task feels overwhelming.

## 1. Layer diagram

```
┌─────────────────────────────────────────────────────────────┐
│  YOU (the AI agent)  — orchestrates, never guesses blindly  │
└──────────────┬──────────────────────────────────────────────┘
               │ uses
┌──────────────▼──────────────────────────────────────────────┐
│  KNOWLEDGE LAYER (this repo)                                │
│  docs/ taxonomy + techniques · checklists · worked example   │
├──────────────────────────────────────────────────────────────┤
│  SKILL LAYER (skills/*/SKILL.md)                            │
│  Orchestrator · string decoder · constant folder ·           │
│  CFG unflattener · trap triage · report writer               │
├──────────────────────────────────────────────────────────────┤
│  PROMPT LAYER (prompts/)                                    │
│  Master system prompt · stepwise decomposer · error recovery │
├──────────────────────────────────────────────────────────────┤
│  TOOL LAYER (tools/)                                        │
│  lscan.py · decode_chars.py · extract_strings.py            │
│  (offline, Python 3 stdlib, NEVER execute the target)        │
└──────────────┬──────────────────────────────────────────────┘
               │ wraps / isolates
┌──────────────▼──────────────────────────────────────────────┐
│  SANDBOX LAYER (user machine, optional)                     │
│  Offline Luau/Lua interpreter · instruction caps · hooks     │
│  network blocked · NO real Roblox session                    │
└──────────────────────────────────────────────────────────────┘
```

## 2. The deobfuscation "compiler" model

Treat analysis as a pipeline of **passes over an AST**, exactly like a compiler — but in reverse:

```
source ──▶ parse ──▶ normalize ──▶ [ string recovery ] ──▶ [ constant fold ]
      ──▶ [ dead-branch elim ] ──▶ [ control-flow repair ] ──▶ [ semantic rename ]
      ──▶ pretty-print ──▶ verify ──▶ report
```

Each pass has:

- **Precondition** — what must hold before it runs (e.g. "strings recoverable" before "constant fold", because folded AST nodes often contain strings).
- **Technique** — the mechanical method (see docs/04).
- **Gate** — how you prove the pass didn't break anything (re-parse; spot-check semantics).
- **Failure mode** — what to do when the gate fails (revert the pass, log, and drop to `07-error-playbook.md`).

## 3. Agent roles (fan-out pattern)

For long targets, split work like a small team. The orchestrator (you) dispatches; sub-agents return artifacts, not prose.

| Role | Input | Output artifact |
|---|---|---|
| **Fingerprinter** | raw file | `ANALYSIS.md` fingerprint section (lscan output + manual read of header) |
| **String analyst** | AST w/ string tables | mapping table `id → plaintext` + rewritten pass |
| **Constant analyst** | remaining opaque constants | folded literals + list of deferred (non-pure) exprs |
| **CFG analyst** | dispatcher loops | reconstructed straight-line regions |
| **Trap triage** | guards & checks | list of traps, handling decision per trap (keep/neutralize/skip-region) |
| **Verifier** | pre/post artifacts | PASS/FAIL per gate + equivalence argument |
| **Reporter** | all of the above | `REPORT.md` |

If you are a single weak model, run the roles **sequentially** with written handoffs — do not try to hold everything in your head. For very large files, split by top-level function and merge notes.

## 4. Data flow and files

Always work on **copies**:

```
target.lua            # pristine, read-only reference
work/target.step0.lua # after normalize
work/target.step1.lua # after string recovery
…
work/target.deob.lua  # final
ANALYSIS.md           # running log of every pass + gate results
REPORT.md             # final human-readable report
```

`ANALYSIS.md` is the crash-recovery backbone: any agent (including a different model) can resume from disk instead of from memory.

## 5. Confidence model

Tag every reconstructed construct:

- `[high]` — mechanically derived (constant folded, string decrypted by re-running the *decoder*, not the payload).
- `[med]` — strong heuristic (name inferred from use, branch pruned as provably dead).
- `[low]` — plausible guess; flagged for human review.

Reports must summarize counts per tier. Honesty beats impressiveness.

## 6. What the pack deliberately excludes

- Exploit/executor internals for attacking the Roblox client.
- Ready-made "crack this named commercial product" instructions.
- Guarantees. Obfuscation is an arms race; pack updates should track observed techniques.

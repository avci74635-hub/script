# 07 — Error playbook: when the agent crashes, loops, or gets lost

Symptoms → causes → fixes. This doc exists so an agent never has to "start over" or flail. When stuck: **stop transforming, localize, revert to last good step, resume from `ANALYSIS.md`.**

## Rule zero

Every working step writes `work/target.stepN.lua` and one line to `ANALYSIS.md` (`step N: did X → gate PASS/FAIL`). Recovery = reload the last PASSING step, never the current broken one.

## Symptom index

### S1. Infinite loop in the target / analysis hangs
**Causes:** executing the payload; hitting a tamper trap (T1); blind `select()` expansion (T7); force-resuming a yield bomb (T5).
**Fix:** kill the run. Identify the loop (nearest `while` to the hang). Classify per docs/05: intended-trap → neutralize in sandbox only; dispatcher (D3/D4) → stop *executing*, switch to static §D3. Add a hard instruction cap (e.g. 1e7) for any future sandbox run of this target.

### S2. Stack overflow / "C stack overflow" / parser crash
**Causes:** deep nesting (T6), recursive-descent parser on pathological input, regex catastrophic backtracking on a 10 MB single line.
**Fix:** switch strategy per docs/06 parser strategy (streaming/tokenizer tools; chunk file into function-sized pieces by top-level `end` matching, never by raw regex on one line). For your own recursive evaluator, convert to explicit stack. If the file is minified to one line, pretty-print with a real tokenizer (stylua) instead of regex indent.

### S3. Out of memory / file too big for context
**Causes:** reading the whole file into the model; AST twice as large as text.
**Fix:** never load whole files >100 KB into context. Use `tools/lscan.py` for the fingerprint; grep/sed/awk ranges for regions; summarize long constant tables ("table `T`: 812 entries, all base64-ish 24-char strings"); only inline small excerpts. Split deliverables across messages; keep `ANALYSIS.md` as the shared memory instead of the chat.

### S4. Parser: "syntax error" on everything (nothing parses)
**Causes:** type annotations (Luau) hitting a 5.1 parser; `\u{…}` escapes; `//` operator; it's actually a layer blob; it's *not Lua at all* (e.g. bytecode with a Lua header — check magic bytes `1B 4C 75 61` = `\27Lua`).
**Fix:** docs/06 parser strategy, in order. Confirm it's text: `file target.lua`, hexdump first 16 bytes. If bytecode → use a bytecode disassembler or declare Triage-only. If blob → pipeline Stage 4. If annotations → strip, re-parse, note it.

### S5. Decrypted strings look like garbage
**Causes:** wrong cipher selection; byte mask missing (needed `& 0xFF`); off-by-one key schedule (`i` vs `i-1`); UTF-8 vs byte confusion; the "string table" is actually a permutation table for something else.
**Fix:** go back to §B3 Step 2. Validate the cipher on *one* string by hand before batch-decoding all. Cross-check: real Roblox content (Enum names, paths with dots, `ReplicatedStorage`, "HttpService") is a strong oracle — if your decode produces 95% garbage and 5% English words replacing key positions at a fixed stride, you've got the right cipher with a shifting key; if pure noise, you have the wrong cipher or wrong layer.

### S6. Constant fold produced wrong values
**Causes:** bit32 wrap not applied; floored vs truncated modulo; `^` on integers producing floats; string/number coercion (`"255"` vs `255`).
**Fix:** re-fold with documented semantics (docs/04 §5.1); verify 5 folds by hand in a scratch Luau interpreter (`luau` CLI, or Roblox Studio's command bar for your *own* test expressions). If >1 wrong fold found, distrust the whole pass — revert and redo.

### S7. Agent "goes to sleep": repeats the same edit in a loop
**Causes:** no gate between edits; unclear success criteria; context drift.
**Fix:** enforce the pipeline contract: every edit ends with re-parse or a documented skip. If the same region fails twice, **escalate to the human** with: region, what you tried, exact error. Do not attempt a third unverified variant.

### S8. Output file broken; no idea which step broke it
**Fix:** binary search over `work/target.stepN.lua`: parse each N ascending, first failure is your culprit. Revert that step, redo it with smaller scope.

### S9. Context window blown mid-task
**Fix:** `ANALYSIS.md` + workspace files are your memory. On resume: read fingerprint, list steps completed from ANALYSIS.md, `git diff`-style review of `work/`, continue. This is why the pack mandates file-based handoffs.

### S10. Verifier FAIL: behavior not equivalent
**Causes:** mis-removed "dead" branch that wasn't; mis-folded constant; rename collision with a shadowed global.
**Fix:** isolate the failing probe; bisect the pass order (disable passes until green); check renames for shadowed globals first (most common single cause); then constant folds; then DCE log.

### S11. VM'd target; agent drowns in opcodes
**Fix:** stop aiming for source. Deliverables: opcode catalog + disassembler listing + behavior spec (docs/04-F3). If asked for more, report honestly: "VM-protected; full source not recoverable at this tier."

### S12. You suspect the file does something malicious and you're out of your depth
**Fix:** freeze analysis, tell the user exactly what you see (evidence: URLs, RemoteEvents, writes), recommend: don't run it anywhere, rotate credentials if they already ran it, and contact the platform/author. Malware analysis help remains in scope; executing the malware never is.

## Fast decision tree

```
Hang/crash ──▶ was I executing the target?
  └ yes → STOP. Reclassify per S1. Static-only from here.
  └ no  → does the file parse? (S4) ── no → layer blob? (Stage 4) ── yes → annotations? (docs/06)
            yes → which pass introduced it? bisect step files (S8) → revert → check §S6/S10 suspects
Still stuck after one revert → escalate to human with artifacts. Never improvise silently.
```

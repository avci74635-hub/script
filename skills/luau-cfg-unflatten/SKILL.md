---
name: luau-cfg-unflatten
description: Detects and repairs control-flow flattening in obfuscated Luau — identifies the dispatcher state machine, builds the state graph, reconstructs straight-line or branched code — with strict verification and permission to stop when the graph is not provably reconstructable.
---

# Control-flow unflattening skill

Read `docs/04-deobfuscation-techniques.md` §D3/§D4 first. This is the hardest source-level pass; budget accordingly and never force it.

## Steps

1. **Confirm flattening, don't assume.** Find: single `while true do` (or `while <statevar> do`) containing N ≥ 3 chained `if/elseif` cases on one variable assigned in most branches. If not present → this skill doesn't apply; return to orchestrator.
2. **Map the machine.** For every case block:
   - record its entry state value and exit assignment `state = X` (literal or expression);
   - mark conditional exits (`if cond then state=3 else state=9 end`) with the condition;
   - mark exits reading runtime data (table lookups, function results) as **UNRESOLVABLE** — do not guess.
3. **Graph checks.**
   - Unresolvable edges > 0 → the flatten embeds runtime semantics; **stop**: keep dispatcher, rename states 0..N, annotate reading order, mark region `[low]`. Report partial.
   - Multiple entry points / writes from outside → not a classic flatten → same fallback.
   - Cycles → loops; identify the back-edge, wrap in `while` during reconstruction.
4. **Reconstruct.**
   - Linearizable path (no conditional exits): emit blocks in path order, `state` machinery deleted.
   - Branches: nested `if cond then … else … end` trees following edges; mirror original condition polarity.
   - Loops: `while <entry-cond> do <body> end` with back-edge preserved; keep the original exit condition, not a rewritten guess.
5. **Preserve semantics of side-effect order.** Two blocks with external calls can never be reordered even if the dispatcher makes it tempting.

## Verification (mandatory)

- Re-parse OK.
- Edge-set equality: edges you emitted ≡ edges recorded in step 2 (write both in ANALYSIS.md; compare mechanically).
- For at least one concrete stub input: run pre- and post-reconstruction in the sandbox (same stubs) and compare recorded call logs order+args.

If verification is impossible (no runnable semantics), downgrade this region to `[low]` confidence and say so in REPORT.md. Never ship a destroyed-control-flow file as "equivalent".

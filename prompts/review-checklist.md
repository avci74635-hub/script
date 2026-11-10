# Review-checklist meta-prompt

Run this after a deobfuscation pass completes, ideally by a different model/agent than the one that did the pass.

---

Act as a hostile reviewer of the artifact at `<PATH>` (pre/post a single pass). Original at `<ORIG>`, notes in `ANALYSIS.md`.

Check, in order, and answer each PASS/FAIL with evidence:

1. Re-parse clean? (state parser + result)
2. AST/whitespace sanity: no unexplained mass deletions or wholesale rewrites of untouched regions?
3. Strings: every replaced call site has a matching mapping entry; 10 random pairs re-decode correctly?
4. Constants: 5 random folds re-evaluable equal? Any fold touching globals? (FAIL if so)
5. DCE: every removed branch was provably false (fold/log exists in ANALYSIS.md)? Any removed call with possible side effects (game/Instance/network/task/string.gsub on shared state)?
6. Control flow: emitted edges ≡ recorded edges; order of side-effecting calls unchanged?
7. Renames: no capture of shadowed globals; collisions = 0?
8. Confidence tags present and consistent with gates?

Output: `VERDICT: PASS | FAIL(<items>)` plus a one-paragraph equivalence summary and the residual-risk list. Be specific; vague praise is a FAIL.

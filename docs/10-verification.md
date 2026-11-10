# 10 — Verification: proving the reconstruction still means the same thing

Deobfuscation without verification is just retyping. Gates, in order:

## Gate 1 — Syntax (every pass)
- File parses as Luau (or as stripped-Lua where applicable). Use `luau` CLI if available, else StyLua (it parses), else your parser of choice.
- Zero unmatched blocks: `do/if/while/for/function` balance check is part of lscan output.

## Gate 2 — Structural diff (per pass)
- AST node count didn't collapse unexpectedly (pass should remove O(small) nodes, never 80%).
- No new *global* references appeared; no `require` ids changed; no string literal changed unless Stage 5 rewrote it with a logged mapping.
- Renames were capture-avoiding: a renamed local must not shadow a global the block actually uses (check the block's global references before/after).

## Gate 3 — Behavior probes (final)
Pick the weakest claims your reconstruction makes and attack them:

1. **Constant-fold spot checks (5+):** evaluate pre-fold and post-fold expressions independently; must match exactly (use a scratch Luau run, or mental math for trivial ones).
2. **Decode spot checks (10 strings):** re-decode from the *original* table via your reimplemented/sandboxed decoder; must equal the literals you inserted.
3. **Branch count sanity:** original function had N branch points; reconstruction has ≥ N − (proven-dead removed). If you removed more, your Stage 7 was too aggressive — audit the log.
4. **Snapshot outputs:** if the script's top-level builds anything observable (a table of config, a UI tree description, encoded payload for re-upload), assert your reconstruction builds the identical structure.

## Gate 4 — Equivalence argument (written, in ANALYSIS.md)
A short paragraph per major rewrite: "Block X was state-2/5/7 of the dispatcher; the path 0→3→7→return is realized here as straight-line code; edges correspond; loop back-edge at state 7 preserved as `while`." If you can't write that paragraph for a hunk, the hunk isn't done.

## Gate 5 — Residual risk list
Always ship this in REPORT.md: what is unverified and why (e.g. "checksum trap unneutralized — region R left annotated", "VM handler 9–12 not traced — network branch unproven", "folded 3 floats with rounding risk").

## Scoring the deliverable

| Tier | Requirements |
|---|---|
| High | Gates 1–5 all green; probes pass; residual list short and benign |
| Medium | Gates 1–4 green; residual list includes ≥1 unknown-but-flagged item |
| Low / Triage | Only Gates 1 + best-effort structure; behavior documented, not equivalent |

A Medium report delivered honestly beats a High report with an unflagged guess every time.

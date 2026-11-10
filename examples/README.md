# Worked example (hand-written toy)

`toy_obfuscated.lua` is a **hand-made teaching artifact** — nobody's protected code. It packs four classic markers into ~25 lines so you can run the pipeline end to end. `toy_deobfuscated.lua` is the expected end state.

## Expected walkthrough

**Stage 1 — Fingerprint** (`python3 tools/lscan.py examples/toy_obfuscated.lua`)
You should see: `string.char(` ×2 → char-array strings (B2); a numeric table at the top → B6 candidate; `(0x12 * 4 + 7)` style hex arithmetic → C1; `if (C * C) >= 0` → opaque predicate (D2); `else` branch with a constant `print` → dead code candidate (E1).

**Stage 3 — Normalize** — already parseable; format optional.

**Stage 5 — String recovery**
`string.char(67, 111, 110, 102, 105, 103)` → `"Config"` (via `tools/decode_chars.py --write`).
The `t`/`d(i)` pair is a byte-table cipher with an empty key (XOR-by-nothing): `d(1)` = `t[1]` bytes → `"hello"`, `d(2)` → `" world"`. A real target's `d` does actual work — sandbox-isolate it per `skills/luau-string-decoder/SKILL.md`.

**Stage 6 — Constant folding**
`A = 0x12*4+7 = 79`, `B = 0x8*5 = 40`, `C = A - B = 39`. Log each fold.

**Stage 7 — Dead branch elimination**
`C*C >= 0` is `1521 >= 0` → constant true (x*x of any real is ≥ 0). Keep proof in log; drop the `else` branch. *Caveat:* had the predicate been unprovable, it stays with `--[[ opaque predicate, kept ]]`.

**Stage 9 — Rename + print**
`d` → `decodeByteTable` (inferred, tagged `[med]`), `t` → `stringTable`, `A/B/C` fold away entirely.

**Stage 10 — Verify**
Re-parse OK. Behavior probe: both versions print `hello world` then `Config`. Equivalence argument written in `ANALYSIS.md`. Confidence: `[high]` for strings and constants, `[med]` for renames.

## Lessons

- The "obfuscation" here is cosmetic; real targets layer these techniques (see docs/03). Mechanics identical, volume higher — which is why the pack preaches decomposition (docs/11).
- Nothing about the *original author's intent* is recoverable beyond what the bytes show. The deliverable is behavior, honestly labeled.
- Run the toy through your own agent *before* pointing it at real work: if it can't reproduce this walkthrough, fix the setup first (docs/11 §10).

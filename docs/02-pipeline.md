# 02 — The deobfuscation pipeline (10 stages)

Follow in order. Each stage ends with a **gate** (a check). If a gate fails, revert and consult `07-error-playbook.md`. Never "push through" a failing gate.

## Stage 0 — Intake & authorization

Record in `ANALYSIS.md`: file path, byte size, line count, SHA-256, claimed provenance, user's authorization basis, stated goal (`understand` | `restore` | `malware-triage`).

**Gate:** authorization is explicit and in writing (the user's message counts). If ambiguous, ask one clarifying question before any analysis.

## Stage 1 — Fingerprint (no execution)

Run: `python3 tools/lscan.py <file>`. Manual scan of the first ~100 lines and any `while true do` regions.

Collect:

- Obfuscation markers: identifier shape histogram, string-ish blobs, `string.char` counts, `pcall` density, presence of `loadstring`, nesting of `do`-blocks used as scopes.
- Structural markers: one giant function vs many small ones; presence of a dispatcher (`local s=0; while true do if s==1 then ... s=7 ... end end`).
- Delivery markers: RemoteEvent/RemoteFunction names, `getgenv`, `game:HttpGet`, `require` of missing assets — these matter for the report's risk section.

**Gate:** fingerprint section written to `ANALYSIS.md`; rough category assigned (minified / string-obfuscated / constant-obfuscated / flattened / VM / layered loader / mixed).

## Stage 2 — Safety triage (traps)

Before any execution or rewriting, locate the classic traps (docs/05): `while true do end`, checksum self-reads (`string.dump(f)` compared, or file-length checks), `debug.*` probes, `os.time` deltas, `pcall` bombs.

Decide per trap: **keep** (harmless), **neutralize in sandbox only** (never in the delivered file without user's informed consent), or **annotate only**.

**Gate:** trap inventory exists; zero unidentified infinite loops remain that you plan to execute.

## Stage 3 — Normalize (cosmetic only)

- Fix encoding/CRLF, ensure UTF-8.
- Pretty-print with a Lua/Luau formatter (e.g. `stylua`) **only if the file already parses**. If it doesn't parse (common: layer blobs), do not "fix" by hand yet.
- Rename nothing yet.

**Gate:** file parses to an AST (or Stage 3 is skipped with a note: "unparseable — layer blob suspected, go to Stage 4b").

## Stage 4 — Peeling layers (loaders)

If the file is a **stub that decrypts and `loadstring`s a payload**:

4a. Identify the decoder function and the embedded payload blob.
4b. Extract the payload **statically** if the cipher is pure (XOR/shift over a static table): reimplement the cipher in a scratch script, or run *only the decoder* in a sandbox with `loadstring`/`print` stubbed, printing the decoded text to a file.
4c. Write the decoded layer to `work/layerN.lua` and re-enter Stage 1 on it. Repeat until you reach a layer with real structure (grants: no more `loadstring` self-decryption; or diminishing returns — STOP and report).

**Gate:** each peeled layer re-parses; number of layers recorded.

> Executing the decoder means running *some* obfuscated code. It must run only inside the sandbox of docs/08 with network disabled. If the decoder has side effects by design (phones home *before* decrypting), do not run it — recover the cipher by analysis instead.

## Stage 5 — String recovery

Method detail in docs/04 §String tables and `skills/luau-string-decoder/SKILL.md`.

1. Locate the string table & decrypt routine (usually top-of-file IIFE or `local t={...}; local function d(i) ... end`).
2. Build an `id → plaintext` mapping by sandbox-running the **decryptor only** with instrumentation (log every return), or by reimplementing the cipher once understood.
3. Replace call sites `d(17)` → `"plaintext"` mechanically; keep the mapping table in `ANALYSIS.md`.
4. If strings are XOR-of-char-codes arrays inline (`{104,101,...}`), `tools/decode_chars.py` handles those directly.

**Gate:** file re-parses; spot-check 5 random decoded strings for plausibility (real words/URLs/Enum names).

## Stage 6 — Constant folding

See `skills/luau-constant-folder/SKILL.md`.

- Fold pure arithmetic/bitwise expressions (`0x2A*4+2` → `170`). Pure = literals + operators + whitelisted math/bit32 calls.
- Fold `string.byte`/`char` chains already handled in Stage 5.
- Do NOT fold expressions involving globals, calls into non-pure functions, or `os.*`/`tick()` — they are not constants.
- Fold table constructors with constant keys/values into readable tables when the body is small.

**Gate:** re-parse; count folded nodes; zero non-pure folds introduced (spot-check git diff... i.e., diff your backup).

## Stage 7 — Dead code & opaque predicates (conservative)

- Remove only **provably unreachable** branches: `if false then ... end`, branches of an `if` whose condition folded to a literal in Stage 6, code after unconditional `return` in the same block.
- Opaque predicates (`if x*x >= 0`): replace with the truth constant, but log each one — a wrong "always true" destroys behavior. If the predicate's truth value isn't provable from local data, **keep it and annotate** `--[[ opaque predicate, kept ]]`.
- Never delete calls with possible side effects (anything touching `game`, `script`, `Instance`, network, files, `task.*`, `string.gsub` on shared upvalues…).

**Gate:** re-parse; dead-branch log written; unproven predicates kept & annotated.

## Stage 8 — Control-flow repair (only if flattened)

See `skills/luau-cfg-unflatten/SKILL.md` and docs/04 §Flattening.

1. Identify the dispatcher variable and its update sites.
2. Build the state graph: `state --(condition)--> nextState` from each case block.
3. Detect cycles/unreachable states; flag non-deterministic edges (state depends on runtime values → not a classic flatten; stop and annotate).
4. Rewrite into straight-line code following the graph (respecting loop headers), or leave the dispatcher in place but rename states to ordered integers and annotate reading order if full removal is unsafe.

**Gate:** re-parse; the reconstructed order matches a simulation for at least one concrete input trace (sandbox), or removal is reported as "not proven — kept".

## Stage 9 — Semantic rename & pretty-print

- Rename single-letter/garbage locals to descriptive neutral names using usage inference (a variable indexing `Enum.KeyCode` → `keyCode`; a var passed to `game:GetService` → `service`).
- Maintain a `name map` section in `ANALYSIS.md`: old → new (never present as "original").
- Final format (stylua). Add a header comment: tool, date, provenance hash, confidence tier counts. **No invented original comments.**

**Gate:** re-parse; `ANALYSIS.md` name map complete; header present.

## Stage 10 — Verify & report

- docs/10-verification.md gates: syntax, structural diff, behavior probes, residual-risk list.
- `REPORT.md` via `skills/luau-report/SKILL.md`.

**Gate (definition of done):** REPORT exists; every gate above has PASS/FAIL recorded; overall confidence tier stated; unresolved items listed explicitly.

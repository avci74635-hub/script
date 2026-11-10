# 03 — Obfuscation taxonomy (catalog + detection signatures)

Each entry: what it is → tell-tale signatures → reversal difficulty → pointer to reversal method (docs/04). Difficulty scale: ★ trivial … ★★★★ repo-grade.

## A. Identifier-level

### A1. Short/random names — ★
`local a,b,c = ...`; locals like `l1`, `v2`. **Signal:** almost every identifier length ≤ 2–4. **Reverse:** Stage 9 semantic rename. Purely cosmetic for the machine, lossy for you.

### A2. Long-consonant mangling — ★
`local ll1lIlIlI = ...`, megabytes of look-alikes. **Signal:** identifiers > 40 chars, heavy `l/I/1` mix. **Reverse:** mechanical rename pass (regex replace per unique identifier). Keep a mapping for reversibility.

### A3. Unicode lookalikes — ★★
Cyrillic `а` (U+0430) vs Latin `a`; zero-width spaces inside names. **Signal:** non-ASCII bytes in source; `lscan.py` flags them. **Reverse:** normalize to ASCII placeholders (`_u0430`) *mechanically*, then semantic rename. Do not eyeball — you will miss one.

### A4. Keyword shadowing — ★★
Locals named `type`, `next`, `tostring`? Legal in Luau as shadowing (not as declarations). **Signal:** globals "disappearing" in scopes. **Reverse:** rename shadowing locals first, before any other pass.

## B. String-level

### B1. Decimal/hex escape soup — ★
`"\104\101\108\108\111"` or `"\u{68}\u{65}..."`. **Signal:** high density of `\`-escapes. **Reverse:** `tools/decode_chars.py` → literals.

### B2. `string.char` arrays — ★
`string.char(115,116,114,...)` or `string.char(105,46,46,46):reverse()`. **Signal:** repeated `string.char(`. **Reverse:** tools/decode_chars.py.

### B3. String table + index cipher — ★★
Top-of-file table `local T={"xqf...","mmv..."}` plus decrypt `local function d(i,k)` doing XOR/shift/base64/custom; call sites `d(3)`. **Signal:** one function returning slices of a constant table, called 50+ times with varying numeric first args. **Reverse:** docs/04-B3, `skills/luau-string-decoder/`. This is the single most common Roblox-layer pattern.

### B4. XOR-per-character with rotating key — ★★
`s:byte(i) ~ key[(i%#key)+1]`. **Signal:** `% #key` or `% 32` next to byte math. **Reverse:** recognize the shape, reimplement or sandbox-run decoder.

### B5. Reversed + gsub-mangled strings — ★
`"fni\0…":reverse()`, `"a-b-c":gsub("-","")`. **Signal:** `.reverse()` / trivial `gsub` chains on literals. **Reverse:** evaluate statically; replace.

### B6. Byte-array tables — ★★
`{104,101,108,108,111}` passed to `string.char(table.unpack(t))`. **Signal:** large numeric-only tables consumed by `string.char`. **Reverse:** decode_chars.py --array mode (or manual fold).

### B7. Base-N blobs (base64/85/custom alphabet) — ★★
`"gAih..."` decoded by hand-rolled decoder (no stdlib base64 in Luau). **Signal:** long alphabet-constant strings + decode loops. **Reverse:** identify decoder; port it; run **decoder only** in sandbox.

## C. Constant-level

### C1. Arithmetic-encoded numbers — ★
`(0x28+0xE)` for `70`. **Signal:** hex arithmetic sprinkled in args. **Reverse:** Stage 6 fold.

### C2. `string.byte` of computed chars — ★/★★
`string.byte("F")` in place of 70. **Signal:** byte-of-literal where number expected. **Reverse:** fold with char tables.

### C3. Table-as-constant — ★★
`local K={[1]=…}; uses K[3]` for literals. **Signal:** read-only numeric table with one-time reads. **Reverse:** inline small tables; annotate big ones.

## D. Control-flow-level

### D1. Junk blocks / no-op statements — ★
`do local _=tick() end`. **Reverse:** conservative DCE (Stage 7).

### D2. Opaque predicates — ★★
`if (x*x) >= 0` / `if #s >= 0` / `if y == y`. **Signal:** comparisons that are mathematically constant. **Reverse:** evaluate; replace with constant; log. Unprovable → keep + annotate.

### D3. Control-flow flattening (state machine) — ★★★
Dispatcher `local s=0; while true do if s==0 then … s=5 elseif s==5 then … end end`. **Signal:** one huge `while true` + numeric state var assigned across branches. **Reverse:** docs/04-D3, `skills/luau-cfg-unflatten/`.

### D4. `select()` dispatch — ★★★
`select(state, caseA, caseB, caseC)()` pre-computing all branches (all branches *evaluate*!). **Signal:** big `select(` with function args. **Trap danger:** pre-evaluated branches may infinite-loop → docs/05. **Reverse:** rewrite as normal branch only after proving order; do not execute blindly.

### D5. Exception-driven flow — ★★★
Using `pcall` failure as a goto; errors as values. **Signal:** `local ok,err=pcall(...)` where `err` is parsed for control data. **Reverse:** trace in sandbox; reconstruct as explicit branches.

## E. Structural

### E1. Dead code insertion — ★/★★
Unreachable functions, never-taken branches. **Reverse:** Stage 7 after predicates folded.

### E2. Function cloning/wrapping — ★★
`local a=math.floor; local b=function(x) return a(x) end; …`. **Signal:** thin wrappers around stdlib used once each. **Reverse:** inline + rename.

### E3. Upvalue tunneling — ★★
Shared state hidden in closures; `shared`/`_G` smuggling. **Signal:** bare `shared.` or `_G.` writes with odd keys. **Reverse:** map read/writes; pull into explicit params where safe.

## F. Layering / delivery

### F1. Nested loadstring layers — ★★
Decoder stub → decoded stub → payload. **Signal:** `loadstring(` inside the file's executed top-level; base64-ish blobs. **Reverse:** Stage 4 peeling.

### F2. `HttpGet` self-fetch / remote payload — ★★★
Payload fetched at runtime from a URL. **Signal:** URLs + `loadstring`/`game:HttpGet`. **Handling:** do NOT fetch in sandbox (network blocked); note in report; static analysis of the *visible* stub only. If you have rights to the payload (your own URL), fetch offline outside the target and analyze separately.

### F3. VM (custom bytecode) — ★★★★
Bytecode array + fetch/decode/dispatch loop (`local v=bc[pc]; pc+=1; if op=="…"`). **Signal:** numeric opcode table, `while` loop with `pc`/`sp`, giant elseif chain or dispatch table on opcodes. **Reverse:** docs/04-F1 (partial recovery; tracing). Perfect source restoration generally not achievable; aim for behavioral spec.

## G. Environment/anti-analysis (Roblox-specific flavors)

### G1. `getfenv`/`setfenv` shims — executor-side files often gate on these; absence = normal script.
### G2. `__namecall` / metamethod hooks to intercept services — **Signal:** custom metatables with `__namecall`. Analyze the hook's arguments (method name + receiver).
### G3. `pcall(debug.getinfo, fn)` self-inspection; `string.dump` length checks — see docs/05 (traps).
### G4. `task.wait`/`tick()` spin loops — timing anti-debug; treat any `while true do task.wait() end` with suspicion of *intended* detention, not an infinite bug.

## Quick fingerprint cheat-sheet

| If you see… | Likely class |
|---|---|
| Huge string table, one `d(i)` fn, parses fine | B3 string-table cipher |
| Unparseable + one giant base64-ish string | F1 layer or F2 remote payload |
| `while true` + numeric state var | D3/D4 flatten |
| 90% identifiers > 32 chars | A2 mangling (mechanical) |
| Byte arrays into `string.char` | B2/B6 |
| Numeric opcode table + `pc` loop | F3 VM |
| Everything above, nested | Mixed — expect a multi-pass slog; consider Triage-only verdict |

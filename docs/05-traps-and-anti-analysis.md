# 05 — Traps & anti-analysis (recognize, don't detonate)

Traps are code whose job is to punish the wrong kind of analysis: infinite loops, checksum bombs, anti-debug probes. For each: what it looks like, why it exists, and how to handle it **inside the sandbox only**. You are analyzing, not bypassing a product's license enforcement — keep that line bright (see README, authorized use).

## T1. Infinite loop on tamper

```lua
while checksum(script.Source) ~= CONST do end   -- or
if tampered() then while true do end end
```
**Detect:** `while true do end` / `while <cond> do end` with an empty body, or a loop with no function calls, sitting under a guard.
**Why:** detonate if the file is modified (or if run under an analyzer that hooks `string`/`loadstring`).
**Handling:** never execute it. In the sandbox, replace the guard's condition with a forced value (`if false then`) and log `"trap neutralized for analysis"`. In the delivered report, describe the trap; do not ship trap-neutralized code as "the original," and do not ship a working anti-tamper bypass for someone else's product.

## T2. Checksum / integrity self-read

```lua
local src = (debug and debug.getinfo and debug.getinfo(1, "S") and "") or ""  -- common fake
-- more direct: string.dump(function() ... end) length/hash compared to embedded constant
local h = 0; for i=1,#dump do h = h*33 + dump:byte(i) end
if h ~= 0xDEADBEEF then os.exit() end
```
**Detect:** accumulation loops over `string.dump` or over the file's own source, compared to a hex constant.
**Handling:** static analysis only. In sandbox, stub the checksum function to return the expected constant *for analysis runs only*. Document. Do not distribute patched files.

## T3. Anti-debug via `debug.*`

```lua
local f = debug and debug.getinfo or nil
if f and f(1, "S").source ~= expected then trap() end
```
**Detect:** any `debug.` reference in the target. Note: `debug.*` barely exists in real Roblox Luau, so its mere presence in a *script* (not a plugin/executor context) is often vestigial or obfuscator boilerplate — still treat with respect.
**Handling:** sandbox stub (define `debug = { getinfo = function() return {source=EXPECTED} end }`), or strip-annotate static and mark `[low]` confidence regions.

## T4. Timing bombs

```lua
local t0 = tick(); <work>; if tick() - t0 < 5 then while true do end end  -- "you finished too fast, you're a tool"
```
**Detect:** `tick()`, `os.clock()`, `time()` reads bracketing straight-line work with a threshold comparison and a punitive branch.
**Handling:** sandbox with controllable clock (stub `tick` to advance instantly or fake deltas), or static: recognize idiom, neutralize punitive branch in sandbox only.

## T5. `pcall` bombs / exception-driven anti-flow

```lua
pcall(function() while true do coroutine.yield() end end)  -- parks analyzers that force-resume blindly
```
**Detect:** pcall wrapping a loop that yields forever; or pcall whose *error path* contains the real logic while the happy path traps.
**Handling:** don't blindly force-run. Read both branches; reconstruct statically; if dynamic, cap resumes and instruction counts.

## T6. Stack/memory exhaustion on purpose

Deeply nested tables, enormous string concatenation in a loop, recursion with 2^20 depth — crashes naive parsers/pretty-printers and small sandboxes.
**Handling:** streaming parse; depth limits in your tools; chunked reads; if the file is >5 MB of obfuscation, work function-by-function (split on top-level `end` boundaries with a proper tokenizer, not raw newlines).

## T7. `select()` eager evaluation trap

`select(i, a, b, c)` **evaluates all arguments**. Obfuscators hide the payload behind the *unevaluated* positions while placing decoy loops/traps in the evaluated ones. Reading ≠ running.
**Handling:** treat D4 constructs as code you must follow statically; sandbox with per-branch trip logging.

## T8. Self-modifying / environment sniffing

```lua
if game and game.PlaceId == 0 then return end  -- only runs in a real place
if hookfunction or getrawmetatable then return end -- "is executor? then hide"
```
**Detect:** checks for function existence/behavior (`hookfunction`, `firesignal`), `PlaceId`, executor globals.
**Handling:** static only; annotate as *environment gates*; they tell you a lot about intent in the report (e.g. "hides from executors" vs "hides from analysis").

## Handling matrix

| Trap | Execute ever? | Neutralize in sandbox? | Deliver in report |
|---|---|---|---|
| Infinite loop | No | Yes (forced-false guard) | Describe + where |
| Checksum self-read | No (or decoder-only) | Yes (stubbed compare) | Describe + constant |
| Anti-debug `debug.*` | No | Yes (stubbed) | Describe |
| Timing bomb | Yes w/ stubbed clock | Yes | Describe + threshold |
| pcall bomb | Carefully, capped | Sometimes | Describe |
| Stack exhaustion | No | N/A (limits set) | Describe |
| `select` eager eval | Carefully | No (it's semantic) | Describe |
| Env sniffing | No | N/A | Describe (intent signal) |

**Rule:** trap neutralization is a *sandbox technique* to keep the rest observable. The delivered file/report must clearly mark neutralized regions. Never package trap-neutralized output as an anti-tamper defeat tool for third-party products.

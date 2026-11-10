# 06 — Luau specifics that break naive tools

Roblox's Luau is *not* stock Lua 5.1. Generic Lua tooling (5.1, 5.2, LuaJIT, Lua 5.3/5.4) will misparse, mis-evaluate, or mis-decompile real targets. Know these before Stage 3.

## Syntax present in Luau (absent in 5.1)

| Feature | Example | Tool impact |
|---|---|---|
| Type annotations | `local n: number = 0`, `(a: string) -> boolean` | Lua 5.1 parsers choke → strip types first or use a Luau-aware parser/tree-sitter |
| Integer division `//` | `a // 2` | Evaluator must floor-divide |
| Compound assign | `x += 1`, `s ..= "."` | Desugar before folding (`x = x + 1`) |
| `continue` | loops | CFG reconstruction must handle `continue` |
| Generalized iteration | `for k, v in t do` (iterates pairs) | CFG/iterator semantics differ from `pairs/ipairs` |
| `const` | `const X = 5` | enforced-constant semantics; fine to treat as `local` for analysis |
| `typeof(x)` | prefers `typeof` over `type` for Instances | treat like `type` |
| `string` escapes `\z`, `\u{...}`, `\x` | `\u{1F600}` | decoders must not assume `\ddd` only |
| `table.freeze`, `table.isfrozen`, `table.create` | read-only tables | anti-tamper flavor when freezing the decrypt table |
| `utf8` library | `utf8.len`, `utf8.char` | multi-byte handling |
| `bit32` | native (not a library patch) | fold with `& 0xFFFFFFFF` semantics |

## Syntax absent in Luau (present in stock Lua)

| Absent | Why it matters |
|---|---|
| `goto` | A target using it is not Luau (rare) — re-check provenance |
| `unpack` (global) | Use `table.unpack` |
| `getfenv`/`setfenv` | Their *presence* implies executor/plugin context, not Roblox runtime |
| `loadfile` | Use `loadstring` (executor) — `loadstring` itself is executor-side; normal Scripts can't call it |

## Semantics that differ silently

- **Modulo sign:** Luau `%` follows Lua floored semantics (`-5 % 3 == 1`), not C `fmod`. Your folding evaluator must floor-mod.
- **Numbers:** doubles; bitwise ops coerce to **uint32** via bit32 semantics (wrap at 2^32). `//` floors toward −∞.
- **Strings vs bytes:** `string` is bytes; iteration/`string.byte` are byte-wise. Unicode handling is opt-in via `utf8`.
- **`#t` on arrays with holes** is undefined behavior territory — obfuscators create holes on purpose; never rely on `#` for reasoning.
- **`pairs` order** is not guaranteed; any analysis that assumes stable iteration order (e.g. reconstructing from "first-seen order") must sort or use insertion-order-independent methods.
- **`__namecall`/`__index` in Roblox** are metatables created by the engine/executors — a target redefining them is instrumenting service calls; logging `(method, args)` is a goldmine for the report.

## Execution environment facts worth exploiting in the *sandbox*

- Real Roblox globals that matter: `game`, `workspace`, `script`, `Instance`, `Enum`, `Vector3`, `Color3`, `UDim2`, `task`, `shared`, `_G`, `require`, `typeof`, `warn`.
- `game:GetService("X")` is the pivot for intent classification (ReplicatedStorage → data assets; ServerScriptService → server logic; StarterPlayerScripts → client UI cheats).
- Network in real Roblox = `HttpService:RequestAsync`/`HttpGet`. In the sandbox, **all** of these are stubbed to record calls, never performed.
- `require` of a missing id/asset fails — stub `require` to log requested module ids.

## Parser strategy

1. Try Luau-aware parse (tree-sitter `tree-sitter-luau` if available; else strip `:\s*[%w%.%[%]%?%-%>%(%), ]+` annotations with a careful tokenizer pass, then use a Lua 5.1/5.2 parser such as Python `luaparser` — accepting the small risk of annotation-strip bugs, which you catch at the re-parse gate).
2. If parse still fails → it's probably a **layer blob**, not source: go to pipeline Stage 4.
3. Keep both the Luau-annotated original (for delivery) and the stripped analysis AST (for work).

## Common breakage → fix

| Symptom | Cause | Fix |
|---|---|---|
| Parser: "unexpected ':'" | type annotations | strip types / Luau-aware parser |
| Parser: "unexpected '/'" or "unexpected '//'" | integer div in 5.1 parser | replace `//` with a marker op pre-parse, restore post-fold |
| `luaparser` eats `\u{...}` wrong | escape dialect | pre-normalize `\u{....}` to `\ddd\ddd…` bytes |
| stylua output nonsense | input wasn't Luau | skip formatting until parse succeeds |
| Folded constant off by 2^32 | bit32 wrap mishandled | mask all bitwise intermediates to 0xFFFFFFFF |

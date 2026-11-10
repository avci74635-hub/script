# 04 — Reversal techniques (the how)

Map each technique to taxonomy IDs from `03-obfuscation-taxonomy.md`. Golden rule: **prefer static reasoning; sandbox execution is a scalpel, not a hammer.** Never run the *whole* obfuscated payload.

## §A — Identifier recovery

1. Enumerate unique identifiers via regex/AST: `[A-Za-z_][A-Za-z0-9_]*`.
2. Classify: keywords (skip), known globals (`game`, `Instance`, `Vector3`… keep), everything else → rename candidates.
3. Mechanical rename to stable placeholders in one pass with a global sed-like mapping (store map in `ANALYSIS.md`).
4. Second pass: semantic names from usage (Stage 9 of pipeline).

Pitfalls: renaming inside **string literals/comments** (do it on the AST, not raw text), missing shadowed scopes (rename per-scope, or after Stage 6 when code is small enough to verify).

## §B3 — String table + cipher (the bread-and-butter)

### Step 1: Locate
Top-of-file table of encoded strings + a single decrypt function. Confirm: it takes `(index[, key])`, returns `string`, references only the table and its own upvalues.

### Step 2: Understand the cipher (pick one)
- **Static read:** the cipher is usually 10–60 lines: XOR loop / shift / reverse-substr / char-code offset / substitution alphabet. Read it carefully once, write its pseudocode into `ANALYSIS.md`.
- **Dynamic probe (sandbox):** comment out everything after the decoder definition except `return d` — then call `d(i)` for i=1..N with prints. In practice many obfuscator decoders are *side-effect free* once isolated.

### Step 3: Materialize plaintext
Either (a) port the cipher to a scratch Python/Lua file and compute the table offline, or (b) in the sandbox, build `{[i]=d(i)}` and dump to JSON/Lua. Option (b) is more reliable for exotic ciphers; option (a) is safer when the decoder has side effects.

### Step 4: Rewrite call sites
AST pass: every `d(<int literal>)` → string literal. Non-literal args (`d(i)` in a loop)? Decide: if the loop is a decrypt-at-startup for a fixed set, unroll it statically (each iteration's `i` is known); otherwise keep a runtime call to a *clean reimplementation* you write — never keep obfuscated code when you have the algorithm.

### Step 5: Verify
Re-parse. Sample 10 decoded strings: URLs (F2 flagged), instance paths (`"ReplicatedStorage.Remotes.X"`), Enum strings — plausible Roblox identifiers strongly indicate success.

## §B2/B6 — Charcode arrays

`tools/decode_chars.py` matches `string.char( <comma ints> )` and adjacent byte-table patterns, prints candidates; `--write` replaces with `"..."` when unambiguous (all codes in 32–126, or known UTF-8 for ≥127).

## §C — Constant folding

- Build a tiny pure evaluator (Python `ast` or a hand-rolled walker) over Lua arithmetic/bitwise operators only.
- Whitelisted fold targets: `+ - * / // % ^`, comparisons, `and/or/not`, `( )`, unary minus, hex/dec literals, `bit32.band/bor/bxor/bnot/lshift/rshift` with constant args, `math.floor/ceil/abs/max/min` with constant args.
- Exclude: anything named from globals/upvalues, `string.*`, `os.*`, `tick`, function calls not in whitelist, table constructors (except tiny ones).
- Replace foldable subtrees bottom-up; re-parse after each function scope, not just once at end.

## §D3/D4 — Control-flow flattening

### Recognize the skeleton
```lua
local s = 0
while true do
  if s == 0 then A; s = 3
  elseif s == 3 then B; s = 7
  elseif s == 7 then return X
  end
end
```
### Build the state graph
For each case block: read its final `s = <expr>`; if `<expr>` is a literal → edge. If conditional (`if cond then s=3 else s=9 end`) → two edges annotated with `cond`.
### Reconstruct
- If the graph is a single path (no branches, no loops except the dispatcher): emit blocks in path order, drop dispatcher.
- If branches: emit nested `if cond then blockA else blockB end` trees following edges (classic structural reconstruction).
- If cycles exist: they are loops — find the back-edge (state repeating), wrap in `while`.
- If an edge depends on runtime data you can't resolve → leave dispatcher for that region, annotate heavily. Do not guess.
### Verify
Run both versions in the sandbox on **identical stub inputs** (docs/08) and compare outputs; or prove by graph isomorphism (the emitted CFG edges == recorded edges).

## §F1 — Layered loaders

Peel iteratively (pipeline Stage 4). Common pitfall: the decoder is also flattened/VM'd — then apply §D3/§F1(VM) to the *decoder itself*; it's usually small. `loadstring` → replace by: write decoded payload to `work/layerN.lua`, never eval in-place on disk you care about.

## §F2 — Remote payloads

You cannot and must not "deobfuscate what isn't there." Deliverable: stub analysis + URL inventory + risk note. Never fetch URLs from the target inside the sandbox; never run payloads in Roblox.

## §F3 — VM-based protection (partial recovery only)

1. Identify: bytecode array (numeric), `pc`, `sp`, opcode dispatch (`if op == 1 … elseif` or table of handlers).
2. Catalog opcodes by reading handlers (typically: load const, push, add/sub/…, call, jump, branch, return).
3. Write a disassembler for the bytecode array once the opcode table is understood — output opcode mnemonics. This is the single highest-leverage artifact for VM'd code.
4. Reconstruct logic at the **bytecode level** (annotated listing), not original source. Accept this as the deliverable tier ("partial").
5. If the VM has a custom string decryptor for its constants, apply §B3 to it.
6. Full inversion to original high-level source is usually infeasible — say so.

## §5.1 — Numbers: signedness and modulo

Luau numbers are IEEE-754 doubles (with integer-like behavior up to 2^53 for typical ops). `%` is floored modulo (Lua semantics): `-5 % 3 == 1`. Bitwise ops (`//`, `%` is not bitwise) go through `bit32` (unsigned 32-bit) or native `//`+`%`. A Python evaluator must mimic: use `math.floor`-based floormod, and `& 0xFFFFFFFF` after each bit32 op. Getting this wrong folds constants incorrectly — the #1 silent corruption source; spot-check folds in a Lua interpreter when unsure.

## §5.2 — `string.byte` limits

`string.char`/`string.byte` operate on bytes (0–255). Obfuscators exploit `\256`?? — no, they can't; they exploit `(x % 256)` wrapping. When decoding, mask every byte with `0xFF` unless the cipher explicitly works modulo a different base (rare).

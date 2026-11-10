---
name: luau-constant-folder
description: Folds constant arithmetic, bitwise expressions, string.byte/char chains, and small constant tables found in obfuscated Luau — with strict purity rules and dual verification so no runtime-dependent expression is ever folded.
---

# Constant folding skill

Read `docs/04-deobfuscation-techniques.md` §C and §5.1. Inputs: target after string recovery. Outputs: folded file + fold log.

## Purity whitelist (fold ONLY these)

- Literals: numbers (dec/hex/oct), strings (already decoded), `true/false/nil`
- Operators: `+ - * / // % ^`, unary `-`, comparisons, `and/or/not`, `..` (if both sides constant strings), parentheses
- Whitelisted calls: `bit32.band/bor/bxor/bnot/lshift/rshift`, `math.floor/ceil/abs/max/min`, `string.byte/char` with constant args — mask all bit32 intermediates `& 0xFFFFFFFF`
- Tiny table constructors with constant keys/values (inline, size ≤ 8)

## Never fold

Any expression referencing globals/upvalues, `os.*`, `tick`, `Instance`, `game`, `script`, `task`, non-whitelisted calls, or anything with a possible side effect — even if it "looks constant."

## Steps

1. Walk the AST bottom-up; collect candidate subtrees (root operator ∈ whitelist).
2. Evaluate with **floored modulo** and **uint32 bit32 wrap**. Doubles only; no integer overflow assumption beyond 2^53.
3. Replace bottom-up; re-parse at the end of each function scope.
4. Log every fold `line: before → after` in `ANALYSIS.md` (cap log at 200 entries; summarize beyond).
5. Gate: re-parse + 5 independent spot-checks (evaluate both forms in scratch Luau, must match bit-for-bit).

## Failure protocol

One mismatched spot-check → distrust the pass → revert step, fix evaluator semantics, re-run. Never accept "mostly correct" constant folds; a single wrong constant silently flips a branch.

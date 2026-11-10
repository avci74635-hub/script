---
name: luau-string-decoder
description: Recovers encrypted strings from obfuscated Roblox Luau — string tables with index ciphers (XOR/shift/substitution), string.char arrays, decimal escapes, reversed/gsub-mangled literals — using static analysis and sandbox-isolated decoder execution.
---

# String recovery skill

Read `docs/04-deobfuscation-techniques.md` §B first. Inputs: the target (or current `work/` step). Outputs: rewritten file + mapping table in `ANALYSIS.md`.

## Steps

1. **Locate the cipher.** Search for `local <t> = {` followed within ~200 lines by a function returning from `<t>` (match `return` inside). Confirm it is called with numeric literal args ≥20 times.
2. **Classify the cipher** (XOR / shift / substitution / base-N / reverse+mask). Write a 3-line pseudocode summary in ANALYSIS.md. If you cannot state the algorithm, you are not ready to run anything — re-read the decoder until you can.
3. **Prefer offline reconstruction.** Reimplement the cipher in a scratch file (Python or Lua). Validate it on ONE known-ish string first.
4. **If the cipher resists reading**, sandbox-run the decoder fragment only (`docs/08`): copy the decoder + its table into an isolated file with Roblox globals stubbed; loop `i = 1..#T`, record `{index, plaintext}` to a dump file. Never `loadstring` a payload; blocking `loadstring` in the sandbox is mandatory.
5. **Validate plaintext quality.** If <30% of decoded strings look plausible (English words, dotted instance paths, URLs, Enum names), STOP: wrong cipher or wrong layer → `docs/07` S5.
6. **Rewrite call sites.** AST-aware replacement `d(12)` → `"plaintext"`. Leave non-literal indices for a follow-up unroll decision (see docs/04 §B3 step 4).
7. **Record** the full `index → plaintext` mapping in `ANALYSIS.md` and bump the step file. Re-parse; spot-check 10.

For inline `string.char(...)`/`\ddd` soup, use `python3 tools/decode_chars.py <file> [--write]` — no execution needed.

## Verifier's checklist

- [ ] Re-parse OK
- [ ] Mapping covers every call site that was replaced (no leftover `d(` calls unless intentionally runtime)
- [ ] 10 sampled strings eyeball-plausible
- [ ] New literals contain no raw bytes >0x7E without `\u{...}` escapes (keep file valid UTF-8/ASCII)

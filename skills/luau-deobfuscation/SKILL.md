---
name: luau-deobfuscation
description: Orchestrates the full deobfuscation job on an authorized Roblox Luau script — fingerprint, triage, multi-pass pipeline (strings, constants, dead code, control flow), verification, and report. Use whenever the user asks to analyze, deobfuscate, or understand an obfuscated Lua/Luau Roblox file.
---

# Luau deobfuscation — orchestrator skill

## Preconditon check (always first)

1. Confirm the user's authorization and goal in one line: own code? malware triage? sanctioned audit? If clearly unauthorized (crack a third-party commercial script), refuse that part and offer legitimate alternatives.
2. Confirm the raw file is preserved read-only; all work happens in `work/`.

## Procedure

1. **Fingerprint** — `python3 tools/lscan.py <file>`; write results into `ANALYSIS.md` under `## Fingerprint`. Classify: minified | string-cipher | constant-obfuscated | flattened | VM | layered loader | mixed.
2. **Trap triage** — hand off to skill `luau-trap-triage` if any traps from `docs/05-traps-and-anti-analysis.md` are present. Do not proceed with executon until traps are inventoried.
3. **Peel layers** (if `loadstring`+blob detected): extract decoder, recover payload statically or in the sandbox (`docs/08-dynamic-sandbox.md`), recurse into `work/layerN.lua`.
4. **String recovery** — `luau-string-decoder` skill.
5. **Constant folding** — `luau-constant-folder` skill.
6. **Dead branch elimination** — conservative only; keep unprovable predicates annotated.
7. **Control-flow repair** (if a dispatcher exists) — `luau-cfg-unflatten` skill.
8. **Semantic rename + pretty-print** — neutral names; `ANALYSIS.md` keeps old→new map.
9. **Verify** — gates in `docs/10-verification.md`; record PASS/FAIL per gate.
10. **Report** — `luau-report` skill → `REPORT.md`.

## Non-negotiables

- Never execute the target payload outside the sandbox.
- Re-parse after every pass; on FAIL, revert to last good step (`docs/07-error-playbook.md`) and escalate to the user if one retry also fails.
- No invented names/comments. Tag every reconstruction `[high]`/`[med]`/`[low]`.
- If you are asked to "crack" someone else's licensing/key protection, stop and say why.

## Output contract

`<name>.deob.lua` + `ANALYSIS.md` + `REPORT.md` (or explicit Triage-only verdict with reasons).

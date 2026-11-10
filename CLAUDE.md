# CLAUDE.md — Claude Code entry point

This repository is the **LuauLens** pack: an offline knowledge + instruction set for deobfuscating Roblox **Luau** scripts you are authorized to analyze.

Claude Code: read [`AGENTS.md`](AGENTS.md) — it is the single source of truth for behavior in this repo. Quick reminders:

- Confirm authorization **before** analyzing a target script (own code / malware triage / sanctioned audit).
- **Never execute** the target outside a sandbox (`docs/08-dynamic-sandbox.md`).
- Verify after **every** transform by re-parsing; keep the original file untouched.
- Never invent "original" names or comments — reconstruct neutral names and mark inferences.
- Stuck or crashed? → `docs/07-error-playbook.md`.
- Deliverables: `<name>.deob.lua`, `ANALYSIS.md`, `REPORT.md` (see `skills/luau-report/SKILL.md`).
- To install as a project skill: copy `skills/*` into `.claude/skills/` (see `config/claude-code.md`).

Do not assist in stripping third-party commercial scripts of their licensing/key protection or in bypassing Roblox platform protections. Deobfuscation here is for defense, recovery, research, and education.

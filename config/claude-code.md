# Claude Code integration

## What Claude Code reads automatically

- `CLAUDE.md` at the project root (this repo's version points to `AGENTS.md`, the single source of truth).
- Agent Skills under `.claude/skills/<skill-name>/SKILL.md` (project) or `~/.claude/skills/<skill-name>/SKILL.md` (global). The files in this repo's `skills/` are already in that exact format.

## Setup — project-scoped (recommended)

```bash
cd your-analysis-project
mkdir -p .claude/skills
cp -r /path/to/this/pack/skills/* .claude/skills/
cp /path/to/this/pack/AGENTS.md ./AGENTS.md
# optional: keep docs/ and tools/ available too
cp -r /path/to/this/pack/docs /path/to/this/pack/tools /path/to/this/pack/checklists .
```

Claude Code will list `/luau-deobfuscation`, `/luau-string-decoder`, etc. as available skills.

## Setup — global (all projects)

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/this/pack/skills/* ~/.claude/skills/
```

Keep the knowledge base reachable: global skills can reference absolute paths — edit each `SKILL.md`'s doc references if you move `docs/`, or symlink `~/luaulens/docs`.

## Using it

> /luau-deobfuscation — authorized target: my own obfuscated script at ./target.lua. Produce .deob.lua, ANALYSIS.md, REPORT.md.

## Notes & limits

- Skills are instructions, not magic; Gates in docs/10 still apply.
- For long targets, run passes in separate sessions; `ANALYSIS.md` is the handoff (see docs/07 S9).
- Do not let it `WebFetch` random "deobfuscator" sites; the pack is self-contained on purpose.

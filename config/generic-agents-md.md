# Generic AGENTS.md-aware agents (Cursor, Aider, Windsurf, custom CLIs, …)

Any agent that reads a root instruction file can run this pack. The contract:

1. Put this repo's `AGENTS.md` (or a symlink/copy) at the root of the working directory that contains the target script.
2. Make `docs/` and `tools/` reachable paths (relative or absolute — if you copy instead of symlink, fix nothing; paths in AGENTS.md are relative to repo root).
3. Load `prompts/master-system-prompt.md` as the system prompt if your agent supports one; otherwise start the session with: "Read AGENTS.md and follow it."
4. Skills in `skills/` are plain markdown — any agent can be pointed at one explicitly ("Follow skills/luau-string-decoder/SKILL.md on this file").

## Minimal session kickoff

```
Read AGENTS.md. Authorized target: ./target.lua (my code / malware triage).
Goal: understand behavior + produce .deob.lua if feasible.
Start with tools/lscan.py and report the fingerprint before proposing a plan.
```

## Cursor-specific

Add to `.cursor/rules/luaulens.mdc` (or paste into Project Rules): the `AGENTS.md` content. Keep `docs/` in the repo so `@docs/…` references resolve.

## Aider-specific

`--read AGENTS.md --read docs/02-pipeline.md` and chat instructions as above. Use `/add` for the specific docs per pass.

## What to expect

- Small/medium targets: full pipeline in one session.
- 100 KB+ targets: multiple sessions; `ANALYSIS.md` is the handoff — never rely on chat memory across sessions.
- VM-grade targets: agreement on a Triage-tier deliverable up front saves days of pain.

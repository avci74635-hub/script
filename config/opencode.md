# OpenCode CLI integration

Goal: `opencode` (in any project) automatically behaves as a LuauLens analyst with these docs as its brain.

## 1. Install OpenCode (see opencode.ai for current canonical steps)

```bash
# either the installer
curl -fsSL https://opencode.ai/install | bash
# or via npm (requires Node ≥ 18)
npm i -g opencode-ai
```

## 2. Clone this pack somewhere stable

```bash
git clone https://github.com/avci74635-hub/script.git ~/luaulens
```

## 3a. Simplest: run OpenCode with the pack as project

```bash
cd ~/luaulens
opencode
```

OpenCode auto-discovers `AGENTS.md` at the repo root; `skills/` here follow the `SKILL.md` convention used by the broader agent-skills ecosystem.

## 3b. Use it inside your own project (recommended for real work)

```bash
cd ~/my-analysis-task        # contains target.lua, work/, ANALYSIS.md …
ln -s ~/luaulens/AGENTS.md AGENTS.md      # or copy
ln -s ~/luaulens/docs docs
ln -s ~/luaulens/skills skills
ln -s ~/luaulens/prompts prompts
ln -s ~/luaulens/tools tools
opencode
```

## 3c. Or wire it via opencode config (per project or global)

`opencode.jsonc` (project root) or `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "instructions": [
    "~/luaulens/AGENTS.md",
    "~/luaulens/docs/02-pipeline.md",
    "~/luaulens/docs/05-traps-and-anti-analysis.md"
  ]
}
```

(Exact key names can drift between OpenCode versions — check `opencode --help` / the config docs; the principle "inject AGENTS.md + key docs as instructions" is stable.)

## 4. Model routing (incl. budget models)

- Any capable tool-using model works; for DeepSeek chat-class, also set low temperature (0–0.3) if your provider exposes it, and keep `docs/11-model-tuning.md` in the instructions — it is written for exactly this.
- Suggested env pattern: put `master-system-prompt.md` content as the first instruction, keep `docs/07-error-playbook.md` reachable for crashes.

## 5. First run prompt

> Read AGENTS.md. Fingerprint `target.lua` with tools/lscan.py and tell me the class + suspected traps before proposing any plan. Authorized: my own script.

## Troubleshooting

| Symptom | Fix |
|---|---|
| opencode doesn't see the docs | check cwd; AGENTS.md must be in project root (or symlinked) |
| Model edits the original file | remind it of the provenance rule; restore with `git checkout` if in a git dir |
| Model loops on one region | feed `prompts/error-recovery.md` verbatim |
| Wrong decodes accepted | enforce `skills/luau-string-decoder` verifier checklist |

# LuauLens — Roblox Luau Deobfuscation Skill Pack

**An offline knowledge + instructions pack that turns AI coding agents (OpenCode, Claude Code, Termux, Cursor, and any AGENTS.md-aware CLI) into disciplined Luau deobfuscation analysts.**

This repository contains everything an AI model needs to **read, analyze, and recover the behavior of obfuscated Roblox Luau scripts**: step-by-step pipeline, obfuscation taxonomy, reversal techniques, trap handling, an error-recovery playbook, verification methodology, agent prompts, checklists, and working helper tools.

> Works with small/cheap models too, not only frontier ones — see [`docs/11-model-tuning.md`](docs/11-model-tuning.md) for how to get consistent results from budget models like DeepSeek via decomposition, exemplars, and verification gates.

---

## Authorized use (read this first)

Use this pack to analyze code that is **yours** or that you are **authorized to analyze**:

- Your own scripts that you lost the source for, or that a toolchain mangled.
- Suspected **malicious / backdoored** scripts (e.g. free models, plug-ins, loaders) so you can understand and report what they do.
- Security research, audits, and incident response on experiences you own or moderate.
- Education and interoperability research.

Do **not** use it to steal other developers' protected work, strip licensing/key systems from scripts you have no rights to, or circumvent access controls on services or experiences you don't own. Obfuscated ≠ free to take — obfuscation is a rights marker, not a challenge. Respect Roblox's Terms of Use and applicable law. Nothing here is legal advice.

## Honest limits (so you don't get burned)

- **You recover behavior, not history.** Original variable names, comments, formatting, and file layout are gone after obfuscation. The best possible outcome is semantically equivalent, readable code. Anyone selling "perfect restoration" is selling fiction.
- **VM-protected scripts** (custom-bytecode virtual machines, e.g. Luraph-style) resist full automatic deobfuscation. You typically get: (a) the decryption layers peeled, (b) the VM's fetch/decode/dispatch loop understood, (c) behavior reconstructed via tracing. Full source-level recovery is research-grade and sometimes impossible.
- **Anti-analysis traps** (infinite loops, checksum bombs) are *meant* to be executed only inside a sandbox with instruction limits — see [`docs/05-traps-and-anti-analysis.md`](docs/05-traps-and-anti-analysis.md) and [`docs/08-dynamic-sandbox.md`](docs/08-dynamic-sandbox.md).
- Every deobfuscation pass must be **verified** (parse check + semantic check). A plausible-looking but subtly wrong reconstruction is worse than an honest "partial" one.

## Quickstart

```bash
git clone https://github.com/avci74635-hub/script.git
cd script
```

Pick your agent — full guides in [`config/`](config/):

| Agent / CLI            | How it loads this pack                                        | Guide |
|------------------------|---------------------------------------------------------------|-------|
| OpenCode CLI           | `AGENTS.md` is auto-discovered + `skills/` installed as skills | [config/opencode.md](config/opencode.md) |
| Claude Code            | `CLAUDE.md` auto-loaded; skills in `.claude/skills/`           | [config/claude-code.md](config/claude-code.md) |
| Termux (Android)       | Same pack, Termux install steps                                | [config/termux.md](config/termux.md) |
| Any AGENTS.md-aware CLI| Root `AGENTS.md` + point the agent at `docs/`                  | [config/generic-agents-md.md](config/generic-agents-md.md) |

Then, in the agent, with an obfuscated file in hand:

> "Read AGENTS.md and run the LuauLens pipeline on `sample.lua`. Authorized target: my own script. Follow the skill in `skills/luau-deobfuscation/SKILL.md`."

## The pipeline in one paragraph

**Intake → Fingerprint → Safety triage → Static normalization → String/constant recovery → Control-flow repair → Dead code elimination → Semantic rename → Verification → Report.** An obfuscated file is treated as *evidence*: it is never executed outside a sandbox, every transformation is validated by re-parsing, and the final output is checked for behavioral equivalence (or flagged with the exact points where equivalence could not be proven). Full detail: [`docs/02-pipeline.md`](docs/02-pipeline.md).

## Repository map

```
AGENTS.md                Agent entry point — read first (OpenCode et al. auto-load it)
CLAUDE.md                Claude Code entry point (thin pointer to AGENTS.md)
README.md                You are here
LICENSE                  MIT

docs/                    The knowledge base (numbered, read in order)
  00-overview.md             Scope, goals, non-goals, honest expectations
  01-architecture.md         Blueprint: layers, data flow, agent roles
  02-pipeline.md             The 10-stage deobfuscation pipeline, in detail
  03-obfuscation-taxonomy.md Catalog of techniques + detection signatures
  04-deobfuscation-techniques.md  Reversal methods per technique
  05-traps-and-anti-analysis.md  Infinite loops, checksum bombs, anti-debug…
  06-luau-specifics.md       Luau vs Lua 5.1 gotchas that break naive tools
  07-error-playbook.md       When the agent crashes/loops/gets lost: fixes
  08-dynamic-sandbox.md      Running untrusted code safely (offline, hooked)
  09-tooling.md              Real tools: parsers, formatters, tracers
  10-verification.md         Proving the output still means the same thing
  11-model-tuning.md         Making budget models (e.g. DeepSeek) perform
  12-glossary.md             Terms: CFG, opaque predicate, VM, taint…

skills/                  Agent Skills (SKILL.md) — loadable by Claude Code & friends
  luau-deobfuscation/        Orchestrator skill for the full job
  luau-string-decoder/       String tables & cipher recovery
  luau-constant-folder/      Constant expression folding
  luau-cfg-unflatten/        Control-flow unflattening
  luau-trap-triage/          Recognize & defang anti-analysis traps
  luau-report/               Write the final analyst report

prompts/                 Drop-in prompts (master system prompt, stepwise, error recovery)
checklists/              Human + agent checklists (authorization, triage, delivery)
config/                  Per-agent integration guides (OpenCode, Claude Code, Termux)
tools/                   Working Python 3 stdlib-only utilities (offline, no exec of target)
examples/                Hand-written toy example: obfuscated ↔ deobfuscated + walkthrough
```

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, publish it, sell nothing you don't have rights to.

# 00 — Overview: scope, goals, and honest expectations

## What this pack does

LuauLens teaches an AI agent to **systematically read obfuscated Roblox Luau source** and produce the most faithful possible human-readable reconstruction of it. It covers:

- **Source-level obfuscation** (identifier mangling, string encryption, constant encoding, dead code, opaque predicates, control-flow flattening) — the majority of what you actually meet.
- **Layered loaders** (one obfuscated stub that decrypts and `loadstring`s the next layer) — peel iteratively.
- **VM-protected code** (Luraph-style custom bytecode machines) — peeled as far as practical; see limits.
- **Anti-analysis traps** — recognizing them, and neutralizing them *inside a sandbox* with justification.

## What success looks like

| Verdict | Meaning |
|---|---|
| **Recovered (high confidence)** | Semantically equivalent, readable code. Passes re-parse + behavior probes. |
| **Partial (medium)** | Structure understood; some regions replaced by annotated equivalents (e.g. a VM dispatch loop left in place with explanation). |
| **Triage-only (low)** | Cannot safely reconstruct; but behavior documented (network calls, data written, loops, requires) with evidence. |

Any tier is a valid deliverable if reported honestly. **A confident wrong reconstruction is failure.**

## Non-goals

- **Not** a tool for defeating third-party commercial licensing/key systems.
- **Not** a Roblox exploit/executor development kit. Nothing here helps inject into the client or bypass platform anti-cheat.
- **Not** malware for Roblox; it analyzes it.
- **Not** a guarantee of perfect source recovery — impossible in general (see architecture, threat model).

## Why obfuscation resists reversal (the threat model in one paragraph)

Obfuscators apply *information-destroying* transforms to make the deobfuscator do exponential work: names are replaced by noise, strings are encrypted behind a cipher whose key is embedded in the code, constants become arithmetic expressions, straight-line code becomes a state machine, and traps detonate if you "step wrong." Every recovery technique in this pack is about **localizing entropy** (find the few bits of actual information: the cipher, the state table, the predicate truth values) and **re-executing or rewriting it safely**. If the obfuscator is well-built and VM-based, the information required to perfectly invert it simply isn't present at the source level — hence tracing and behavioral recovery.

## How to read these docs

Read `01-architecture.md` (how the pieces fit) and `02-pipeline.md` (what to do, in order) before any hands-on work. `03` and `04` are the reference catalog; `05` and `08` are safety-critical; `06` keeps you from breaking on Luau quirks; `07` is your crash recovery manual; `10` defines "done"; `11` is for tuning weaker models.

---
name: luau-report
description: Writes the final analyst report (REPORT.md) for a deobfuscation job — behavior summary, structure map, risk register, confidence per region, and explicit residual-risk list — in plain language for a human reviewer.
---

# Report writing skill

The report is the deliverable that makes the work auditable. No report → task not done. Write for a technical human who will **not** read `ANALYSIS.md` unless they have to.

## Template (fill, don't omit)

```markdown
# REPORT — <file> deobfuscation
Date / target hash / authorization basis / goal

## TL;DR (≤5 lines)
What the script is, what it does, verdict tier (High/Medium/Triage).

## Structure map
Bulleted outline: top-level functions and their roles (inferred), entry point, layers peeled.

## Behavior
- What it reads (services, remotes, assets)
- What it does (network calls with URLs, data written, UI, loops)
- Side effects with line references into the .deob.lua

## Risk register
| id | finding | severity | evidence (line) |
(Remote URLs, exfiltration shapes, credential-looking strings, persistence, self-destruct/trap locations)

## Traps found & handling
Table from trap triage: id, category, where, how handled (kept/neutralized-in-sandbox/annotated).

## Confidence ledger
Region → [high]/[med]/[low] + one-line why. Counts per tier.

## Residual risks / not done
Explicit list of unverified claims and why (VM arms, unresolvable edges, opaque constants).

## Provenance & ethics
Original hash, tools used, transformations applied (pointer to ANALYSIS.md). Authorized-use reminder + no-distribution note for third-party protected code.
```

## Rules

- Every behavioral claim cites a line in the reconstruction or a tool log. No vibe-claims.
- If the script is benign, say so plainly; if it's malicious, say what it does concretely, minus weaponizable detail you invented (stick to evidence).
- Never fabricate original authorship, comments, or variable names. Everything inferred is labeled inferred.

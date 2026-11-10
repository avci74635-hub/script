---
name: luau-trap-triage
description: Inventories anti-analysis traps in obfuscated Luau (infinite loops, checksum self-reads, anti-debug probes, timing bombs, pcall bombs, select-eager-eval, environment sniffing) and decides per-trap handling — keep, neutralize in sandbox only, or annotate — with a mandatory written inventory.
---

# Trap triage skill

Read `docs/05-traps-and-anti-analysis.md` completely before touching anything.

## Steps

1. **Scan** for trap signatures: `while true do end` (empty body), `string.dump`, `debug.getinfo`, `getfenv`, `hookfunction`, `getrawmetatable`, `tick()`/`os.clock()` paired with punitive branches, `pcall(function() … end)` containing loops, `select(` with more than 4 args where some args are loops/traps.
2. **Inventory** into `ANALYSIS.md` table: `id | line | category | trigger | blast radius | decision`.
3. **Decide** per trap:
   - **Keep** — harmless to analysis (e.g. env sniffing you simply won't exercise).
   - **Neutralize in sandbox only** — replace guard with forced value in the *sandbox copy*, log `TRAP-NEUTRALIZED <id>`. The on-disk deliverable stays faithful or carries explicit annotations; it is never a distributed crack.
   - **Annotate only** — if neutralizing would destroy the analysis value (e.g. the trap IS the behavior), keep it, mark `[low]`, explain in REPORT.md.
4. **Capability check:** any remaining executable region must have a documented instruction/trip cap. If you cannot cap it, you cannot run it — analysis stays static for that region.
5. **Hand back** to orchestrator with the inventory attached. Execution beyond decoder isolation requires trap triage COMPLETE.

## Red lines

- Never produce a general-purpose anti-tamper bypass for a named third-party product.
- Never claim a tampered game/experience's protection "doesn't work" as a deliverable.
- Triage output = understanding, not weaponization.

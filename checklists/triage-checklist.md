# Triage checklist (first 10 minutes)

- [ ] `file target.lua` + hexdump first 16 bytes — confirm text vs bytecode (`\27Lua`)
- [ ] Size, line count, SHA-256 recorded
- [ ] `python3 tools/lscan.py target.lua` saved to ANALYSIS.md
- [ ] `python3 tools/extract_strings.py target.lua` skimmed (URLs? paths? Enum-ish tokens?)
- [ ] Classification chosen: minified / string-cipher / constant / flattened / VM / layered / mixed
- [ ] Trap scan: empty-body `while true do end`, `string.dump`, `debug.`, `tick()` near branches, `select(` wide calls — inventoried
- [ ] Network indicators listed separately: every URL, RemoteEvent/Function name, `require` id
- [ ] Authorization checklist linked
- [ ] Plan of passes + gates drafted (prompts/stepwise-decompose.md) and approved by user if stakes are high

# Pre-delivery checklist

- [ ] `REPORT.md` exists with all template sections (no omissions)
- [ ] Verdict tier stated: High / Medium / Triage — matches the confidence ledger counts
- [ ] Residual-risk list explicit (empty list = you didn't look hard enough; expect at least one unknown)
- [ ] Header comment in `.deob.lua`: tool, date, original SHA-256, tier counts
- [ ] No invented provenance; inferred names marked
- [ ] Network/exfil indicators listed with line refs
- [ ] Traps described, not "fixed" silently; neutralizations confined to sandbox artifacts and logged
- [ ] User informed of authorized-use scope for the output (no redistribution of third-party protected code)
- [ ] Artifacts named consistently: `<name>.deob.lua`, `ANALYSIS.md`, `REPORT.md`

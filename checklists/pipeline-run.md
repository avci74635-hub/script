# Pipeline run checklist

One box per pass; every box needs evidence in ANALYSIS.md.

- [ ] Pass 3 normalize: parses / deferred-to-Stage-4 (blob)
- [ ] Pass 4 layers: layer count = __, payload reached: yes/no
- [ ] Pass 5 strings: mapping entries = __, spot-checks 10/10 plausible
- [ ] Pass 6 constants: folds logged = __, 5 spot-checks match
- [ ] Pass 7 dead branches: removals logged = __, each with proof; unprovable predicates kept+annotated
- [ ] Pass 8 control flow: applied / not needed / stopped(reason)
- [ ] Pass 9 rename+fmt: map complete, header present, file re-parses
- [ ] Every gate result recorded as PASS/FAIL
- [ ] work/ contains step files; originals untouched

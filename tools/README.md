# tools/

Offline, Python 3 stdlib-only utilities. They never execute the target and never touch the network. See `docs/09-tooling.md` for what fits where, and `examples/` for a practice target.

| Tool | Purpose |
|---|---|
| `lscan.py` | Fingerprint (Stage 1): size/hash, identifier stats, marker counts, rough block balance |
| `extract_strings.py` | List literals (Stage 5 triage): offsets, lengths, duplicates, light escape decoding |
| `decode_chars.py` | Mechanically decode `string.char(...)` and `\ddd` escapes (Stage 5), dry-run by default |
| `luaulens_walk.py` | Shared comment/string-aware source walker used by the other three |

All support `--help`. `decode_chars.py --write` emits a `.decoded` sibling; originals are never modified.

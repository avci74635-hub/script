#!/usr/bin/env python3
"""extract_strings.py — list string literals in a (possibly obfuscated) file.

Never executes the target. Comment/string-aware walker; escapes are shown
lightly decoded for readability. --min filters short noise, --dupes shows
only repeated literals, --json for machine-readable output.

Usage: python3 extract_strings.py <file> [--min N] [--dupes] [--json]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from luaulens_walk import walk

ESC_RE = re.compile(r"\\(\d{1,3}|x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|n|r|t|\\|\"|')")

def decode_escapes(body: str) -> str:
    def repl(m: re.Match) -> str:
        e = m.group(1)
        if e.isdigit():
            return chr(int(e, 10) & 0xFF)
        if e.startswith("x"):
            return chr(int(e[1:], 16))
        if e.startswith("u{"):
            try:
                return chr(int(e[2:-1], 16))
            except ValueError:
                return m.group(0)
        return {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "'": "'"}.get(e, m.group(0))
    return ESC_RE.sub(repl, body)

def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = args[0]
    min_len = 0
    if "--min" in args:
        min_len = int(args[args.index("--min") + 1])
    dupes_only = "--dupes" in args
    as_json = "--json" in args

    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"error: {e}")
        return 1

    _, literals = walk(text)
    items = []
    counts: dict[str, int] = {}
    for off, raw in literals:
        if raw.startswith("[[") or raw.startswith("[="):
            # long-bracket string: strip [[ ]] / [=*[ ]=*]
            m = re.match(r"\[(=*)\[(.*)\]\1\]\s*$", raw, re.S)
            body = m.group(2) if m else raw
            decoded = body
        else:
            body = raw[1:-1]
            decoded = decode_escapes(body)
        counts[decoded] = counts.get(decoded, 0) + 1
        items.append((off, decoded))

    if dupes_only:
        items = [(o, d) for (o, d) in items if counts[d] > 1]
    items = [(o, d) for (o, d) in items if len(d) >= min_len]

    if as_json:
        print(json.dumps([{"offset": o, "text": d, "count": counts[d]} for o, d in items],
                         ensure_ascii=False, indent=1))
        return 0

    for i, (o, d) in enumerate(items):
        preview = d if len(d) <= 100 else d[:100] + f"…(+{len(d)-100} chars)"
        preview = preview.replace("\n", "\\n").replace("\r", "\\r")
        flag = f" x{counts[d]}" if counts[d] > 1 else ""
        print(f"[{i:4d}] off={o:<7d} len={len(d):<5d}{flag}  {preview}")
    print(f"\ntotal shown: {len(items)} (file has {len(counts)} unique literals)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

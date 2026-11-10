#!/usr/bin/env python3
"""decode_chars.py — decode inline encoded characters without executing anything.

Handles two common obfuscator constructs, comment/string-aware:

  1. string.char(104, 101, 108, 108, 111)      ->  "hello"
  2. "\\104\\101\\108\\108\\111"  (decimal escapes)  ->  "hello"   (--escapes)

Safety: never runs the target. With --write it writes a sibling
`<name>.decoded<ext>`; the original is never modified.

Usage:
  python3 decode_chars.py <file>                 # report only (no writes)
  python3 decode_chars.py <file> --write         # emit .decoded sibling
  python3 decode_chars.py <file> --escapes       # also decode \\ddd inside literals
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from luaulens_walk import walk

CHAR_CALL_RE = re.compile(r"string\.char\(\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)\s*\)")
DEC_ESC_RE = re.compile(r"\\(\d{1,3})")

def printable(s: str) -> bool:
    return all(32 <= ord(c) < 127 or c in "\n\r\t" for c in s)

def lua_escape(s: str) -> str:
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append(f"\\{ord(ch)}")
    return '"' + "".join(out) + '"'

def apply_edits(text: str, edits):
    """Apply (start, end, repl) edits; must not overlap. Applies from the end."""
    for start, end, repl in sorted(edits, key=lambda e: e[0], reverse=True):
        text = text[:start] + repl + text[end:]
    return text

def decode_char_calls(text: str):
    mask, _ = walk(text)
    hits, edits = [], []
    for m in CHAR_CALL_RE.finditer(text):
        if not mask[m.start()]:
            continue  # inside a string or comment — leave untouched
        codes = [int(x) for x in m.group(1).split(",")]
        if any(c > 255 for c in codes):
            hits.append((m.start(), m.group(0), None))
            continue
        s = "".join(chr(c) for c in codes)
        hits.append((m.start(), m.group(0), s))
        if printable(s):
            edits.append((m.start(), m.end(), lua_escape(s)))
    return apply_edits(text, edits), hits

def decode_decimal_escapes(text: str):
    _, literals = walk(text)
    hits, edits = [], []
    for off, raw in literals:
        if not raw.startswith('"'):
            continue  # double-quoted only (byte semantics)
        body = raw[1:-1]
        changed = False
        def esub(em):
            nonlocal changed
            v = int(em.group(1), 10)
            if v > 255:
                return em.group(0)
            changed = True
            return chr(v)
        decoded_body = DEC_ESC_RE.sub(esub, body)
        if changed:
            new_lit = '"' + decoded_body.replace("\\", "\\\\").replace('"', '\\"') + '"'
            edits.append((off, off + len(raw), new_lit))
            hits.append((off, raw, decoded_body))
    return apply_edits(text, edits), hits

def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = args[0]
    write = "--write" in args
    also_escapes = "--escapes" in args

    try:
        raw = open(path, "rb").read()
    except OSError as e:
        print(f"error: {e}")
        return 1
    text = raw.decode("utf-8", errors="surrogateescape")

    if also_escapes:
        text, hits2 = decode_decimal_escapes(text)
        print(f"\\ddd-escape literals decoded: {len(hits2)}")
        for off, orig, dec in hits2[:25]:
            print(f"  off={off:<8} {orig[:60]!r:64} -> {dec[:60]!r}")
        if len(hits2) > 25:
            print(f"  … and {len(hits2) - 25} more")

    text, hits1 = decode_char_calls(text)
    print(f"string.char(...) sites: {len(hits1)}")
    for off, orig, dec in hits1[:25]:
        shown = repr(dec) if dec is not None else "(skipped: code > 255)"
        print(f"  off={off:<8} {orig[:60]!r:64} -> {shown}")
    if len(hits1) > 25:
        print(f"  … and {len(hits1) - 25} more")

    if write:
        if "." in path.rsplit("/", 1)[-1]:
            stem, ext = path.rsplit(".", 1)
            out = f"{stem}.decoded.{ext}"
        else:
            out = path + ".decoded"
        open(out, "wb").write(text.encode("utf-8", errors="surrogateescape"))
        print(f"\nwrote {out} (original untouched)")
    else:
        print("\ndry run — no files written. Pass --write to emit a .decoded sibling.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

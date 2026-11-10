#!/usr/bin/env python3
"""lscan.py — offline fingerprint of a suspicious/obfuscated Luau/Lua file.

Text-level heuristics only. Never executes the target. Reports the facts an
analyst needs to route the pipeline (see docs/02-pipeline.md, Stage 1).

Usage: python3 lscan.py <file>
"""
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from luaulens_walk import walk, code_only

MARKERS = [
    ("string.char(", "char-array string building (B2/B6)"),
    ("loadstring", "layered loader candidate (F1)"),
    ("getfenv", "environment manipulation (G1)"),
    ("setfenv", "environment manipulation (G1)"),
    ("debug.", "anti-analysis probe (G3)"),
    ("string.dump", "checksum trap candidate (T2)"),
    ("hookfunction", "executor-environment sniffing (T8)"),
    ("getrawmetatable", "metatable sniffing (T8)"),
    ("game:HttpGet", "network fetch (F2)"),
    ("HttpService", "network service (F2)"),
    ("pcall(", "pcall usage (D5/T5)"),
    ("while true do", "dispatcher/loop marker (D3)"),
    ("select(", "eager-eval dispatch candidate (D4/T7)"),
    ("setclipboard", "executor-side IO marker"),
    ("\x1bLua", "PUC-Lua bytecode magic"),
    ("\x1bLuau", "Luau bytecode magic"),
]

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
BLOCK_OPEN_RE = re.compile(r"\b(function|if|for|while|repeat)\b")
BLOCK_CLOSE_RE = re.compile(r"\b(end|until)\b")

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    try:
        raw = open(path, "rb").read()
    except OSError as e:
        print(f"error: cannot read {path}: {e}")
        return 1

    print("=== LuauLens fingerprint ===")
    print(f"file:        {path}")
    print(f"bytes:       {len(raw)}")
    print(f"sha256:      {hashlib.sha256(raw).hexdigest()}")
    if raw[:4] == b"\x1bLua":
        print("!! bytecode magic detected — this is NOT source. See docs/07 S4.")
        return 1

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    mask, literals = walk(text)
    code = code_only(text)  # strings/comments blanked; newlines preserved
    print(f"lines:       {len(lines)}")
    print(f"max line len:{max((len(l) for l in lines), default=0)}")
    if len(lines) <= 3 and len(raw) > 5000:
        print("shape:       single-line minified blob (Stage 3 formatting applies)")

    non_ascii = sum(1 for ch in text if ord(ch) > 126)
    print(f"non-ascii chars: {non_ascii}" + ("  (possible Cyrillic lookalikes A3)" if non_ascii > 50 else ""))

    idents = IDENT_RE.findall(code)
    if idents:
        lens = [len(i) for i in idents]
        n = len(lens)
        over32 = sum(1 for l in lens if l > 32)
        le2 = sum(1 for l in lens if l <= 2)
        avg = sum(lens) / n
        print(f"identifiers: {n} total | avg len {avg:.1f} | <=2ch: {le2/n:.0%} | >32ch: {over32/n:.0%}")
        if over32 / n > 0.3:
            print("signature:   A2-style mangled identifiers (>30% are >32 chars)")
    else:
        print("identifiers: none — not parseable Lua text?")

    strings = [lit for (_, lit) in literals]
    print(f"string literals (walker): {len(strings)}")

    print("\n=== marker counts ===")
    for needle, note in MARKERS:
        count = text.count(needle)
        if count:
            print(f"{count:6d}  {needle:<16} — {note}")

    opens = len(BLOCK_OPEN_RE.findall(code))
    closes = len(BLOCK_CLOSE_RE.findall(code))
    print(f"\nblock keyword balance (rough): opens={opens} closes={closes} "
          f"({'ok' if opens == closes else 'MISMATCH — unterminated or string/comment pollution; verify with a real parser'})")
    print("\nnotes: text-level only. Confirm with a Luau-aware parse before transforming (docs/06).")
    return 0

if __name__ == "__main__":
    sys.exit(main())

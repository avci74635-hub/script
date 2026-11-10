#!/usr/bin/env python3
"""luaulens_walk.py — shared tiny Lua/Luau source walker (stdlib only).

Produces a "code mask": 1 for real code bytes, 0 inside comments and strings.
Also yields the string literal tokens found in code regions. Single pass,
no regex guessing, no execution of target.

Imported by the other tools; not pretty, but correct enough for triage.
"""

def long_bracket_open(text, i):
    """If text[i] == '[' starts a long bracket ([[, [=[, ...), return (level, content_start)."""
    if i >= len(text) or text[i] != '[':
        return None
    j = i + 1
    level = 0
    while j < len(text) and text[j] == '=':
        level += 1
        j += 1
    if j < len(text) and text[j] == '[':
        return level, j + 1
    return None

def long_bracket_close(text, start, level):
    closer = ']' + '=' * level + ']'
    idx = text.find(closer, start)
    return len(text) if idx == -1 else idx + len(closer)

def walk(text):
    """Return (mask bytearray, literals list[(start, raw_with_quotes)])."""
    n = len(text)
    mask = bytearray(b'\x01') * n
    literals = []
    i = 0
    while i < n:
        c = text[i]
        # line comment or block comment
        if text.startswith('--', i):
            lb = long_bracket_open(text, i + 2)
            if lb is not None:
                level, content_start = lb
                end = long_bracket_close(text, content_start, level)
            else:
                end = text.find('\n', i)
                if end == -1:
                    end = n
            for k in range(i, end):
                mask[k] = 0
            i = end
            continue
        # long string
        lb = long_bracket_open(text, i) if c == '[' else None
        if lb is not None:
            level, content_start = lb
            end = long_bracket_close(text, content_start, level)
            literals.append((i, text[i:end]))
            for k in range(i, end):
                mask[k] = 0
            i = end
            continue
        # quoted string
        if c == '"' or c == "'":
            q = c
            j = i + 1
            while j < n:
                if text[j] == '\\':
                    j = min(j + 2, n)
                    continue
                if text[j] == q:
                    j += 1
                    break
                if text[j] == '\n':      # unterminated; stop at EOL
                    break
                j += 1
            literals.append((i, text[i:j]))
            for k in range(i, j):
                mask[k] = 0
            i = j
            continue
        i += 1
    return mask, literals


def code_only(text):
    """Return text with comments/strings blanked to spaces (newlines kept)."""
    mask, _ = walk(text)
    return ''.join(ch if mask[k] else ('\n' if ch == '\n' else ' ')
                   for k, ch in enumerate(text))

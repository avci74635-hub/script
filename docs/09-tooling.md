# 09 — Tooling (real, with what it's actually good for)

No cargo cult: every entry lists *where it fits*, not just that it exists.

## This repo (offline, Python 3 stdlib only)

| Tool | What it does | Limits |
|---|---|---|
| `tools/lscan.py` | Fingerprint: size, ident stats, marker counts (string.char, pcall, loadstring, while-true), non-ASCII scan | Text-level only; no AST claims |
| `tools/extract_strings.py` | Pull all string literals; report long/duplicated/suspicious ones | Regex-lite; escapes shown decoded where trivial |
| `tools/decode_chars.py` | Decode `string.char(…)` chains and `\ddd` escapes to text; EXPLAIN mode shows the mapping | ASCII/UTF-8 output; ambiguous escapes left as-is |

Run any with `--help`. They never execute the target and never touch the network.

## External (optional, heavier)

| Tool | Fits | Notes / cautions |
|---|---|---|
| `luau` CLI (Roblox's open-source Luau) | Fast re-parse checks of *your own test snippets*, not the payload | Install per luau-lang/luau releases for your OS; Termux: build from source or use Linux binary if it runs |
| StyLua | Pretty-printing a **parseable** file | If it errors, file isn't valid Luau — that's information |
| tree-sitter + community Lua/Luau grammar | AST queries (find dispatcher, string tables) | Grammars vary in Luau coverage; Luau type annotations may need a pre-strip |
| Python `luaparser` | AST for Lua (not Luau) — use after annotation stripping | `pip install luaparser`; 5.1/5.3 dialect differences apply to `%`, `//` (absent), etc. |
| `lua5.1` / `lua5.3` | Running **your own** reimplemented decoders/checkers | Not for running the payload |
| `luajit -bl` | Disassembling **LuaJIT** bytecode | Does **not** disassemble Luau bytecode |
| `unluac` | Decompiling **PUC Lua 5.1** bytecode | Does **not** understand Luau bytecode — a target with Luau bytecode headers needs VM-level work (docs/04-F3) |
| `luac -l` | Listing **PUC Lua** bytecode | Same caveat |
| Ghidra / IDA / Binary Ninja | Not for source-level Luau obfuscation | Useful only if the payload embeds native code (rare) |
| `tcpdump` / Wireshark | Offline capture in the sandbox of your own hosts | Never third-party hosts; see docs/08 |
| CyberChef (local instance) | Ad-hoc base64/hex/XOR experiments while reading ciphers | Run locally, offline |

## Deliberately NOT recommended

- "Roblox decompiler online" websites / pastebins that ask you to upload the script — you're handing someone else's protected source to a third party. Local tools only.
- Executing the payload in Roblox Studio "to see what it does" — Studio runs real APIs; that's a live detonation with extra steps.
- Auto-"deobfuscator" executors that claim one-click restoration — they are usually wrappers around the same techniques in this pack, plus their own telemetry.

## Choosing a stack

- **Quick triage (5 min):** `lscan.py` + `extract_strings.py` + eyeballs.
- **String-cipher target:** decoder isolation in sandbox (docs/08) + `decode_chars.py` for inline arrays.
- **Flattened target:** AST (tree-sitter/luaparser) + hand-guided §D3 rewrite. No reliable push-button flattener exists for Luau.
- **VM target:** tracing (docs/04-F3/08). Budget days, not minutes; deliverable is a spec.

## Requirements file

`tools/requirements.txt` is intentionally empty (stdlib only). If you add `luaparser`, add it there with a comment so Termux users know it needs pip.

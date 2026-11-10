# 08 — Dynamic analysis sandbox

Static analysis is the default. When you must execute a *decoder* or *probe behavior*, do it here — never in an executor, never in your real Roblox session, never with network access.

## Hard requirements

1. **Disposable environment:** a VM, container, or at minimum a separate OS user with no Roblox cookies, no SSH keys, no `gh` tokens. The sandbox must be able to die without collateral damage.
2. **No network:** block egress at the VM/container firewall, or run with the interface down. Allow only loopback if the tool needs it. The F2 pattern (remote payload) exists precisely to catch you here — the answer is always "no fetch."
3. **Interpreter you control:** `luau` CLI (Roblox's open-source Luau) if it runs in your environment, or `lua5.1` with compatibility shims (`bit32`, missing stdlib bits). For decoder emulation you usually don't need Roblox APIs at all — you stub them.
4. **Resource caps:** CPU time limit, instruction/trip counter (hard abort at e.g. 1e7), memory cap, output size cap. One `while true do end` must cost you seconds, not an hour.
5. **No credentials in the sandbox.** No `GH_TOKEN`, no Roblox login, no `.netrc`.

## Reference sandbox skeleton (Lua/Luau)

```lua
-- sandbox.lua — run: lua5.1 sandbox.lua target_decoder.lua
local INSTRUCTION_BUDGET = 1e7
local ticks = 0
-- crude trip counter: wrap the global loop by limiting via debug or by static rewrite
-- (document which you did)

-- Stub every Roblox-ish global the target may reference
local calls = {}   -- recorded calls for the report
local function rec(kind) return function(...) table.insert(calls, {kind, ...}) end end
game = {
  GetService = function(_, name) return setmetatable({}, {__index = function() return rec("game."..name) end}) end,
  HttpGet = rec("game:HttpGet"),         -- records, does NOT fetch
  PlaceId = 0000000,
}
Instance = newproxy and setmetatable({}, {__in = function() return rec("Instance") end}) or {}
script = { Parent = nil }
shared, _G = {}, {}
require = rec("require")
loadstring = function(_) error("loadstring blocked in sandbox") end
tick, os = setmetatable({clock = function() return 0 end}, {__index = os}), os  -- frozen-ish clock

-- Load ONLY the decoder fragment you extracted (pipeline Stage 4/5), never the payload wholesale.
-- local decoder = assert(loadfile("decoder_fragment.lua"))
-- print(decoder())  -- prints/returns the materialized strings

-- Dump the call log for REPORT.md
for i, c in ipairs(calls) do print(i, c[1]) end
```

Prefer improving the stubs over loosening the caps. If the target refuses to run without real Roblox, that's a finding, not an invitation.

## Instrumented tracing (for VM'd code, docs/04-F3)

Goal: log `(pc, op, sp_top_value)` per dispatch iteration.

1. Extract the VM main loop.
2. Duplicate it with logging inserted at the dispatch point (manual edit of the copy in `work/`, never the original).
3. Run with stubbed globals + instruction cap.
4. Turn the trace into: opcode histogram → per-opcode handler understanding → disassembly listing.

## Network observation (optional, offline capture only)

If the user controls the infrastructure being contacted (their own server), packet capture in the sandbox (tcpdump/wireshark offline) can corroborate what a suspicious script tries to send. Never against third-party hosts. See `config/` for nothing special — OS tooling suffices.

## What the sandbox may never contain

- Real Roblox login/session.
- The user's Discord/GitHub tokens, `git config` credentials, SSH keys.
- Outbound network, ever, for unknown URLs.
- `setclipboard`-style bridges into the host (Termux:evil-savvy aside — keep it isolated).

## After the run

Delete the sandbox or roll back the snapshot. Nothing the target wrote persists. Record in `ANALYSIS.md`: interpreter, stubs used, caps, outcome, and every neutralized trap with location.

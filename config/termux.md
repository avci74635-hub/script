# Termux (Android) setup

Run the whole pack from your phone — useful for triage in the field (e.g. inspecting a suspicious free-model payload someone sent you). Analysis only; never execute payloads on-device.

## 1. Termux basics

```bash
pkg update && pkg upgrade -y
pkg install -y git python nodejs
```

## 2. OpenCode on Termux

```bash
npm i -g opencode-ai
opencode --version
```

If the npm global bin dir isn't on PATH: `export PATH="$PATH:$(npm prefix -g)/bin"` and persist it in `~/.bashrc`.

## 3. Get the pack and an isolated work area

```bash
git clone https://github.com/avci74635-hub/script.git ~/luaulens
mkdir -p ~/analysis/work && cd ~/analysis
cp ~/luaulens/AGENTS.md .
# point your agent at the pack explicitly, e.g. in opencode instructions:
#   "instructions": ["~/luaulens/AGENTS.md", "~/luaulens/docs/07-error-playbook.md"]
```

## 4. Using the tools

```bash
python3 ~/luaulens/tools/lscan.py target.lua
python3 ~/luaulens/tools/extract_strings.py target.lua | head -50
python3 ~/luaulens/tools/decode_chars.py target.lua
```

Pure stdlib — no pip install needed. For Luau-aware parsing on-device, prefer reviewing statically; Termux Lua interpreters work for *your own* scratch decoders (`pkg install lua54`), not for running the payload.

## 5. Termux-specific cautions

- Phone sandboxes are weak: do **not** `termux-setup-storage` grant the target access to shared storage; work inside `~/analysis`.
- Battery/thermal limits: big files + long Traces will heat the phone — keep passes small; this pack's decomposition does that by design.
- Never paste a suspicious script into an executor "to test it" on Android.

## 6. Offline mode

Everything except the agent's own model calls works fully offline. Airplane mode + the pack = full static analysis capability.

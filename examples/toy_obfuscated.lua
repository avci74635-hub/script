-- examples/toy_obfuscated.lua
-- HAND-WRITTEN TOY for teaching the pipeline. NOT real-world-strength, and not
-- anyone's protected code — it exists so you can practice Stages 5–9 safely.
-- Goal of the walkthrough: recover what this does without running it "for real".

local t = {[1] = {104, 101, 108, 108, 111}, [2] = {32, 119, 111, 114, 108, 100}}
local function d(i)
	local a = t[i]
	local s = ""
	for j = 1, #a do
		s = s .. string.char(a[j])
	end
	return s
end

local A = (0x12 * 4 + 7)   -- 79
local B = (0x8 * 5)        -- 40
local C = A - B            -- 39

if (C * C) >= 0 then       -- opaque predicate: x*x is never negative
	print(d(1) .. " " .. d(2))
else
	print("never runs — dead branch")
end

local K = string.char(67, 111, 110, 102, 105, 103)  -- config marker, inline
print(K)

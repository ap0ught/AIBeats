-- TOWER1 probe (FCEUX): play the 1P TAS and find the code that writes the vertical camera $0089 in Level 12.
local out = io.open("logs/fix/tw1_hook_fceux.txt", "w")
emu.speedmode("maximum")
local seen = {}
local f = 0
local hooked = false
local function onw()
  local pc = memory.getregister("pc")
  local key = string.format("%04X", pc)
  if not seen[key] then
    seen[key] = 0
    local t = {}
    for a = pc - 160, pc + 96 do t[#t+1] = string.format("%02X", memory.readbyte(a)) end
    out:write(string.format("PC %s frame %d bytes[pc-160..pc+96]: %s\n", key, f, table.concat(t, " ")))
  end
  seen[key] = seen[key] + 1
end
while true do
  emu.frameadvance(); f = f + 1
  if f == 70500 and not hooked then memory.registerwrite(0x0089, 1, onw); hooked = true end
  if f >= 71300 then
    for k, v in pairs(seen) do out:write(k .. " count " .. v .. "\n") end
    out:close(); emu.exit()
  end
end

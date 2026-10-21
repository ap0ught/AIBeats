-- FCEUX: play the 1-player TAS (#5093) and dump the 2 KB RAM + pad every frame over the end of Terra Tubes
-- (staircase top, bugs 0x74, descent, floor, duck corridor, end): frames 59150..60960.  -> logs/fix/heli_tas1p_ram.txt
local out = io.open("logs/fix/heli_tas1p_ram.txt", "w")
emu.speedmode("maximum")
local f = 0
while true do
  emu.frameadvance(); f = f + 1
  if f >= 59150 and f <= 60960 then
    local t = {}
    for a = 0, 0x7FF do t[#t+1] = string.format("%02x", memory.readbyte(a)) end
    local j = joypad.get(1); local b = ""
    for _, k in ipairs({"right","left","down","up","start","select","B","A"}) do b = b .. (j[k] and k:sub(1,1) or ".") end
    out:write(string.format("f%d %s %s\n", f, b, table.concat(t)))
  end
  if f > 60960 then out:close(); emu.exit() end
end

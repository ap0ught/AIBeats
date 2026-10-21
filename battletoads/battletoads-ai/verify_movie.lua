-- usage (from the BizHawk folder):
--   EmuHawk.exe --lua=verify_movie.lua --userdata=frames:46752;out:end.ram --movie=run/battletoads_ai_12m23s.bk2 "Battletoads (USA).nes"
--   then: sha1 of end.ram should be e2a1d2dc9d5933e2b18bba0b0d5021ad617dac52
-- plays the loaded movie untouched (no joypad calls), then writes RAM at the given frame and quits
local target = tonumber(userdata.get("frames") or "0")
local out = userdata.get("out")
client.speedmode(6400)
client.unpause()
while emu.framecount() < target do emu.frameadvance() end
local f = io.open(out, "wb")
local ram = memory.read_bytes_as_array(0, 0x800, "RAM")
for i = 1, #ram do f:write(string.char(ram[i])) end
f:close()
client.exit()

MASKS = [[G:/AI World Record/Ninja Gaiden/work/fastcore/out/full1.masks]]
OUT = [[G:/AI World Record/Ninja Gaiden/work/fastcore/out/full1.bin]]
IOFF = 1
RAMINIT = "nes"
FULLRAM = false
NFRAMES = 39084
-- generated parameters are prepended: MASKS (path), OUT (path), IOFF, RAMINIT ("nes"|"none"), FULLRAM (bool), NFRAMES
local masks = {}
do
  local f = io.open(MASKS, "rb"); local d = f:read("*a"); f:close()
  for i = 1, #d do masks[i] = d:byte(i) end
end
local FIELDS = {42,41,30,96,97,98,99,100,101,102,109,110,118,119,128,132,133,134,135,137,138,139,140,149,80,81,82,172,173,190,191,201,208,1208,51,45,76,509,1175,111,115,771,62}
local out = io.open(OUT, "wb")
local fullout = FULLRAM and io.open(OUT .. ".ram", "wb") or nil
local RAM = emu.memType.nesInternalRam
local polls, frames, reads = 0, 0, 0
local cur = 0
local function setpad(m)
  emu.setInput({a = (m & 0x80) ~= 0, b = (m & 0x40) ~= 0, select = (m & 0x20) ~= 0, start = (m & 0x10) ~= 0,
                up = (m & 0x08) ~= 0, down = (m & 0x04) ~= 0, left = (m & 0x02) ~= 0, right = (m & 0x01) ~= 0}, 0, 0)
end
if RAMINIT == "nes" then
  local done = false
  emu.addMemoryCallback(function()
    if done then return end
    done = true
    for a = 0, 0x7FF do emu.write(a, ((a & 4) ~= 0) and 0xFF or 0x00, RAM) end
  end, emu.callbackType.exec, 0xFFDA)
end
local rbits = 0
emu.addMemoryCallback(function(addr, value) reads = reads + 1; rbits = ((rbits << 1) | (value & 1)) & 0xFFFFFFFF end, emu.callbackType.read, 0x4016)
emu.addEventCallback(function()
  polls = polls + 1
  local k = polls + IOFF
  cur = masks[k] or 0
  setpad(cur)
end, emu.eventType.inputPolled)
local t0 = os.clock()
emu.addEventCallback(function()
  frames = frames + 1
  local t = {}
  for i = 1, #FIELDS do t[i] = string.char(emu.read(FIELDS[i], RAM)) end
  out:write(string.pack("<I4I4BBI4", frames, polls, math.min(reads, 255), cur, rbits), table.concat(t))
  reads = 0; rbits = 0
  if fullout then
    local r = {}
    for a = 0, 0x7FF do r[a + 1] = string.char(emu.read(a, RAM)) end
    fullout:write(table.concat(r))
  end
  if frames >= NFRAMES then
    out:close(); if fullout then fullout:close() end
    local f = io.open(OUT .. ".done", "w"); f:write(string.format("%d %.3f\n", frames, os.clock() - t0)); f:close()
    emu.stop(0)
  end
end, emu.eventType.endFrame)

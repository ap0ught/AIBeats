-- generated parameters are prepended: MASKS (path), OUT (path), IOFF, RAMINIT ("nes"|"none"), FULLRAM (bool), NFRAMES
local masks = {}
do
  local f = io.open(MASKS, "rb"); local d = f:read("*a"); f:close()
  for i = 1, #d do masks[i] = d:byte(i) end
end
local FIELDS = FIELDS_LIST
local out = io.open(OUT, "wb")
local _x = 0
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
local dlog = io.open(OUT .. ".dmc", "w")
emu.addMemoryCallback(function(addr, value)
  reads = reads + 1; rbits = ((rbits << 1) | (value & 1)) & 0xFFFFFFFF
  local s = emu.getState()
  if reads == 1 then
    dlog:write(string.format("F %d %d %d %d %d %s %d %s\n", frames + 1, s["cpu.cycleCount"], s["apu.dmc.timer.timer"], s["apu.dmc.timer.period"],
      s["apu.dmc.bitsRemaining"], tostring(s["apu.dmc.bufferEmpty"]), s["apu.dmc.bytesRemaining"], tostring(s["apu.dmc.silenceFlag"])))
  end
  dlog:write(string.format("R %d\n", s["cpu.cycleCount"]))
end, emu.callbackType.read, 0x4016)
emu.addMemoryCallback(function(addr, value)
  local s = emu.getState()
  dlog:write(string.format("W %d %d %d %d\n", addr, value, s["cpu.cycleCount"], frames + 1))
end, emu.callbackType.write, 0x4010, 0x4015)
emu.addMemoryCallback(function()
  local s = emu.getState()
  dlog:write(string.format("N %d %d %d %d %d %s %d\n", s["cpu.cycleCount"], frames + 1, s["apu.dmc.timer.timer"],
    s["apu.dmc.timer.period"], s["apu.dmc.bitsRemaining"], tostring(s["apu.dmc.bufferEmpty"]), s["apu.dmc.bytesRemaining"]))
end, emu.callbackType.exec, 0xF91A)
emu.addEventCallback(function()
  polls = polls + 1
  local k = polls + IOFF
  cur = masks[k] or 0
  if not NOSET then setpad(cur) end
end, emu.eventType.inputPolled)
if FORCE then
  emu.addMemoryCallback(function()
    emu.write(0x28, cur, RAM); emu.write(0x21, cur, RAM)
  end, emu.callbackType.exec, 0xF9D6)
end
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
    out:close(); dlog:close(); if fullout then fullout:close() end
    local f = io.open(OUT .. ".done", "w"); f:write(string.format("%d %.3f\n", frames, os.clock() - t0)); f:close()
    emu.stop(0)
  end
end, emu.eventType.endFrame)

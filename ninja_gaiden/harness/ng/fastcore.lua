-- fastcore.lua: the Mesen 2 side of ng/fastcore.py (Mesen test runner = headless, one long-lived process).
-- fastcore.py prepends: PORT, TOKEN, TICKS ({ {name, addr, "hexsig" or false}, ... }).
--
-- Protocol (TCP, Mesen connects to Python): request = one text line (+ binary payload of announced length);
-- reply = one text line "OK ..." / "ERR ..." (+ " <len>" and a binary payload when there is one).
--
-- Time base = NesHawk numbering. A CHECKPOINT is the CPU at the NMI handler entry $F91A. The checkpoint after
-- NesHawk frame f is where the game reads row f+1. Row k of a request = the k-th frame after the checkpoint it
-- starts from; the bytes recorded for row k = RAM at the end of that frame (Mesen endFrame). Savestates are
-- always taken/loaded at a checkpoint (Mesen allows savestates only inside an exec callback).
--
-- Input: the game reads the pad twice in its NMI ($F9CC, $F9D3) and keeps the previous pad on a mismatch.
-- Mesen's DMC-DMA/controller conflicts fall on other frames than NesHawk's, so this script FORCES a clean read:
-- at $F9D6 both copies ($28, $21) are set to the row's mask. The pad is also set on Mesen's controller.
-- NesHawk's own conflicts are not modelled (see knowledge/fastcore.md).
local socket = require("socket.core")
local RAM = emu.memType.nesInternalRam
local CPU = emu.memType.nesMemory
local NMI = 0xF91A
local PADCHK = 0xF9D6

local conn = socket.tcp()
conn:settimeout(30)
assert(conn:connect("127.0.0.1", PORT))
conn:settimeout(nil)
conn:setoption("tcp-nodelay", true)
conn:send("HELLO " .. TOKEN .. "\n")

local function recvline()
  local l, err = conn:receive("*l")
  if not l then emu.stop(3); error("socket closed: " .. tostring(err)) end
  return l
end
local function recvn(n)
  if n == 0 then return "" end
  local d, err = conn:receive(n)
  if not d then emu.stop(3); error("socket closed: " .. tostring(err)) end
  return d
end
local function reply(line, payload)
  if payload then conn:send(line .. " " .. #payload .. "\n" .. payload) else conn:send(line .. "\n") end
end
local function words(l)
  local t = {}
  for w in l:gmatch("%S+") do t[#t + 1] = w end
  return t
end

-- power-on: NesHawk's RAM pattern ((addr & 4) ? $FF : $00), written before the reset code runs
local powered = false
emu.addMemoryCallback(function()
  if powered then return end
  powered = true
  for a = 0, 0x7FF do emu.write(a, ((a & 4) ~= 0) and 0xFF or 0x00, RAM) end
end, emu.callbackType.exec, 0xFFDA)

-- BOOT <n> + n masks: play rows 1..n from power-on (row k = NesHawk frame k after reset()), then go idle at the
-- checkpoint after row n. n = 0: idle at the first checkpoint (frame unknown; load a state next).
local bw = words(recvline())
local boot_n = tonumber(bw[2])
local boot_rows = recvn(boot_n)
local boot_polls, boot_frames = 0, 0

local ADDRS = {}
local slots = {}
local job = nil
local cur = 0
local mode = (boot_n > 0) and "boot" or "idle"
local frames_total, lag_total = 0, 0
local reads = 0

-- execution counters (like the BizHawk bridge's `tick`): executions of addr during the frame
local tick_n = {}
local function sigmatch(addr, sig)
  for i = 0, 3 do
    if emu.read(addr + i, CPU) ~= tonumber(sig:sub(i * 2 + 1, i * 2 + 2), 16) then return false end
  end
  return true
end
for i, t in ipairs(TICKS) do
  tick_n[i] = 0
  local addr, sig = t[2], t[3]
  emu.addMemoryCallback(function()
    if (not sig) or sigmatch(addr, sig) then tick_n[i] = tick_n[i] + 1 end
  end, emu.callbackType.exec, addr)
end

local function setpad(m)
  emu.setInput({a = (m & 0x80) ~= 0, b = (m & 0x40) ~= 0, select = (m & 0x20) ~= 0, start = (m & 0x10) ~= 0,
                up = (m & 0x08) ~= 0, down = (m & 0x04) ~= 0, left = (m & 0x02) ~= 0, right = (m & 0x01) ~= 0}, 0, 0)
end

local function readram_all()
  local r = {}
  for a = 0, 0x7FF do r[a + 1] = string.char(emu.read(a, RAM)) end
  return table.concat(r)
end

-- one row's record: ADDRS bytes, tick counts (u8), lagged (u8)
local function record_row(lagged)
  local t = {}
  for i = 1, #ADDRS do t[i] = string.char(emu.read(ADDRS[i], RAM)) end
  local n = #t
  for i = 1, #TICKS do n = n + 1; t[n] = string.char(math.min(tick_n[i], 255)) end
  t[n + 1] = string.char(lagged)
  return table.concat(t)
end

-- RUN payload (little endian): u16 ncand, u8 flags (1 = 2 KB RAM after the last row, 2 = keep each end state in
--   slot "<prefix><i>", 4 = record every row (else the last row only)), u16 nstop,
--   nstop x (u16 addr, u8 op (0 ==, 1 !=, 2 >=, 3 <=, 4 changed since the start, 5 &mask ~= 0), u8 value),
--   then per candidate: u16 len, len x u8 mask.
-- Reply payload per candidate: u16 rows played, u8 status (0 all rows, 1 stopped by a condition, 2 the checkpoint
--   after the last row came late (NMI off) - its end state is not at row len), records, [2048 B RAM].
local function parse_job(slot, prefix, p)
  local pos = 1
  local function u8() local v = p:byte(pos); pos = pos + 1; return v end
  local function u16() local v = string.unpack("<I2", p, pos); pos = pos + 2; return v end
  local j = {slot = slot, prefix = prefix, cands = {}, stops = {}, out = {}, ci = 0}
  local nc = u16()
  j.flags = u8()
  local ns = u16()
  for i = 1, ns do j.stops[i] = {u16(), u8(), u8()} end
  for i = 1, nc do
    local len = u16()
    j.cands[i] = p:sub(pos, pos + len - 1)
    pos = pos + len
  end
  return j
end

local function start_rows(j, rows)
  j.rows = rows
  j.k = 1
  j.rec = {}
  j.status = 0
  j.ended = false
  j.lagend = false
  j.start0 = {}
  for i, s in ipairs(j.stops) do j.start0[i] = emu.read(s[1], RAM) end
  cur = rows:byte(1) or 0
  setpad(cur)
end

local function begin_candidate()
  local j = job
  while true do
    j.ci = j.ci + 1
    if j.ci > #j.cands then return false end
    if #j.cands[j.ci] > 0 then break end
    j.out[#j.out + 1] = string.pack("<I2B", 0, 0)   -- empty candidate: nothing played
  end
  emu.loadSavestate(slots[j.slot])
  start_rows(j, j.cands[j.ci])
  return true
end

local function finish_candidate()
  local j = job
  if j.lagend and j.status == 0 then j.status = 2 end
  local extra = ((j.flags & 1) ~= 0) and readram_all() or ""
  j.out[#j.out + 1] = string.pack("<I2B", j.played, j.status) .. table.concat(j.rec) .. extra
  if (j.flags & 2) ~= 0 then slots[j.prefix .. j.ci] = emu.createSavestate() end
end

local function handle_command()
  -- runs inside the NMI exec callback (savestates allowed); returns when emulation has to continue
  while true do
    local w = words(recvline())
    local c = w[1]
    if c == "SAVE" then
      slots[w[2]] = emu.createSavestate(); reply("OK " .. #slots[w[2]])
    elseif c == "LOAD" then
      if not slots[w[2]] then reply("ERR noslot " .. w[2]) else emu.loadSavestate(slots[w[2]]); reply("OK") end
    elseif c == "GET" then
      if not slots[w[2]] then reply("ERR noslot " .. w[2]) else reply("OK", slots[w[2]]) end
    elseif c == "PUT" then
      slots[w[2]] = recvn(tonumber(w[3])); reply("OK")
    elseif c == "DROP" then
      for i = 2, #w do slots[w[i]] = nil end; reply("OK")
    elseif c == "DROPPREFIX" then
      for k in pairs(slots) do if k:sub(1, #w[2]) == w[2] then slots[k] = nil end end; reply("OK")
    elseif c == "ADDRS" then
      local p = recvn(tonumber(w[2]) * 2)
      ADDRS = {}
      for i = 1, tonumber(w[2]) do ADDRS[i] = string.unpack("<I2", p, i * 2 - 1) end
      reply("OK")
    elseif c == "RAM" then
      reply("OK", readram_all())
    elseif c == "POKE" then
      emu.write(tonumber(w[2]), tonumber(w[3]), RAM); reply("OK")
    elseif c == "INFO" then
      reply("OK frames=" .. frames_total .. " lag=" .. lag_total)
    elseif c == "STEP" then
      -- STEP <n> <flags> + n masks: play from the CURRENT checkpoint (flags 4 = record every row)
      local n = tonumber(w[2])
      local p = recvn(n)
      if n == 0 then
        reply("OK 0 0", "")
      else
        job = {step = true, cands = {p}, stops = {}, out = {}, flags = tonumber(w[3]) or 0, ci = 1}
        start_rows(job, p)
        mode = "run"
        return
      end
    elseif c == "RUN" then
      -- RUN <slot> <prefix> <payload len>
      local p = recvn(tonumber(w[4]))
      if not slots[w[2]] then
        reply("ERR noslot " .. w[2])
      else
        job = parse_job(w[2], w[3], p)
        if begin_candidate() then
          mode = "run"
          return
        end
        reply("OK", table.concat(job.out)); job = nil
      end
    elseif c == "QUIT" then
      reply("OK"); conn:close(); emu.stop(0); return
    elseif c == "PING" then
      reply("OK")
    else
      reply("ERR unknown " .. tostring(c))
    end
  end
end

emu.addMemoryCallback(function()
  if mode == "boot" then
    if boot_frames >= boot_n then
      mode = "idle"
      reply("OK BOOT " .. boot_frames .. " " .. ((boot_frames == boot_n) and 0 or 1))
      handle_command()
    end
    return
  end
  if mode == "idle" then
    handle_command()
    return
  end
  local j = job
  if not j.ended then return end
  -- the checkpoint after the last row (late by the NMI-off frames if lagend)
  if j.step then
    mode = "idle"; job = nil
    reply("OK " .. j.played .. " " .. ((j.lagend and 2) or j.status), table.concat(j.rec))
    handle_command()
    return
  end
  finish_candidate()
  if not begin_candidate() then
    mode = "idle"; job = nil
    reply("OK", table.concat(j.out))
    handle_command()
  end
end, emu.callbackType.exec, NMI)

emu.addMemoryCallback(function()
  emu.write(0x28, cur, RAM); emu.write(0x21, cur, RAM)
end, emu.callbackType.exec, PADCHK)

emu.addMemoryCallback(function() reads = reads + 1 end, emu.callbackType.read, 0x4016)

-- input poll (scanline 241): the frame of the next row starts here
emu.addEventCallback(function()
  for i = 1, #TICKS do tick_n[i] = 0 end
  reads = 0
  if mode == "boot" then
    boot_polls = boot_polls + 1
    cur = boot_rows:byte(boot_polls + 1) or 0
    setpad(cur)
    return
  end
  if mode ~= "run" then return end
  local j = job
  if j.ended then
    -- a poll after the last row's frame before the checkpoint: the NMI was off on that frame
    j.after = (j.after or 0) + 1
    if j.after > 1 then j.lagend = true end
    return
  end
  j.k = j.k + 1
  cur = j.rows:byte(j.k) or 0
  setpad(cur)
end, emu.eventType.inputPolled)

-- end of a frame: record the row
emu.addEventCallback(function()
  frames_total = frames_total + 1
  local lagged = (reads == 0) and 1 or 0
  lag_total = lag_total + lagged
  if mode == "boot" then boot_frames = boot_frames + 1; return end
  if mode ~= "run" then return end
  local j = job
  if j.ended then return end
  local k = j.k
  local last = k >= #j.rows
  local stop = false
  for i, s in ipairs(j.stops) do
    local v = emu.read(s[1], RAM)
    local op = s[2]
    if (op == 0 and v == s[3]) or (op == 1 and v ~= s[3]) or (op == 2 and v >= s[3]) or (op == 3 and v <= s[3])
       or (op == 4 and v ~= j.start0[i]) or (op == 5 and (v & s[3]) ~= 0) then stop = true end
  end
  if (j.flags & 4) ~= 0 then
    j.rec[#j.rec + 1] = record_row(lagged)
  elseif last or stop then
    j.rec = {record_row(lagged)}
  end
  if last or stop then
    j.played = k
    if stop and not last then j.status = 1 end
    j.ended = true
    j.after = 0
  end
end, emu.eventType.endFrame)

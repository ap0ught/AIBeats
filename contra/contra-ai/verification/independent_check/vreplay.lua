-- vreplay.lua : independent verifier replay. Runs inside EmuHawk, no sockets, no savestates, no memory writes,
-- no reset. Reads verify1/job_<job>.txt (key=value lines), plays the input list from wherever the emulator is
-- when the script starts (logged), and writes per-frame RAM + OAM + lag flag and a PNG of every requested frame.
--
-- job keys: inputs=<path>  out=<dir, must exist>  extra=<idle frames after the list>  maxrows=<0 = all>
--           shots=all | none | a-b,c-d,...        every=<also every Nth frame, 0 = off>
local DIR = "verify2/"
local job = tostring(userdata.get("job"))
local cfg = {}
for line in io.lines(DIR .. "job_" .. job .. ".txt") do
  local k, v = line:match("^(%w+)=(.*)$")
  if k then cfg[k] = v end
end
local out = cfg.out
local logf = io.open(out .. "/replay.log", "w")
local function log(s) logf:write(s .. "\n"); logf:flush(); console.log(s) end

local ok, err = pcall(function()
  client.unpause()
  emu.limitframerate(false)
  client.SetSoundOn(false)
  client.frameskip(0)

  log("start_framecount=" .. emu.framecount())
  log("start_lagcount=" .. emu.lagcount())
  log("system=" .. tostring(emu.getsystemid()))
  pcall(function() log("board=" .. tostring(emu.getboardname())) end)
  pcall(function() log("romhash=" .. tostring(gameinfo.getromhash())) end)
  pcall(function() log("romname=" .. tostring(gameinfo.getromname())) end)
  pcall(function() log("status=" .. tostring(gameinfo.getstatus())) end)
  pcall(function() log("displaytype=" .. tostring(emu.getdisplaytype())) end)
  local names = {}
  local d = memory.getmemorydomainlist()
  for i = 0, 64 do if d[i] ~= nil then names[#names + 1] = tostring(d[i]) end end
  log("domains=" .. table.concat(names, "|"))
  pcall(function() log("movie_mode=" .. tostring(movie.mode())) end)
  pcall(function() log("movie_loaded=" .. tostring(movie.isloaded())) end)

  -- read inputs
  local BIT = {A = 128, B = 64, Select = 32, Start = 16, Up = 8, Down = 4, Left = 2, Right = 1}
  local NAMES = {"A", "B", "Select", "Start", "Up", "Down", "Left", "Right"}
  local rows = {}
  for line in io.lines(cfg.inputs) do
    if line:sub(1, 1) ~= "#" then
      line = line:gsub("\r", "")
      local t = {}
      local m = 0
      for b in line:gmatch("[^+,%s]+") do
        assert(BIT[b], "unknown button " .. b)
        t[b] = true
        m = m + BIT[b]
      end
      rows[#rows + 1] = {t, m}
    end
  end
  local maxrows = tonumber(cfg.maxrows or "0") or 0
  local nrows = #rows
  if maxrows > 0 and maxrows < nrows then nrows = maxrows end
  local extra = tonumber(cfg.extra or "0") or 0
  log("rows_in_file=" .. #rows .. " rows_played=" .. nrows .. " extra=" .. extra)

  -- which frames get a picture
  local every = tonumber(cfg.every or "0") or 0
  local all = (cfg.shots == "all")
  local ranges = {}
  if cfg.shots and cfg.shots ~= "all" and cfg.shots ~= "none" then
    for a, b in cfg.shots:gmatch("(%d+)-(%d+)") do ranges[#ranges + 1] = {tonumber(a), tonumber(b)} end
  end
  local function want(f)
    if all then return true end
    if every > 0 and f % every == 0 then return true end
    for _, r in ipairs(ranges) do if f >= r[1] and f <= r[2] then return true end end
    return false
  end

  local function binstr(domain, addr, len)
    local s
    local okb = pcall(function() s = memory.read_bytes_as_binary_string(addr, len, domain) end)
    if okb and type(s) == "string" and #s == len then return s end
    local arr = memory.read_bytes_as_array(addr, len, domain)
    local p = {}
    for i = 0, len do if arr[i] ~= nil then p[#p + 1] = string.char(arr[i]) end end
    s = table.concat(p)
    assert(#s == len, "short read " .. #s)
    return s
  end

  local tr = io.open(out .. "/trace.bin", "wb")
  local total = nrows + extra
  local f0 = emu.framecount()
  for i = 1, total do
    local set = {}
    local m = 0
    local row = rows[i]
    for _, n in ipairs(NAMES) do
      local v = false
      if i <= nrows and row[1][n] then v = true end
      set["P1 " .. n] = v
      set["P2 " .. n] = false
    end
    if i <= nrows then m = row[2] end
    joypad.set(set)
    emu.frameadvance()
    local f = emu.framecount()
    assert(f == f0 + i, "frame count skew: " .. f .. " vs " .. (f0 + i))
    local b0 = f % 256
    local b1 = math.floor(f / 256) % 256
    local b2 = math.floor(f / 65536) % 256
    tr:write(string.char(b0, b1, b2, 0, emu.islagged() and 1 or 0, m))
    tr:write(binstr("RAM", 0, 2048))
    local oam
    if not pcall(function() oam = binstr("OAM", 0, 256) end) then oam = string.rep("\0", 256) end   -- quickerNES has no OAM domain
    tr:write(oam)
    if want(f) then client.screenshot(string.format("%s/f%05d.png", out, f)) end
    if i % 5000 == 0 then log("progress frame=" .. f .. " lag=" .. emu.lagcount()) end
  end
  tr:close()
  log("end_framecount=" .. emu.framecount())
  log("end_lagcount=" .. emu.lagcount())
  log("DONE")
end)
if not ok then log("ERROR " .. tostring(err)) end
logf:close()
client.exit()

-- verify_movie.lua : plays the loaded BizHawk movie hands-off (no joypad calls, no memory writes, no savestates)
-- and records, for every frame, the frame number, BizHawk's lag flag and all 2 KB of NES RAM. Takes screenshots of
-- the frames listed in "shots" (numbers joined by _ ; BizHawk's --userdata
-- mangles commas). Used by verify_bk2.py, which starts EmuHawk like this (from the BizHawk folder):
--
--   EmuHawk.exe --config=<private config> --lua=verify_movie.lua
--               --userdata=frames:34568;out:<dir>;shots:590_591_592_593_594_34508_34509 --movie=contra_ai_9m24s.bk2
--               "Contra (USA).nes"
--
-- Output in <dir>: movie.log (what BizHawk loaded), ram.bin (per frame: 3-byte frame number, lag flag, 2048 RAM
-- bytes), f<frame>.png. Optional userdata "save:<path>" re-saves the loaded movie there (BizHawk's own
-- writer; it appends .bk2).
local target = tonumber(userdata.get("frames") or "34568")
local out = tostring(userdata.get("out"))
local shots = {}
for n in string.gmatch(tostring(userdata.get("shots") or ""), "%d+") do shots[tonumber(n)] = true end
local save = userdata.get("save")

local logf = io.open(out .. "/movie.log", "w")
local function log(s) logf:write(s .. "\n"); logf:flush() end

local function binstr(domain, addr, len)
  local s
  local ok = pcall(function() s = memory.read_bytes_as_binary_string(addr, len, domain) end)
  if ok and type(s) == "string" and #s == len then return s end
  local arr = memory.read_bytes_as_array(addr, len, domain)
  local p = {}
  for i = 0, len do if arr[i] ~= nil then p[#p + 1] = string.char(arr[i]) end end
  s = table.concat(p)
  assert(#s == len, "short read " .. #s)
  return s
end

local ok, err = pcall(function()
  client.unpause()
  pcall(function() emu.limitframerate(false) end)
  pcall(function() client.SetSoundOn(false) end)
  pcall(function() client.frameskip(0) end)
  log("start_framecount=" .. emu.framecount())
  log("movie_loaded=" .. tostring(movie.isloaded()))
  log("movie_mode=" .. tostring(movie.mode()))
  pcall(function() log("movie_file=" .. tostring(movie.filename())) end)
  pcall(function() log("movie_length=" .. tostring(movie.length())) end)
  pcall(function() log("movie_startsfromsavestate=" .. tostring(movie.startsfromsavestate())) end)
  pcall(function() log("movie_startsfromsaveram=" .. tostring(movie.startsfromsaveram())) end)
  pcall(function()
    local h = movie.getheader()
    for k, v in pairs(h) do log("movie_header " .. tostring(k) .. "=" .. tostring(v)) end
  end)
  log("system=" .. tostring(emu.getsystemid()))
  pcall(function() log("board=" .. tostring(emu.getboardname())) end)
  pcall(function() log("romhash=" .. tostring(gameinfo.getromhash())) end)
  pcall(function() log("romname=" .. tostring(gameinfo.getromname())) end)
  local names = {}
  local d = memory.getmemorydomainlist()
  for i = 0, 64 do if d[i] ~= nil then names[#names + 1] = tostring(d[i]) end end
  log("domains=" .. table.concat(names, "|"))

  local tr = io.open(out .. "/ram.bin", "wb")
  local modes = {}
  while emu.framecount() < target do
    emu.frameadvance()
    local f = emu.framecount()
    local m = tostring(movie.mode())
    if modes[#modes] ~= m then modes[#modes + 1] = m; log("movie_mode_at_frame " .. f .. " " .. m) end
    tr:write(string.char(f % 256, math.floor(f / 256) % 256, math.floor(f / 65536) % 256, emu.islagged() and 1 or 0))
    tr:write(binstr("RAM", 0, 2048))
    if shots[f] then client.screenshot(string.format("%s/f%05d.png", out, f)) end
  end
  tr:close()
  log("end_framecount=" .. emu.framecount())
  log("end_lagcount=" .. emu.lagcount())
  log("end_movie_mode=" .. tostring(movie.mode()))
  if save then
    local okS, e2 = pcall(function() movie.save(save) end)
    log("saved_movie=" .. tostring(save) .. " ok=" .. tostring(okS) .. (okS and "" or (" " .. tostring(e2))))
  end
  log("DONE")
end)
if not ok then log("ERROR " .. tostring(err)) end
logf:close()
client.exit()

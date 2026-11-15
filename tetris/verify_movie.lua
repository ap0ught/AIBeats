-- verify_movie.lua : plays the loaded BizHawk movie hands-off (no joypad calls, no memory writes, no savestates)
-- and records, for every frame, the frame number, BizHawk's lag flag and all 2 KB of NES RAM. Used by
-- verify_bk2.py, which starts EmuHawk like this (from the BizHawk folder):
--
--   EmuHawk.exe --config=<private config> --lua=verify_movie.lua
--               --userdata=frames:8419;out:<dir> --movie=tetris_ai_2m14s_any_piece.bk2 <your ROM>
--
-- Output in <dir>: movie.log (what BizHawk loaded), ram.bin (per frame: 3-byte frame number, lag flag, 2048 RAM
-- bytes), last.png (a screenshot of the last frame).
local target = tonumber(userdata.get("frames") or "8419")
local out = tostring(userdata.get("out"))

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

  local tr = io.open(out .. "/ram.bin", "wb")
  local modes = {}
  while emu.framecount() < target do
    emu.frameadvance()
    local f = emu.framecount()
    local m = tostring(movie.mode())
    if modes[#modes] ~= m then modes[#modes + 1] = m; log("movie_mode_at_frame " .. f .. " " .. m) end
    tr:write(string.char(f % 256, math.floor(f / 256) % 256, math.floor(f / 65536) % 256, emu.islagged() and 1 or 0))
    tr:write(binstr("RAM", 0, 2048))
  end
  tr:close()
  client.screenshot(out .. "/last.png")
  log("end_framecount=" .. emu.framecount())
  log("end_lagcount=" .. emu.lagcount())
  log("end_movie_mode=" .. tostring(movie.mode()))
  log("DONE")
end)
if not ok then log("ERROR " .. tostring(err)) end
logf:close()
client.exit()

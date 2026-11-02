-- vreplay.lua : independent open-loop replay for the verifier (work/verify). No TCP, no project code.
-- Reads work/verify/run/cfg.txt: line 1 = input file, line 2 = output dir, line 3 = tail frames (no input after the
-- last row), line 4 = "shots" or "noshots".
-- For every emulated frame writes one CSV line (after the frame): row index (1-based; 0 for tail frames counted
-- as row = nrows + k), emu.framecount, lagged, RAM bytes, PPU timer-digit tiles, palette, OAM sprite count.
-- Screenshots (picture of the frame just emulated): rows 165-185; the first 4 frames after any all-black palette
-- ends (and the last all-black frame before it); every frame while stage $6D == 21 and $63 <= 4.

local here = "G:/AI World Record/Ninja Gaiden/work/verify/"
local cf = io.open(here .. "run/cfg.txt", "r")
local INPUTS = cf:read("*l"); local OUTDIR = cf:read("*l"); local TAIL = tonumber(cf:read("*l"))
local SHOTS = (cf:read("*l") or "shots") == "shots"
cf:close()

local log = io.open(OUTDIR .. "/frames.csv", "w")
local meta = io.open(OUTDIR .. "/meta.txt", "w")
meta:write("framecount_at_script_start=" .. emu.framecount() .. "\n")
meta:write("system=" .. tostring(emu.getsystemid()) .. "\n")
local names = {}
local dl = memory.getmemorydomainlist()
for i = 0, 64 do if dl[i] ~= nil then names[#names + 1] = tostring(dl[i]) end end
meta:write("domains=" .. table.concat(names, "|") .. "\n")
pcall(function() meta:write("board=" .. tostring(emu.getboardname()) .. "\n") end)
pcall(function() meta:write("romhash=" .. tostring(gameinfo.getromhash()) .. "\n") end)
pcall(function() meta:write("pref_core=" .. tostring(client.getconfig().PreferredCores["NES"]) .. "\n") end)
pcall(function() meta:write("opposing=" .. tostring(client.getconfig().OpposingDirPolicy) .. "\n") end)
meta:flush()

-- read inputs
local rows = {}
for line in io.lines(INPUTS) do
  if line:sub(1, 1) ~= "#" then
    rows[#rows + 1] = line:gsub("%s+$", "")
  end
end
meta:write("rows=" .. #rows .. "\n"); meta:flush()

local BUTTONS = {"Up", "Down", "Left", "Right", "Select", "Start", "B", "A"}
local function pad(s)
  local t = {}
  for _, b in ipairs(BUTTONS) do t[b] = false end
  for tok in s:gmatch("[^+,]+") do
    local ok = false
    for _, b in ipairs(BUTTONS) do if b == tok then t[b] = true; ok = true end end
    if not ok then meta:write("BAD_TOKEN " .. tok .. "\n") end
  end
  return t
end

local RAMADDR = {0x33, 0x6D, 0x6E, 0x63, 0x62, 0x66, 0x3E, 0x1FD, 0x65, 0x64, 0xC9, 0x76, 0xBF, 0x2A, 0x29, 0x86, 0x85, 0x8A, 0x4C, 0x1E}
local hdr = {"row", "fc", "lagged"}
for _, a in ipairs(RAMADDR) do hdr[#hdr + 1] = string.format("r%X", a) end
hdr[#hdr + 1] = "tdig"; hdr[#hdr + 1] = "pal"; hdr[#hdr + 1] = "nspr"
log:write(table.concat(hdr, ",") .. "\n")

emu.limitframerate(false)
pcall(function() client.SetSoundOn(false) end)

local prev_black = false
local after_flip = 0
local end_left = 40   -- screenshots kept for 40 frames after the timer reads 0 in 6-5
local total = #rows + TAIL
local buf = {}
-- A fresh launch has already emulated frame 1 with no input: that frame IS row 1 (.bk2 numbering, row k =
-- framecount k). Row 1 must therefore be empty; play from row 2.
local first = emu.framecount() + 1
meta:write("first_row_played=" .. first .. "\n")
for i = 1, first - 1 do
  if rows[i] ~= nil and rows[i] ~= "" then meta:write("ERROR row " .. i .. " not empty but already emulated\n") end
end
for i = first, total do
  if i <= #rows then joypad.set(pad(rows[i]), 1) end
  emu.frameadvance()
  local p = {i, emu.framecount(), emu.islagged() and 1 or 0}
  for _, a in ipairs(RAMADDR) do p[#p + 1] = mainmemory.read_u8(a) end
  local d = memory.read_bytes_as_array(0x20A9, 3, "PPU Bus")
  p[#p + 1] = string.format("%02X%02X%02X", d[1], d[2], d[3])
  local pal = memory.read_bytes_as_array(0, 32, "PALRAM")
  local ps = {}
  local nonblack = 0
  for k = 1, 32 do
    ps[k] = string.format("%02X", pal[k])
    local v = pal[k] % 64
    if not (v == 0x0F or v == 0x0E or v == 0x0D or v == 0x1F or v == 0x1E or v == 0x2F or v == 0x2E or v == 0x3F or v == 0x3E) then nonblack = nonblack + 1 end
  end
  p[#p + 1] = table.concat(ps)
  local oam = memory.read_bytes_as_array(0, 256, "OAM")
  local ns = 0
  for k = 0, 63 do if oam[k * 4 + 1] < 0xEF then ns = ns + 1 end end
  p[#p + 1] = ns
  buf[#buf + 1] = table.concat(p, ",")
  if i == #rows then
    local r0 = memory.read_bytes_as_array(0, 2048, "RAM")
    local h0 = {}
    for k = 1, 2048 do h0[k] = string.format("%02x", r0[k]) end
    meta:write("ram_at_last_row=" .. table.concat(h0) .. "\n"); meta:flush()
  end
  if #buf >= 2000 then log:write(table.concat(buf, "\n") .. "\n"); buf = {} end
  if SHOTS then
    local stage, timer = mainmemory.read_u8(0x6D), mainmemory.read_u8(0x63)
    local black = (nonblack == 0)
    local shot = false
    if i >= 165 and i <= 185 then shot = true end
    if prev_black and not black then
      os.rename(OUTDIR .. "/shots/_lastblack.png", OUTDIR .. string.format("/shots/b%06d.png", i - 1))
      after_flip = 4
    end
    if after_flip > 0 then shot = true; after_flip = after_flip - 1 end
    if stage == 21 and timer <= 4 and end_left > 0 then
      shot = true
      if timer == 0 then end_left = end_left - 1 end
    end
    if shot then client.screenshot(OUTDIR .. string.format("/shots/s%06d.png", i)) end
    if black then client.screenshot(OUTDIR .. "/shots/_lastblack.png") end
    prev_black = black
  end
end
log:write(table.concat(buf, "\n") .. "\n")
log:close()
local ram = memory.read_bytes_as_array(0, 2048, "RAM")
local hx = {}
for k = 1, 2048 do hx[k] = string.format("%02x", ram[k]) end
meta:write("ram_after_last=" .. table.concat(hx) .. "\n")
meta:write("DONE\n")
meta:close()
client.exit()

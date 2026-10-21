-- bridge.lua (Contra) : runs inside EmuHawk. Connects to the Python controller over TCP
-- and executes newline-delimited commands, replying one line per command.
-- Adapted from toads/bridge.lua. The bridge knows nothing about the game: the RAM fields
-- reported in every state line are sent from Python (`fields name:addr,...`).
--
-- Commands:
--   ping                        -> pong
--   step <n> <buttons>          -> hold <buttons> (comma list or "-") for n frames, reply state
--   stepx <hex>                 -> one frame per 2 hex digits (button mask, see MASKBITS), reply state
--   state                       -> reply state
--   fields name:addr,...        -> which RAM bytes a state line reports
--   trace on|off                -> step/stepx reply one state line per frame, joined by ";"
--   ram <addr> <len>            -> hex bytes of main RAM
--   ramd <domain> <addr> <len>  -> hex bytes of any memory domain (e.g. OAM, PALRAM, "PPU Bus")
--   domains                     -> memory domain names
--   coreinfo                    -> system id, board, preferred core, domains
--   save <path> | load <path>   -> savestate to/from file
--   msave | mload <id> | mfree <id>   -> in-memory savestates
--   screenshot <path>           -> png of the frame last emulated
--   fast | normal | frameskip n -> unthrottle / throttle / draw every nth frame
--   reset                       -> power-cycle core
--   poke <addr> <val>           -> DEBUG ONLY, never used by a run
--   quit                        -> exit EmuHawk
--
-- State line: frame=<emu.framecount> <fields...> lag=<emu.lagcount> lagged=<0|1: was the last frame a lag frame>

local socket = require("socket.core")

local port = tonumber(userdata.get("port") or 0)
if not port or port == 0 then
  local f = io.open(".bridge_port", "r")
  if f then port = tonumber(f:read("*l")); f:close() end
end
assert(port and port > 0, "bridge: no port given")

local conn = socket.tcp()
conn:settimeout(15)
local ok, err = conn:connect("127.0.0.1", port)
assert(ok, "bridge: connect failed: " .. tostring(err))
conn:setoption("tcp-nodelay", true)
conn:settimeout(0.05)
console.log("bridge: connected on port " .. port)

local FIELDS = {}

local BUTTONS = {"Up","Down","Left","Right","Select","Start","B","A"}
-- mask bits follow the game's own controller byte ($F1): A B Select Start Up Down Left Right
local MASKBITS = {{128,"A"},{64,"B"},{32,"Select"},{16,"Start"},{8,"Up"},{4,"Down"},{2,"Left"},{1,"Right"}}
TRACE = false

local function state_str()
  local p = {"frame=" .. emu.framecount()}
  for _, f in ipairs(FIELDS) do
    p[#p+1] = f[1] .. "=" .. mainmemory.read_u8(f[2])
  end
  p[#p+1] = "lag=" .. emu.lagcount()
  p[#p+1] = "lagged=" .. (emu.islagged() and 1 or 0)
  return table.concat(p, " ")
end

local function parse_buttons(s)
  local t = {}
  for _, b in ipairs(BUTTONS) do t[b] = false end
  if s and s ~= "-" then
    for b in string.gmatch(s, "[^,]+") do t[b] = true end
  end
  return t
end

local MASKCACHE = {}
local function mask_buttons(m)
  local t = MASKCACHE[m]
  if t then return t end
  t = {}
  local v = m
  for _, mb in ipairs(MASKBITS) do
    if v >= mb[1] then t[mb[2]] = true; v = v - mb[1] else t[mb[2]] = false end
  end
  MASKCACHE[m] = t
  return t
end

local function tohex(arr)
  local out = {}
  for i = 0, #arr do
    if arr[i] ~= nil then out[#out+1] = string.format("%02x", arr[i]) end
  end
  return table.concat(out)
end

local function send(line)
  conn:settimeout(30)
  conn:send(line .. "\n")
  conn:settimeout(0.05)
end

local function handle(line)
  local cmd, rest = line:match("^(%S+)%s*(.*)$")
  if cmd == "ping" then
    send("pong")
  elseif cmd == "step" then
    local n, btn = rest:match("^(%d+)%s*(%S*)$")
    n = tonumber(n) or 1
    local t = parse_buttons(btn)
    if TRACE then
      local lines = {}
      for _ = 1, n do
        joypad.set(t, 1)
        emu.frameadvance()
        lines[#lines+1] = state_str()
      end
      send(table.concat(lines, ";"))
    else
      for _ = 1, n do
        joypad.set(t, 1)
        emu.frameadvance()
      end
      send(state_str())
    end
  elseif cmd == "stepx" then
    local lines = {}
    for i = 1, #rest - 1, 2 do
      joypad.set(mask_buttons(tonumber(rest:sub(i, i + 1), 16)), 1)
      emu.frameadvance()
      if TRACE then lines[#lines+1] = state_str() end
    end
    if TRACE then send(table.concat(lines, ";")) else send(state_str()) end
  elseif cmd == "stepc" then
    -- stepc <pad addr> <carry mask> <hex>: like stepx, but with "lost press" compensation. The game reads the
    -- controller twice per frame and, when the two reads differ (NesHawk emulates the DMC/controller conflict
    -- of the real console), reuses the previous frame's buttons: a press that starts on such a frame is not
    -- seen. Here every button that was sent but is missing from the game's own controller byte (RAM <pad addr>)
    -- after a non-lag frame is pressed again on the next frame. Reply: "<hex of what was really sent>|<final
    -- carry mask>|<state or trace>". The Python side stores what was really sent, so the result is a plain
    -- input list that replays open-loop.
    local pa, carry, hex = rest:match("^(%d+)%s+(%d+)%s+(%x*)$")
    pa = tonumber(pa); carry = tonumber(carry)
    local lines, sent = {}, {}
    for i = 1, #hex - 1, 2 do
      local want = tonumber(hex:sub(i, i + 1), 16)
      local m = want
      if carry ~= 0 then
        for _, mb in ipairs(MASKBITS) do
          if carry % (mb[1] * 2) >= mb[1] and m % (mb[1] * 2) < mb[1] then m = m + mb[1] end
        end
      end
      joypad.set(mask_buttons(m), 1)
      emu.frameadvance()
      sent[#sent+1] = string.format("%02x", m)
      carry = 0
      if not emu.islagged() then
        local pad = mainmemory.read_u8(pa)
        if pad ~= m then
          for _, mb in ipairs(MASKBITS) do
            if m % (mb[1] * 2) >= mb[1] and pad % (mb[1] * 2) < mb[1] then carry = carry + mb[1] end
          end
        end
      end
      if TRACE then lines[#lines+1] = state_str() end
    end
    send(table.concat(sent) .. "|" .. carry .. "|" .. (TRACE and table.concat(lines, ";") or state_str()))
  elseif cmd == "fields" then
    FIELDS = {}
    for name, addr in string.gmatch(rest, "([%w_]+):(%d+)") do
      FIELDS[#FIELDS+1] = {name, tonumber(addr)}
    end
    send("ok " .. #FIELDS)
  elseif cmd == "poke" then
    -- DEBUG ONLY (mechanics experiments on snapshots). Never used by a run: runs are inputs only.
    local a, v = rest:match("^(%d+)%s+(%d+)$")
    mainmemory.write_u8(tonumber(a), tonumber(v)); send("ok")
  elseif cmd == "trace" then
    TRACE = (rest == "on"); send("ok")
  elseif cmd == "state" then
    send(state_str())
  elseif cmd == "ram" then
    local a, l = rest:match("^(%d+)%s+(%d+)$")
    local arr = mainmemory.read_bytes_as_array(tonumber(a), tonumber(l))
    send(tohex(arr))
  elseif cmd == "ramd" then
    -- domain names may contain spaces ("PPU Bus"): Python sends them with "_" for " "
    local dom, a, l = rest:match("^(%S+)%s+(%d+)%s+(%d+)$")
    dom = dom:gsub("_", " ")
    local arr = memory.read_bytes_as_array(tonumber(a), tonumber(l), dom)
    send(tohex(arr))
  elseif cmd == "domains" then
    local names = {}
    local d = memory.getmemorydomainlist()
    for i = 0, 64 do if d[i] ~= nil then names[#names+1] = tostring(d[i]) end end
    send(table.concat(names, "|"))
  elseif cmd == "coreinfo" then
    local names = {}
    local d = memory.getmemorydomainlist()
    for i = 0, 64 do if d[i] ~= nil then names[#names+1] = tostring(d[i]) end end
    local board = "?"
    pcall(function() board = tostring(emu.getboardname()) end)
    local pref = "?"
    pcall(function() pref = tostring(client.getconfig().PreferredCores["NES"]) end)
    local hash = "?"
    pcall(function() hash = tostring(gameinfo.getromhash()) end)
    send("sys=" .. tostring(emu.getsystemid()) .. ";board=" .. board .. ";pref=" .. pref ..
         ";framecount=" .. emu.framecount() .. ";romhash=" .. hash .. ";domains=" .. table.concat(names, "|"))
  elseif cmd == "msave" then
    send(memorysavestate.savecorestate())                    -- in-RAM state, fast
  elseif cmd == "mload" then
    memorysavestate.loadcorestate(rest); send("ok")
  elseif cmd == "mfree" then
    memorysavestate.removestate(rest); send("ok")
  elseif cmd == "save" then
    savestate.save(rest, true); send("ok")
  elseif cmd == "load" then
    local r = savestate.load(rest, true); send(r and "ok" or "fail")
  elseif cmd == "screenshot" then
    client.screenshot(rest); send("ok")
  elseif cmd == "fast" then
    emu.limitframerate(false); client.SetSoundOn(false); send("ok")
  elseif cmd == "normal" then
    emu.limitframerate(true); send("ok")
  elseif cmd == "frameskip" then
    -- draw only every Nth frame while searching: the emulation itself is untouched
    client.frameskip(tonumber(rest) or 0); send("ok")
  elseif cmd == "invis" then
    -- skip rendering and sound entirely while searching (screenshots are stale while this is on)
    client.invisibleemulation(rest == "on"); send("ok")
  elseif cmd == "speed" then
    client.speedmode(tonumber(rest) or 100); send("ok")
  elseif cmd == "reset" then
    client.reboot_core(); send(state_str())
  elseif cmd == "quit" then
    send("bye"); conn:close(); client.exit()
  else
    send("err unknown command: " .. tostring(cmd))
  end
end

client.unpause()
-- Block for commands. Yielding while idle lets the emulator free-run (frames advanced with no
-- input from us and broke replay determinism), so the script holds the main thread instead.
conn:settimeout(nil)
while true do
  local line, e = conn:receive("*l")
  if line then
    local okh, herr = pcall(handle, line)
    if not okh then send("err " .. tostring(herr)) end
  elseif e == "closed" then
    console.log("bridge: connection closed, exiting")
    client.exit()
    break
  end
end

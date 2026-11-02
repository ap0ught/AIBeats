local f = io.open("G:/AI World Record/Ninja Gaiden/work/fastcore/out/dbg.out", "w")
local RAM = emu.memType.nesInternalRam
local hits, hits2 = 0, 0
local ok, err = pcall(function()
  emu.addMemoryCallback(function(a, v) hits = hits + 1 end, emu.callbackType.exec, 0xF9D6)
  emu.addMemoryCallback(function(a, v) hits2 = hits2 + 1 end, emu.callbackType.exec, 0xF91A)
end)
f:write("reg ", tostring(ok), " ", tostring(err), "\n")
local n = 0
emu.addEventCallback(function()
  n = n + 1
  if n == 300 then
    f:write("hits ", hits, " nmi ", hits2, "\n")
    local ok2, e2 = pcall(function() emu.write(0x28, 0x55, RAM) end)
    f:write("write ", tostring(ok2), " ", tostring(e2), " now ", emu.read(0x28, RAM), "\n")
    f:write("memtypes nesMemory=", tostring(emu.memType.nesMemory), " cpu=", tostring(emu.memType.cpu), "\n")
    for k, v in pairs(emu.memType) do if tostring(k):find("nes") then f:write(k, "=", v, " ") end end
    f:close(); emu.stop(0)
  end
end, emu.eventType.endFrame)

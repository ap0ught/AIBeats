local f = io.open("G:/AI World Record/Ninja Gaiden/work/fastcore/hello.out", "w")
local n = 0
local t0 = os.clock()
emu.addEventCallback(function()
  n = n + 1
  if n == 600 then
    f:write("frames ", n, " clock ", os.clock() - t0, " ram6D ", emu.read(0x6D, emu.memType.nesInternalRam), "\n")
    f:write("fc ", emu.getState()["frameCount"] or "nil", "\n")
    f:close()
    emu.stop(7)
  end
end, emu.eventType.endFrame)

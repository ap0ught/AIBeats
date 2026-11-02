local n = 0
local t0
local N = 20000
emu.addEventCallback(function()
  n = n + 1
  if n == 100 then t0 = os.time() ; c0 = os.clock() end
  if n == N then
    local f = io.open("G:/AI World Record/Ninja Gaiden/work/fastcore/out/speed.out", "w")
    f:write(string.format("frames %d cpu %.2f\n", N - 100, os.clock() - c0)); f:close()
    emu.stop(0)
  end
end, emu.eventType.endFrame)

local f = io.open("G:/AI World Record/Ninja Gaiden/work/fastcore/out/keys.out", "w")
local n = 0
emu.addEventCallback(function()
  n = n + 1
  if n == 300 then
    local s = emu.getState()
    local ks = {}
    for k, v in pairs(s) do ks[#ks + 1] = k .. "=" .. tostring(v) end
    table.sort(ks)
    f:write(table.concat(ks, "\n")); f:close(); emu.stop(0)
  end
end, emu.eventType.endFrame)

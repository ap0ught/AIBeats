local out = io.open("G:/AI World Record/Ninja Gaiden/work/tasrun/tas4751_ram.csv", "w")
out:write("frame,lag,mode,in,t63,t62,stg6D,room6E,m2D,s84,e66,hp65,lives76,wpn,ninpo,f1FD,b33,b4C,gt,x86,y8A,scr51,scr52\n")
local extra = 0
local function rb(a) return memory.readbyte(a, "RAM") end
while true do
  emu.frameadvance()
  local j = joypad.get(1)
  local s = ""
  for _, k in ipairs({"Up","Down","Left","Right","Start","Select","B","A"}) do if j[k] then s = s .. k:sub(1,2) end end
  local mm = movie.mode()
  out:write(string.format("%d,%d,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
    emu.framecount(), emu.islagged() and 1 or 0, mm, s, rb(0x63), rb(0x62), rb(0x6D), rb(0x6E), rb(0x2D), rb(0x84), rb(0x66), rb(0x65), rb(0x76), rb(0xC9), rb(0x64), rb(0x1FD), rb(0x33), rb(0x4C), rb(0xBF), rb(0x86), rb(0x8A), rb(0x51), rb(0x52)))
  if mm ~= "PLAY" then extra = extra + 1 end
  if extra > 900 then break end
end
out:close()
client.exit()

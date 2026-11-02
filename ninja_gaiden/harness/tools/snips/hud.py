for n in ('room03_2-1','room05_2-1','room10_3-1'):
    s=e.load('ref4751/'+n); s=e.step((),30)
    p=shot('verify/hud_'+n); print(n, s.frame, 'item', hex(e.byte(0xC9)), 'ninpo', e.byte(0x64), 'lives', e.byte(0x76), 'hp', e.byte(0x65), 'timer', e.byte(0x63))

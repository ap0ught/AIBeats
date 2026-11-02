e.load('ref4751/21_6-5_movie_end')
e.run([()]*(39510-39084))
for k in range(26):
    s=e.step((),1); print(s.frame, 'timer', s.timer, '$3E', e.byte(0x3E), 'stk', s.stk, 'buf', e.ram(0x700,6).hex())

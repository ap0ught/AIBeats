e.watch('r', 0x4016)
e.watch('r', 0x4017)
for a in (0x21,0x28,0x29,0x2a): e.watch('w', a)
s=e.step((),5); print(e.watchget()); e.watchclear()
s=e.step(('Start',),10); 
for f in range(10):
    s=e.step((),1); print(s, zp(0x20,0x30))
shot('ex1/start_test')
for i in range(20):
    s=e.step((),30); shot(f'ex1/st_{s.frame:05d}')

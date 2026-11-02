for a in (0x21,0x2a,0x28): e.watch('r', a)
s=e.step((),40); print(s.frame, e.watchget())
s=e.step(('Start',),2); s=e.step((),10); print(s.frame, e.watchget(), zp(0x20,0x40))

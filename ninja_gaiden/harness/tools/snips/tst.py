e.watch('x', 0x813E)
sid=e.msave()
for d in list(range(0,80,4))+[120,200,400]:
    e.mload(sid); e.watchclear(); e.watch('x',0x813E)
    s=e.step((),d) if d else e.state()
    f0=s.frame
    e.step(('Start',),2); s=e.step((),60)
    w=e.watchget()
    print(d, f0+1, 'accepted' if w else '-', zp(0x2b,0x30), e.ram(0x300,1).hex())
    if d in (0,40): shot(f'ex1/tst_{d}')

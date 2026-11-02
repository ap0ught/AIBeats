e.tick(0xC088)
base=e.msave()
R=[0,1,2,6,9,10,11,12,13,16,17,21,22,23,27,34,35,36,41,45,46,47]
for k in range(22):
    e.mload(base)
    e.poke(0x76,2); e.poke(0x6D,k); e.poke(0x6E,R[k]); e.poke(0x8B,0x80)
    e.trace(True); e.run([()]*320); tr=e.last_trace; e.trace(False)
    # first frame of the reload: room byte set and tk resumes
    marks=[(s.frame,s.stage,s.room,s.tk,s.x,s.y,s.timer) for s in tr[::40]]
    shot(f'lvl/s{k:02d}')
    print(k, marks)

"""Room-31 axe-boost exit vs $BF. From TAS state F0 (before the thrower spawns, 28491) with $BF poked to v (all 256):
TAS pads to 28610 (Ryu jumps from the pillar top to the X-128 wall face), then cling idle (no input) until F1.
Reports: on-TAS at 28583 (pillar top), hits (frame, X,y), the room-32 frame (exit) or none.
python work/l53p/axe31bf.py [F0=28480] [F1=28780] [--cut 28611] [--tail 0]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
CUT = opt('--cut', 28611); TAIL = opt('--tail', 0)
F0 = int(a[0]) if a else 28480; F1 = int(a[1]) if len(a) > 1 else 28780
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
rows = [TM(g)[0x2A] for g in range(F0 + 1, CUT)] + [TAIL] * (F1 - CUT + 1)
good = []
for v0 in range(0, 256, 32):
    vs = list(range(v0, v0 + 32))
    for v in vs:
        fc.load('b'); fc.poke(0xBF, v); fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in vs]
    for v, r in zip(vs, rr):
        st = r.states; hits = []; ex = None; ontas = None
        for i, s in enumerate(st):
            f = F0 + 1 + i
            if f == 28583: ontas = RXY(s) == tas_xy(f)
            if i and s['hp65'] < st[i-1]['hp65']: hits.append((f, RXY(s)))
            if s['room6e'] == 32 and ex is None: ex = f
        sp = (v + 28491 - F0) % 256
        if ex: good.append((v, sp, ex))
        print(f'v {v:3d} spawnBF {sp:3d} onTAS@28583 {ontas} hits {hits[:3]} exit {ex} end hp {st[-1]["hp65"]} X,y {RXY(st[-1])}', flush=True)
    for v in vs: fc.drop(f'p{v}')
print('EXITS', good)
fc.close()

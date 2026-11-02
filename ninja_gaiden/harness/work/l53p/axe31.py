"""Room-31 exit: does the thrower's 2nd axe (flies at Ryu clinging on the X-128 wall face) knock him LEFT over the wall
into the exit? From TAS state F0, TAS pads to the cling, then variants (no jump-off, no slash). python work/l53p/axe31.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
F0 = 28600
fc = core(tas_mst(F0)); fc.save('b'); fc._ka_slot = 'b'
tas = [TM(k)[0x2A] for k in range(F0 + 1, F0 + 80)]
def var(cut, tail, n=70):
    v = tas[:cut - F0 - 1] + [tail] * n
    return v[:n + cut - F0]
V = {'tas': tas,
     'cling_idle@28611': var(28611, 0),
     'cling_left@28611': var(28611, 0x02),
     'cling_up@28611': var(28611, 0x08)}
rr = fc.run_batch('b', list(V.values()), record='all')
for k, r in zip(V, rr):
    print('==', k)
    prev = None
    for j, s in enumerate(r.states):
        f = F0 + 1 + j; X, y = RXY(s)
        if prev is None or s['hp65'] != prev['hp65'] or s['room6e'] != prev['room6e'] or j % 4 == 0:
            print(f, f'X {X} y {y} hp {s["hp65"]} rm {s["room6e"]} touch {s["coll"] if "coll" in s else ""}', '| ' + '; '.join(f't{s[f"t{i}"]} ({s[f"ex{i}"]},{s[f"ey{i}"]})' for i in range(8) if s['eact'] >> i & 1))
        prev = s
        if s['room6e'] != 31: break
fc.close()

"""Fallback lines: a56 r2d5 with s blank rows inserted before row 150 (Ryu walking right, X ~85). Per bf: heart-down row hd on the
r2d5 path (Mesen), then s = hd - hd(243) + d for d in DS (first success kept; the remaining d tried too if --all).
Appends 'bf, line, kill row, hp' to work/l65/r2shift.res.tsv; line files work/l65/lines/r2d5_s<s>.txt."""
import sys, os
sys.path.insert(0, 'work/l65')
from lib65 import *
VS = sys.argv[1] if len(sys.argv) > 1 else '0-255'
DS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '0,1,2,3,4,-1,-2,5,6,7,8,9,10').split(',')]
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
r2 = rows_of('work/l63p/dm_r2d5_kill.txt')
os.makedirs('work/l65/lines', exist_ok=True)
fc = core65()
fc.load('c0'); fc.poke(0xBF, 0); fc.step(r2[:120]); fc.save('p120')
def hd_of(v):
    fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
    r = fc.run_batch('q', [r2[120:149] + [()] * 200], record='last', stops=[(0x487, '==', 168), (0x65, '==', 0)])[0]
    return 120 + r.rows_played if r.status == 1 and r.states[-1]['ey7'] == 168 else None
H0 = hd_of(243); print('hd(243)', H0, flush=True)
out = open('work/l65/r2shift.res.tsv', 'a', newline='\n')
for v in vals:
    h = hd_of(v)
    got = None
    if h is not None:
        for d in DS:
            s = h - H0 + d
            if s < 0: continue
            rows = r2[:149] + [()] * s + r2[149:] + [()] * 20
            fn = f'work/l65/lines/r2d5_s{s}.txt'
            if not os.path.exists(fn):
                with open(fn, 'w', newline='\n') as f:
                    f.write(f'# l65 fallback: a56 r2d5 (work/l63p/dm_r2d5_kill.txt) with {s} blank rows inserted before row 150 (row 1 = 6-5 control row)\n')
                    for r in rows[:-20]: f.write(('+'.join(r) if r else '') + '\n')
            fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
            o = outcome(fc.run_batch('q', [rows[120:]], record='last', stops=STOPS)[0])
            if o[0]:
                got = (s, o[0] + 120, o[1]); out.write(f'{v}\t{fn}\t{o[0] + 120}\t{o[1]}\n'); out.flush(); break
    print(v, 'hd', h, 'got', got, flush=True)
fc.close()

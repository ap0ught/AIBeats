"""Fallback: a56 r2d5 with s blank rows inserted before row 150 (Ryu walking to the heart, X ~85), s = 0..S; for every bf the
smallest kill (Mesen, $BF poked at control-1). Writes work/l65/lines/r2d5_s<s>.txt and appends results to work/l65/r2shift.res.tsv."""
import sys, os
sys.path.insert(0, 'work/l65')
from lib65 import *
S0, S1 = int(sys.argv[1]), int(sys.argv[2]); VS = sys.argv[3] if len(sys.argv) > 3 else '0-255'
vals = []
for p in VS.split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
r2 = rows_of('work/l63p/dm_r2d5_kill.txt')
os.makedirs('work/l65/lines', exist_ok=True)
fc = core65()
# bf-independent prefix: rows 1-120 (nothing reads $BF before the first fireball on row 121); save it once, poke $BF there
fc.load('c0'); fc.poke(0xBF, 0); fc.step(r2[:120]); fc.save('p120')
out = open('work/l65/r2shift.res.tsv', 'a', newline='\n')
for s in range(S0, S1 + 1):
    rows = r2[:149] + [()] * s + r2[149:] + [()] * 20
    fn = f'work/l65/lines/r2d5_s{s}.txt'
    with open(fn, 'w', newline='\n') as f:
        f.write(f'# l65 fallback: a56 r2d5 (work/l63p/dm_r2d5_kill.txt) with {s} blank rows inserted before row 150 (row 1 = 6-5 control row)\n')
        for r in rows[:-20]: f.write(('+'.join(r) if r else '') + '\n')
    n = 0
    for v in vals:
        fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.save('q')
        o = outcome(fc.run_batch('q', [rows[120:]], record='last', stops=STOPS)[0])
        if o[0]:
            out.write(f'{v}\t{fn}\t{o[0] + 120}\t{o[1]}\n'); out.flush(); n += 1
    print('s', s, 'kills', n, flush=True)
fc.close()

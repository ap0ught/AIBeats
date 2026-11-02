"""NesHawk replay of a 6-1 head-start rows file (row 1 = 6-1 control row 30063) from ref4751/16_6-1_control (+ TAS rows up to
30062 if the state is earlier), optional pokes; writes one line per frame: f X y hp np item room BF  -> <out>.
python work/l61p/nhpre61.py <rows> <out> [--pokes 0xBF=v,...] [--junk seed]"""
import sys, random
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l61p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import XY
a = sys.argv[1:]
pk = {}; JS = -1
if '--pokes' in a:
    i = a.index('--pokes'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
if '--junk' in a:
    i = a.index('--junk'); JS = int(a[i + 1]); del a[i:i + 2]
rows = [l.strip() for l in open(a[0]) if l.strip() and not l.startswith('#')]
rows = [() if r == '-' else tuple(r.split('+')) for r in rows]
TR = A.tas_rows()
e = C.open_emu('l61p_nhpre.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/16_6-1_control'); f0 = st['frame']; print('state frame', f0, flush=True)
    if f0 < 30062:
        e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 30063)]); f0 = 30062
    for k, v in pk.items(): e.poke(k, v)
    if JS >= 0:
        rng = random.Random(JS)
        for ad in range(0x400, 0x4A8): e.poke(ad, rng.randrange(256))
    sub = rows[f0 - 30062:]
    _, rams = e.run_ram(sub)
    with open(a[1], 'w') as fo:
        for i, m in enumerate(rams):
            X, y = XY(m)
            fo.write(f'{f0 + 1 + i} {X} {y} {m[0x65]} {m[0x64]} {m[0xC9]} {m[0x6E]} {m[0xBF]}\n')
    m = rams[-1]; print('end', f0 + len(rams), XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], flush=True)
finally:
    e.close()

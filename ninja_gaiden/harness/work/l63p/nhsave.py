"""NesHawk: ref state + TAS rows to F0 + pokes + rows file (first n rows) -> save state NAME (states/NAME.State). Prints the frame and RAM bits.
python work/l63p/nhsave.py <ref> F0 rowsfile n NAME [--poke a=v,..]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l63p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import XY
a = sys.argv[1:]
PK = ''
if '--poke' in a:
    i = a.index('--poke'); PK = a[i + 1]; del a[i:i + 2]
stn, F0, RF, n, NAME = a[0], int(a[1]), a[2], int(a[3]), a[4]
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
rows = [row(l.strip()) for l in open(RF) if not l.startswith('#')][:n]
TR = A.tas_rows()
e = C.open_emu('l63p_nhsave.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, F0 + 1)])
    for kv in [p for p in PK.split(',') if p]:
        k_, v_ = kv.split('='); e.poke(int(k_, 0), int(v_, 0))
    _, rams = e.run_ram(rows)
    m = rams[-1]
    e.save(NAME)
    print('saved', NAME, 'frame', F0 + len(rows), 'XY', XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF], '3E', m[0x3E], '62', m[0x62])
finally:
    e.close()

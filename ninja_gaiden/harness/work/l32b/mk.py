"""rows = legal TAS rows (lag, optional --nob) appended to hist; or a rows file. Save Mesen state + history.
python work/l32b/mk.py <mst> <hist> <tag> (--tas lag n [--nob] | --rows file [--n k])"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
import a56_common as A
from ng.solve import common as C, legality as L
from ng import fastcore as F
a = sys.argv[1:]
mst, hf, tag = a[:3]
H = C.rows_of(hf); f0 = len(H)
if '--tas' in a:
    i = a.index('--tas'); lag, n = int(a[i+1]), int(a[i+2]); TR = A.tas_rows()
    want = [tuple(x for x in TR[f0 - lag + k] if not ('--nob' in a and x == 'B')) for k in range(n)]
    en = L.Enforcer(H[-1900:]); rows = [tuple(sorted(en.emit(w))) for w in want]
else:
    i = a.index('--rows'); rows = C.rows_of(a[i+1])
    if '--n' in a: rows = rows[:int(a[a.index('--n')+1])]
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(mst, 'rb').read()); fc.load('s')
if rows: fc.step(rows, record='last')
r = fc.ram(); fc.save('e'); fc.save_file('e', f'states/mesen/l32b_{tag}.mst', frame=f0 + len(rows)); fc.close()
C.write_inputs(f'work/l32b/h_{tag}.inputs.txt', list(H) + list(rows), f'hist {hf} + {len(rows)} rows')
s52 = r[0x52]; X = s52 * 256 + r[0x51] + r[0x86]
print(tag, 'frame', f0 + len(rows), 'X', X, 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF], 'item', r[0xC9])

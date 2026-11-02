"""python work/l32p/mkst.py <mst> <hist> <rows file> <tag> [--bf v] [--n rows]  -> states/mesen/l32p_<tag>.mst + work/l32p/h_<tag>.inputs.txt"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
bf = opt('--bf', -1); n = opt('--n', -1)
mst, hf, rf, tag = a[:4]
H = C.rows_of(hf); rows = C.rows_of(rf) if rf != '-' else []
if n >= 0: rows = rows[:n]
fc = core(mst)
if bf >= 0: fc.poke(0xBF, bf)
if rows: fc.step(rows, record='last')
r = fc.ram(); fc.save('e'); fc.save_file('e', f'states/mesen/l32p_{tag}.mst', frame=len(H) + len(rows)); fc.close()
C.write_inputs(f'work/l32p/h_{tag}.inputs.txt', list(H) + list(rows), f'hist {hf} + {rf}[:{len(rows)}]')
X = r[0x52]*256 + r[0x51] + r[0x86]
print(tag, 'frame', len(H) + len(rows), 'X', X, 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF], 'anim', r[0x80])

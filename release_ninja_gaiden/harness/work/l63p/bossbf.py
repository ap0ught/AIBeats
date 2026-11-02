"""Boss kill vs arrival phase (Mesen): from TAS state F0, poke ADDR = v for each v, play the rows, stop at $66 == 0.
python work/l63p/bossbf.py F0 rowsfile skip [--addr 0xBF] [--vals 0-255] [--pre 'a=v,b=w']
Prints kill frame (F0 + rows played) per value, grouped."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
AD = int(opt('--addr', '0xBF'), 0); VS = opt('--vals', '0-255'); PRE = opt('--pre', '')
F0, RF, SK = int(a[0]), a[1], int(a[2])
rows = [row(l.strip()) for l in open(RF) if not l.startswith('#')][SK:]
if VS.count('-') == 1 and ',' not in VS:
    x, y = map(int, VS.split('-')); vals = list(range(x, y + 1))
else: vals = [int(v) for v in VS.split(',')]
fc = core_at(F0)
for kv in [p for p in PRE.split(',') if p]:
    k, v = kv.split('='); fc.poke(int(k, 0), int(v, 0))
base = fc.ram()
print('base', hex(AD), base[AD], 'rows', len(rows), flush=True)
fc.save('b0')
res = {}
for v in vals:
    fc.load('b0'); fc.poke(AD, v); fc.save('b'); fc._ka_slot = 'b'
    r = fc.run_batch('b', [rows], record='last', stops=[(0x66, '==', 0)])[0]
    s = r.states[-1] if r.states else {}
    res[v] = (F0 + r.rows_played, s.get('hp65'), s.get('t63'))
groups = {}
for v, k in res.items(): groups.setdefault(k, []).append(v)
for k, vs in sorted(groups.items()): print('kill', k[0], 'hp', k[1], 'T', k[2], 'n', len(vs), vs if len(vs) < 40 else (vs[:20], '...'))
fc.close()

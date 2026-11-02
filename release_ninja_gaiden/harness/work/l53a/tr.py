"""l53a: trace one row spec from a TAS state (or a .mst). python work/l53a/tr.py F0|path.mst F0 'Left*20,A+Right*2,...' [n] [--every k]
Rows start at F0+1. Prints X y xsub vy coll(8C) rflags(84) anim(80) hp np room inv and enemy slots (type,x,y) on request."""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53a')
from lib import *
a = sys.argv[1:]
EV = 1
if '--every' in a:
    i = a.index('--every'); EV = int(a[i+1]); del a[i:i+2]
EN = '--en' in a
ENS = range(8)
if EN:
    i = a.index('--en'); del a[i]
    if i < len(a) and a[i][0] == 's': ENS = [int(c) for c in a[i][1:]]; del a[i]
POKE = {}
if '--poke' in a:
    i = a.index('--poke'); 
    for p in a[i+1].split(','):
        k, v = p.split('='); POKE[int(k, 16)] = int(v)
    del a[i:i+2]
if a[0].endswith('.mst'):
    fc = core(a[0]); F0 = int(a[1]); a = a[1:]
else:
    F0 = int(a[0]); fc = core_at(F0)
for k, v in POKE.items(): fc.poke(k, v)
fc.save('b'); fc._ka_slot = 'b'
spec = a[1]; n = int(a[2]) if len(a) > 2 else 0
rows = []
for part in spec.split(','):
    r, k = part.split('*') if '*' in part else (part, '1')
    rows += [row(r)] * int(k)
if n: rows = (rows + [rows[-1]] * n)[:n]
print('legal:', legal_ok(rows) or 'ok')
st = fc.run_batch('b', [rows], record='all')[0].states
for j, s in enumerate(st):
    if j % EV and j != len(st) - 1: continue
    X, y = RXY(s)
    e = ''
    if EN: e = ' '.join(f"{q}:t{s[f't{q}']}:{s[f'ex{q}']},{s[f'ey{q}']}" for q in ENS)
    print(F0 + 1 + j, f'{P(rows[j]):10s}', X, y, 'xs', s['xsub'], 'vy', s['vy'], 'c %02x' % s['coll'], 'f %02x' % s['rflags'], 'a', s['anim'], 'hp', s['hp65'], 'np', s['np64'], 'rm', s['room6e'], 'inv', s['inv95'], e)
fc.close()

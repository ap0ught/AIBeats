"""l53b: trace a rows file from a .mst or TAS frame. python work/l53b/trf.py <mst|tasF> F0 rows.txt [--every k] [--poke 65=3] [--en]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
EV = opt('--every', 1); POKE = opt('--poke', ''); EN = '--en' in a
if EN: a.remove('--en')
src, F0, rf = a[0], int(a[1]), a[2]
rows = [row(l.strip()) for l in open(rf) if l.strip() and not l.startswith('#')]
fc = core(src) if src.endswith('.mst') else core_at(F0)
for p in [q for q in POKE.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
st = fc.run_batch('b', [rows], record='all')[0].states
fc.close()
prev = None
for j, s in enumerate(st):
    X, y = RXY(s); ev = []
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    prev = s
    if j % EV and not ev and j != len(st) - 1: continue
    e = ''
    if EN: e = ' '.join(f"{q}:t{s[f't{q}']}:{s[f'ex{q}']},{s[f'ey{q}']}" for q in range(8) if s[f't{q}'])
    print(F0 + 1 + j, f'{P(rows[j]):10s}', X, y, 'c %02x' % s['coll'], 'a', s['anim'], 'hp', s['hp65'], 'np', s['np64'], 'rm', s['room6e'], 'inv', s['inv95'], ' '.join(ev), e)

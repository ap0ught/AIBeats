"""l53a: run 5-3 stage rows (row 1 = the 5-3 control row) on a real entry state and on the TAS state (26607, hp poke),
compare Ryu per row. python work/l53a/run53.py rows.txt <mst before control> <F> [--every k] [--pad n]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
EV = opt('--every', 20); PAD = opt('--pad', 30); HP = opt('--hp', 12)
rows = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')] 
mst, F = a[1], int(a[2])
rr = rows + [()] * PAD
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
st = fc.run_batch('b', [rr], record='all')[0].states
fc2 = core(tas_mst(26607)); fc2.poke(0x65, HP); fc2.save('b'); fc2._ka_slot = 'b'
st2 = fc2.run_batch('b', [rr], record='all')[0].states
fc.close(); fc2.close()
prev = None; first = None
for i, (s, t) in enumerate(zip(st, st2)):
    f = F + i; ev = []
    if RXY(s) != RXY(t) and first is None: first = f; ev.append(f'FIRST DIFF vs TAS-state run {RXY(t)}')
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    if ev or (EV and i % EV == 0):
        print(f, f'(stage row {i+1})', P(rr[i]), RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'], 'BF', s['bf'], ' '.join(ev))
    prev = s
print('first diff', first)

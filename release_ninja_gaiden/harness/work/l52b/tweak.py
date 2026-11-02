"""Replay a power-on file from the d3 state with row overrides; report trigger/hp/np. python work/l52b/tweak.py file 'f1-f2=Row;...'"""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
from ng.inputs import read_inputs
rows = [tuple(r) for r in read_inputs(sys.argv[1])]
for part in [p for p in (sys.argv[2] if len(sys.argv) > 2 else '').split(';') if p]:
    k, v = part.split('=')
    x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
    for f in range(x, y + 1): rows[f - 1] = row(v)
fc = core('states/mesen/l52a_d3_25517.mst')
_, st, _ = fc.step(rows[25517:], record='all'); fc.close()
prev = None; trig = None
for i, s in enumerate(st):
    f = 25518 + i
    if f > 26840 and prev and (s['hp65'] != prev['hp65'] or s['np64'] != prev['np64']): print(' ', f, RXY(s), 'hp', s['hp65'], 'np', s['np64'])
    if trig is None and s['room6e'] == 26 and s['e5c'] == 0 and f > 26530: trig = f
    prev = s
s = st[-1]; print('trigger', trig, 'end room', s['room6e'], 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'])

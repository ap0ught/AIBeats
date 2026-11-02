"""Trace macro rows from any Mesen state: python work/l43/rtrace.py <mst> <frame0> <spec> [step] [e]"""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
from mk import parse
mst, F0, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]; st = int(sys.argv[4]) if len(sys.argv) > 4 else 1
en = A.Enforcer([()] * 40); rows = [tuple(sorted(en.emit(w))) for w in parse(spec)]
fc = core(mst); _, recs, _ = fc.step(rows, record='all'); fc.close()
for i, s in enumerate(recs):
    if i % st and i != len(recs) - 1: continue
    f = F0 + 1 + i
    print(f, P(rows[i]), 'rm', s['room'], 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'rf', hex(s['rflags']), 'coll', hex(s['coll']), 'anim', s['anim'],
          '| TAS', TX.get(f), TY.get(f), (' '.join(f's{j}t{tt}@{x},{y}' for j, tt, x, y in enemies_s(s)) if len(sys.argv) > 5 else ''))

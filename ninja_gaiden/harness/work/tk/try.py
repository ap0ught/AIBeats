"""Play a prefix + a wanted-row spec (legalized) and print Ryu every k frames.
    python work/tk/try.py <state> <prefix> N <hist> "<spec: ROW*n,ROW*n,...>" [k]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, legality as L
from ng.mode import TICKS
import a56_common as A
st, pf, N, hf, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
k = int(sys.argv[6]) if len(sys.argv) > 6 else 2
pre = C.rows_of(pf)[:N]; hist = C.rows_of(hf)
want = []
for part in spec.split(','):
    r, n = part.split('*'); want += [tuple(x for x in r.split('+') if x and x != '-')] * int(n)
en = L.Enforcer((hist + pre)[-1900:]); rows = [en.emit(w) for w in want]
e = C.open_emu('tk_try.log')
try:
    e.tick(TICKS); e.load(st); e.run(pre); tr = A.play_trace(e, rows)
finally:
    e.close()
for i, s in enumerate(tr):
    if i % k == 0 or s['room'] != tr[0]['room']:
        print(i, '+'.join(rows[i]) or '-', 'room', s['room'], 'X', C.abs_x(s), 'x', s['x'], 'y', s['y'], hex(s['rflags']), hex(s['coll']), 'anim', s['anim'])
    if s['room'] != tr[0]['room']: break

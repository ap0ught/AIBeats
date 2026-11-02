"""history file (power-on rows to F) + beam rows file (rows from F+1) + c3b rows from R onward; run to trigger.
python work/l51c/bgraft.py hist beamrows R [out]"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
H = [tuple(sorted(r)) for r in C.rows_of(sys.argv[1])]; Bm = [tuple(sorted(r)) for r in C.rows_of(sys.argv[2])]
R = int(sys.argv[3]); out = sys.argv[4] if len(sys.argv) > 4 else None
c3b = [tuple(sorted(r)) for r in C.rows_of('logs/l51_c3b_poweron.inputs.txt')]
F0 = 24270
want = [set(x) for x in H[F0:] + Bm + c3b[R - 1:24760]]
hist = H[:F0]; full = enforce(want, hist)
fc = core('states/mesen/l51c_c3a_24270.mst')
st = fc.run_batch('s', [full], record='all')[0].states
hp = None; trig = None
for i, s in enumerate(st):
    f = F0 + 1 + i
    if hp is not None and s['hp65'] != hp: print('hp', hp, '->', s['hp65'], 'at', f, RXY(s))
    hp = s['hp65']
    if f == len(H) + len(Bm): print('join', line(f, s))
    if s['e5c'] == 0: trig = f; print('TRIGGER', line(f, s)); break
print('5-2 control', trig + 280 if trig else None, 'legal', legal_ok(full, hist) or 'ok')
fc.close()
if out and trig:
    with open(out, 'w', encoding='utf-8') as fo:
        fo.write(f'# frames={trig + 280} l51c bird line: {sys.argv[1]} + {sys.argv[2]} + c3b rows from {R}\n')
        for x in H[:F0] + full[:trig - F0] + [()] * 280: fo.write(('+'.join(x) if x else '') + '\n')
    print('wrote', out)

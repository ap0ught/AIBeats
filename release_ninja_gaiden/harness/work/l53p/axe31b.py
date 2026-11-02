"""Room-31 axe boost in the AIR (hit while jumping from the pillar top to the X-128 wall). From TAS state 28583 (Ryu on the
pillar top X 177 y 128), $BF poked to v, wait w frames (idle), then the TAS's approach rows (Left 12, A+Left 2, Left ...),
then idle. Exit = room 32. python work/l53p/axe31b.py [--wmax 40] [--hold Left|-]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
WMAX = opt('--wmax', 40); HOLD = opt('--hold', 'Left'); F0 = opt('--f0', 28583)
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
L = 0x02; AL = 0x82; H = L if HOLD == 'Left' else 0
def rows(w):
    return [0] * w + [L] * 12 + [AL, AL] + [L] * 14 + [H] * 60
res = []
VSTEP = opt('--vstep', 1)
for v in range(0, 256, VSTEP):
    fc.load('b'); fc.poke(0xBF, v); fc.save('p')
    rr = fc.run_batch('p', [rows(w) for w in range(WMAX + 1)], record='all')
    for w, r in enumerate(rr):
        st = r.states; ex = None; hits = []
        for i, s in enumerate(st):
            if i and s['hp65'] < st[i-1]['hp65']: hits.append((F0 + 1 + i, RXY(st[i-1])))
            if s['room6e'] == 32: ex = F0 + 1 + i; break
        if ex:
            res.append((ex, v, w, hits[:2]))
            print(f'EXIT v {v} w {w} exit {ex} (TAS 28629) hits {hits[:2]} hp {st[-1]["hp65"]}', flush=True)
    print(f'v {v} done, hits in {sum(1 for r in rr if any(r.states[i]["hp65"] < r.states[i-1]["hp65"] for i in range(1, len(r.states))))} of {len(rr)} runs, exits so far {len(res)}', flush=True)
    fc.drop('p')
res.sort()
print('BEST', res[:20]); print('n exits', len(res), 'of', len(range(0, 256, VSTEP)) * (WMAX + 1))
fc.close()

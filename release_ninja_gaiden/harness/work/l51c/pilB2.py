"""Stage B: from a stage-A variant (power-on prefix rows to 24,400), run Right, stand w frames starting at p, run, jump at
p + w + d (A+Right x2), then Right / blank (knockback) ... Score: first frame on the pillar-B top (y 128, X 2,650-2,700,
on ground). python work/l51c/pilB.py "a,b,c" out.jsonl"""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
a, b, c = [None if x == 'None' else int(x) for x in sys.argv[1].split(',')]
out = sys.argv[2]
F0 = 24270; MST = 'states/mesen/l51c_c3a_24270.mst'
rows = [tuple(sorted(r)) for r in C.rows_of('logs/l51_c3a_poweron.inputs.txt')]; hist = rows[:F0]
END = 24400
want = [{'Right'} for _ in range(END - F0)]
for f in (a, a + 1): want[f - F0 - 1] = {'A', 'Right'}
for t in (b, c):
    if t:
        for f in (t, t + 1):
            s = want[f - F0 - 1]; s.discard('Right'); s |= {'B', 'Up'}
pre = enforce(want, hist)
fc = core(MST); fc.save('b'); fc._ka_slot = 'b'
r = fc.run_batch('b', [pre], record='last', keep=True, prefix='p')[0]
print(line(END, r.states[-1]), flush=True)
fc.save('q'); fc._ka_slot = 'q'
h2 = hist + list(pre)
cands = []; seen = set()
for p in (24400, 24424):
    for w in range(0, 34):
        for d in range(0, 28, 1):
            wt = [{'Right'}] * (p - END) + [set()] * w + [{'Right'}] * d + [{'A', 'Right'}] * 2 + [{'Right'}] * 60
            wt = wt[:150]
            rr = enforce(wt, h2)
            if legal_ok(rr, h2) or tuple(rr) in seen: continue
            seen.add(tuple(rr)); cands.append(((p, w, d), rr))
print('cands', len(cands), flush=True)
fo = open(out, 'w')
for i in range(0, len(cands), 60):
    ch = cands[i:i+60]
    res = fc.run_batch('p1', [x for _, x in ch], record='all')
    for (k, rr), r in zip(ch, res):
        st = r.states; hp = st[0]['hp65']; hits = []; top = None
        for t, s in enumerate(st):
            X, y = RXY(s)
            if s['hp65'] != hp: hits.append((END + 1 + t, X, y, hp, s['hp65'])); hp = s['hp65']
            if top is None and y == 128 and 2650 <= X <= 2700 and not s['rf84'] & 4: top = END + 1 + t
        fo.write(json.dumps(dict(k=k, top=top, hits=hits)) + '\n')
    fo.flush()
fc.close()

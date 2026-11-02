"""l53b: repair a NesHawk pad-misread frame: from stage rows, keep rows < FA, search rows FA..FB-1 with row FM forced equal to row FM-1,
to reach the original Ryu key at frame FB (beam that tracks the original trajectory). python work/l53b/fixnh.py stage.txt FA FM FB out.txt"""
import sys, os
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
rf, FA, FM, FB, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
rows = [row(l.strip()) for l in open(rf) if l.strip() and not l.startswith('#')]
hist = rows[:FA - 27360]
fc = core('states/mesen/l53a_e4_27359.mst')
_, orig, _ = fc.step(rows[:FB - 27359 + 5], record='all')
fc.load(fc._ka_slot) if fc._ka_slot else None
fc.close()
fc = core('states/mesen/l53a_e4_27359.mst'); fc.step(hist, record='last'); fc.save('s0'); fc._ka_slot = 's0'
O = {27360 + i: s for i, s in enumerate(orig)}
KEYF = ('x86', 'xsub', 'y8a', 'vy', 'vy_sub', 'rf84', 'coll', 'scr_lo', 'scr_hi')
def key(s): return tuple(s[k] for k in KEYF)
AL = [row(x) for x in 'Up|Right|Left|A+Left|A+Right|-|A|Up+Right|Up+Left|A+Up+Right|A+Up+Left|Left+Up|Right+Up'.split('|')]
nodes = [('s0', (), A.Enforcer(hist))]
for f in range(FA, FB + 1):
    out = []
    for ni, (slot, rr, en) in enumerate(nodes):
        kids = {}
        for w in AL:
            if f == FM: w = rr[-1]
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if f == FM and lg != rr[-1]: continue
            if ('Left' in lg and 'Right' in lg) or ('Up' in lg and 'Down' in lg): continue
            kids.setdefault(lg, e2)
        kl = list(kids.items())
        res = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{f}n{ni}_')
        for (lg, e2), r in zip(kl, res):
            if r.states: out.append((r.slot, rr + (lg,), e2, r.states[-1]))
    fc.drop_prefix(f'g{f-1}n')
    o = O[f]
    sc = sorted(out, key=lambda n: abs(RXY(n[3])[0] - RXY(o)[0]) + abs(RXY(n[3])[1] - RXY(o)[1]) + abs(n[3]['xsub'] - o['xsub']) / 256)
    seen = set(); nodes = []
    for n in sc:
        k = key(n[3]) + (n[1][-1],)
        if k in seen: continue
        seen.add(k); nodes.append(n[:3])
        if f == FB and key(n[3]) == key(o):
            print('FOUND', f, [P(x) for x in n[1]]); 
            new = rows[:FA - 27360] + list(n[1]) + rows[FB - 27360 + 1:]
            print('legal', legal_ok(new))
            open(OUT, 'w').write('# fixnh\n' + '\n'.join(P(x) for x in new) + '\n'); fc.close(); sys.exit()
        if len(nodes) >= int(os.environ.get("W", "400")): break
    print(f, 'best', RXY(sc[0][3]) if sc else None, 'orig', RXY(o), flush=True)
print('not found'); fc.close()

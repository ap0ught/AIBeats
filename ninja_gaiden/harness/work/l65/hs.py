"""Per-phase heart search on podP1 (Mesen). PRE = podP1 (pod dead row 123) + Right x33 (Ryu X 110 on row 156). Then jump cycles of
44 rows (A rows 0-1, Right rows r0..kR-1, slash cycle Down|Down+B|B|-|- from row o, Left from row kL; 6-7 heart hits per jump from
X ~110 and back to X ~108-110 on landing), each preceded by g blank rows. Beam over cycles (width B), scored by hits, rows and damage;
the first cycle's start covers hd(bf) - 12 .. hd(bf) + 14. Kill = $66 0 in stage 21 with hp > 0.
python work/l65/hs.py <vals> [--width 3] [--res work/l65/hs.res.tsv]
Writes work/l65/lines/hs_<bf>.txt (rows from the control row to the kill row) and appends 'bf line kill hp' to --res."""
import sys, os, time
sys.path.insert(0, 'work/l65')
from lib65 import *
from ng.fastcore import free_ram_gb
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
B = int(opt('--width', '3')); RES = opt('--res', 'work/l65/hs.res.tsv'); MAXL = int(opt('--levels', '5'))
vals = []
for p in a[0].split(','):
    if '-' in p: x, y = map(int, p.split('-')); vals += list(range(x, y + 1))
    else: vals.append(int(p))
SPECS = [(6, 8, 40, 2), (7, 10, 38, 0), (6, 9, 38, 3), (8, 10, 40, 1), (9, 11, 40, 2), (6, 8, 36, 2)]
def cycle(sp):
    r0, kR, kL, o = sp
    rr = []
    for t in range(44):
        r = set()
        if t < 2: r.add('A')
        if t >= kL: r.add('Left')
        else:
            if r0 <= t < kR: r.add('Right')
            k = t - o
            if k >= 0:
                ph = k % 5
                if ph == 0: r.add('Down')
                elif ph == 1: r |= {'Down', 'B'}
                elif ph == 2: r.add('B')
        rr.append(tuple(sorted(r)))
    return rr
CYC = {sp: cycle(sp) for sp in SPECS}
HD = {}
for l in open('work/l65/fb1.out'):
    p = l.split()
    if len(p) > 2 and p[1] == 'hd': HD[int(p[0])] = int(p[2])
P1 = rows_of('work/l65/podP1.txt'); PRE = P1 + [('Right',)] * 33
HIST = [()] * 150
L_PRE = K.Legal(HIST + PRE)
fc = core65()
fc.load('c0'); fc.poke(0xBF, 0); fc.step(PRE[:120]); fc.save('p120')
os.makedirs('work/l65/lines', exist_ok=True)
out = open(RES, 'a', newline='\n')
for v in vals:
    if free_ram_gb() < 1.5: print('low RAM, stop before', v, flush=True); break
    t0 = time.time()
    fc.load('p120'); fc.poke(0xBF, (v + 120) % 256); fc.step(PRE[120:]); fc.save(f'n0')
    nodes = [('n0', [], L_PRE, 16, 16)]      # slot, rows after PRE, Legal, hp, heart
    best = None
    for lv in range(MAXL):
        if lv == 0:
            gs = list(range(max(0, HD[v] - 12 - len(PRE) - 1), max(0, HD[v] + 14 - len(PRE) - 1) + 1))
        else:
            gs = list(range(0, 9))
        pool = []
        for ni, (sl, rr, Lx, hp0, h0) in enumerate(nodes):
            cands = []
            for g in gs:
                for sp in SPECS:
                    rows = [()] * g + CYC[sp]
                    L2 = Lx.copy(); ok = True
                    for r in rows:
                        if L2.why(r): ok = False; break
                        L2.push(r)
                    if ok: cands.append(((g, sp), rows, L2))
            if not cands: continue
            res = fc.run_batch(sl, [c[1] + [()] * 8 for c in cands], record='all', stops=STOPS)
            for (spec, rows, L2), r in zip(cands, res):
                st = r.states
                n = len(rows)
                if r.status == 1 and st[-1]['boss'] == 0 and st[-1]['hp65'] > 0 and st[-1]['st6d'] == 21:
                    k = len(PRE) + len(rr) + r.rows_played
                    if best is None or (k, -st[-1]['hp65']) < (best[0], -best[1]):
                        best = (k, st[-1]['hp65'], PRE + rr + rows[:r.rows_played])
                    continue
                if r.status == 1 or len(st) < n: continue
                hp = min(s['hp65'] for s in st)
                if hp < 1 or st[n - 1]['st6d'] != 21: continue
                if st[n - 1]['rf84'] & 4: continue      # must be on the ground at the end of the cycle
                heart = st[n - 1]['boss']
                tot = len(rr) + n
                sc = tot + 6.5 * heart + 25 * (16 - hp)
                pool.append((sc, ni, spec, rows, L2, hp, heart, st[n - 1]['x86']))
        if best and lv >= 1:
            # stop when no node can still beat the kill
            pass
        pool.sort(key=lambda q: q[0])
        new = []; seen = set()
        for q in pool:
            sc, ni, spec, rows, L2, hp, heart, X = q
            kk = (len(nodes[ni][1]) + len(rows), heart, hp, X)
            if kk in seen: continue
            seen.add(kk)
            sl = nodes[ni][0]
            rres = fc.run_batch(sl, [rows], record='last', keep=True, prefix=f'v{v}L{lv}j{len(new)}_')
            new.append((rres[0].slot, nodes[ni][1] + rows, L2, hp, heart))
            if len(new) >= B: break
        fc.drop_prefix(f'v{v}L{lv - 1}j') if lv else None
        nodes = new
        if os.environ.get('HSV'): print('  lv', lv, 'pool', len(pool), [(round(q[0]), q[2], q[5], q[6], q[7]) for q in pool[:3]], flush=True)
        if not nodes: break
        if best and min(len(PRE) + len(n_[1]) for n_ in nodes) >= best[0]: break
    fc.drop_prefix(f'v{v}L')
    if best:
        k, hp, rows = best
        L = K.Legal(HIST); ok = True
        for r in rows:
            if L.why(r): ok = False; break
            L.push(r)
        fn = f'work/l65/lines/hs_{v}.txt'
        with open(fn, 'w', newline='\n') as f:
            f.write(f'# l65 hs.py bf {v}: podP1 + Right x33 + heart jump cycles; kill row {k} (row 1 = 6-5 control row), hp {hp}\n')
            for r in rows: f.write(('+'.join(r) if r else '') + '\n')
        if ok: out.write(f'{v}\t{fn}\t{k}\t{hp}\n'); out.flush()
        print(v, 'hd', HD[v], 'KILL', k, 'hp', hp, 'legal', ok, f'{time.time() - t0:.0f}s', flush=True)
    else:
        print(v, 'hd', HD[v], 'none', f'{time.time() - t0:.0f}s', flush=True)
fc.close()

"""2-1 room 3 from the pillar top to the room exit along the (legalized) TAS line, with a brute-forced post window.

    python work/a12r3/r3_pipe.py [--minutes 50] [--out states/tmp/a12r3_r3pipe.inputs.txt] [--ka 4500] [--kend 5068]

1. a12_chain_1-2_end + states/tmp/a12r2_r3_best.inputs.txt[:1167] = pillar top (TAS 4388 + 208, 1 px behind).
2. legalized TAS rows 4389 .. KA.
3. stage 1 (the jump toward the post): Right x a, Right+A x h, Right ... ; states at TAS-time KB kept by best X
   (distinct, alive, top --keep).
4. stage 2 from each: grammar Right/Left/Right/Right+A/-/Right+A; then Right held while looking for a re-sync with
   the TAS line (|dX| <= 1, |dy| <= 1, same vy, k in 4535..4600); legalized TAS rows from k to KEND must stay in sync
   (tol 2). Score = our frame - k (lag). Best full-sync rows -> --out; best partial -> *_part.inputs.txt.
"""
import itertools
import sys
import time
sys.path.insert(0, 'ng/stages')
sys.path.insert(0, '.')
import a56_common as C  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v)
    return d


minutes = opt('--minutes', 50.0)
out = opt('--out', 'states/tmp/a12r3_r3pipe.inputs.txt')
KA = opt('--ka', 4500)
KB = opt('--kb', 4527)
KEND = opt('--kend', 5068)
keep = opt('--keep', 4)
T = C.tas_trace()
R = C.tas_rows()


def lw(r):
    r = set(r)
    if 'Up' in r and 'Down' in r:
        r.discard('Down')
    if 'Left' in r and 'Right' in r:
        r.discard('Left')
    return tuple(r)


def same(s, t, tol=1):
    return s['room'] == t['room'] and abs(C.abs_x(s) - C.abs_x(t)) <= tol and abs(s['y'] - t['y']) <= tol and \
        (tol > 1 or s.get('vy') == t.get('vy'))


rows = [tuple(r) for r in read_inputs('states/tmp/a12r2_r3_best.inputs.txt')][:1167]
hist = [tuple(r) for r in read_inputs('logs/a12_chain.inputs.txt')]
K0 = 4388
e = C.open_emu('a12r3_probe.log')
t0 = time.time()
try:
    e.tick(TICKS)
    e.load('a12_chain_1-2_end')
    st = e.run(rows)
    off = st['frame'] - K0
    print('pillar', st['frame'], C.abs_x(st), st['y'], 'vs TAS', C.abs_x(T[K0]), T[K0]['y'], 'offset', off, flush=True)
    en = C.Enforcer((hist + rows)[-1900:])
    pre = [en.emit(lw(R[k - 1])) for k in range(K0 + 1, KA + 1)]
    st = e.run(pre)
    print('at KA', KA, 'ours', C.abs_x(st), st['y'], 'TAS', C.abs_x(T[KA]), T[KA]['y'], flush=True)
    sid0 = e.msave()
    base = rows + pre
    # stage 1
    nb = KB - KA
    s1 = {}
    for aa in range(0, 16):
        for h in range(2, 10):
            want = [('Right',)] * aa + [('Right', 'A')] * h + [('Right',)] * max(0, nb - aa - h)
            want = want[:nb]
            en1 = en.copy()
            w = tuple(en1.emit(x) for x in want)
            e.mload(sid0)
            e.trace(True)
            e.run(list(w))
            tr = e.last_trace
            if any(s.get('dw') for s in tr):
                continue
            s = tr[-1]
            key = (C.abs_x(s), s['y'], s.get('vy'), s.get('x'), s.get('xsub'))
            if key not in s1:
                s1[key] = (w, en1, (aa, h))
    ranked = sorted(s1.items(), key=lambda kv: (-kv[0][0], kv[0][1]))
    print('stage 1:', len(s1), 'distinct; top', [(k[:3], v[2]) for k, v in ranked[:8]], flush=True)
    print('TAS at KB', C.abs_x(T[KB]), T[KB]['y'], T[KB].get('vy'), flush=True)
    gram = [(('Right',), range(0, 7)), (('Left',), (0, 2, 3)), (('Right',), range(0, 7)), (('Right', 'A'), (2, 3, 4, 6, 8)),
            ((), (0, 2, 4, 6, 8, 10)), (('Right', 'A'), (2, 3))]
    best = None
    pbest = None
    n = 0
    for (key, (w1, en1, ah)) in ranked[:keep]:
        e.mload(sid0)
        e.run(list(w1))
        sid = e.msave()
        seen = set()
        print('stage 2 from', key[:3], ah, flush=True)
        for lens in itertools.product(*[g[1] for g in gram]):
            if time.time() - t0 > minutes * 60:
                break
            want = []
            for (r, _), k in zip(gram, lens):
                want += [r] * k
            enw = en1.copy()
            win = tuple(enw.emit(x) for x in want)
            if win in seen:
                continue
            seen.add(win)
            tailr = [enw.emit(('Right',)) for _ in range(60)]
            e.mload(sid)
            e.trace(True)
            e.run(list(win) + tailr)
            tr = e.last_trace
            n += 1
            if any(s.get('dw') for s in tr):
                continue
            hit = None
            for i, s in enumerate(tr):
                for k in range(4535, 4600):
                    if same(s, T[k]):
                        hit = (i, k)
                        break
                if hit:
                    break
            if not hit:
                continue
            i, k = hit
            lag = tr[i]['frame'] - k
            if best is not None and lag >= best[0]:
                continue
            e.mload(sid)
            en3 = en1.copy()
            rr = [en3.emit(x) for x in (list(win) + tailr)[:i + 1]]
            e.run(rr)
            fol = [en3.emit(lw(R[kk - 1])) for kk in range(k + 1, KEND + 1)]
            e.trace(True)
            e.run(fol)
            tf = e.last_trace
            bad = next((j for j, s in enumerate(tf) if not same(s, T[k + 1 + j], 2)), None)
            reach = k + 1 + (bad if bad is not None else len(fol)) - 1
            print(f'cand {ah} {lens} resync k {k} lag {lag} sync to TAS {reach}', flush=True)
            if bad is not None and (pbest is None or reach > pbest):
                pbest = reach
                write_inputs(out.replace('.inputs', '_part.inputs'), base + list(w1) + rr + fol[:bad],
                             f'2-1 room 3 partial: lag {lag}, in sync to TAS {reach} (window {ah} {lens})')
            if bad is None:
                best = (lag, ah, lens, k)
                allrows = base + list(w1) + rr + fol
                write_inputs(out, allrows, f'2-1 room 3 pillar -> TAS {KEND} lag {lag} (TAS line legalized, window '
                                           f'{ah} {lens})')
                print('NEW best lag', lag, 'end frame', tf[-1]['frame'], 'rows', len(allrows), f'evals {n} '
                      f'{time.time() - t0:.0f}s', flush=True)
    print('BEST', best, 'partial reach', pbest, 'evals', n, flush=True)
finally:
    e.close()

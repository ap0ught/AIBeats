"""Staged wall-jump / jump search: each stage = keep holding the previous direction i frames (i = 0..--maxoff), then
press D+A for h frames (h in --holds) and hold D; the stage goal must be met (alive). Per stage the --keep best
distinct states (earliest goal frame, then smallest y) go on to the next stage. Stage spec "D,room,cmp,gx,ylo,yhi"
with cmp ge / le / any (room -1 = any room); D may end with ":noA" to also try a plain direction change.

    python work/a12r3/stage_jumps.py <start> <rows> N <hist> <out> D0 "<stage1>" "<stage2>" ... [--maxoff 30]
        [--keep 6] [--horizon 120] [--holds 2,3,4,6,8]
Writes rows[:N] + the best full path up to the last goal frame.
"""
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


maxoff = opt('--maxoff', 30)
keep = opt('--keep', 6)
H = opt('--horizon', 120)
holds = [int(x) for x in opt('--holds', '2,3,4,6,8').split(',')]
start, f, N, hf, out, D0 = a[0], a[1], int(a[2]), a[3], a[4], a[5]
stages = []
for sp in a[6:]:
    d, room, cmp, gx, ylo, yhi = sp.split(',')
    noa = d.endswith(':noA')
    stages.append((d.split(':')[0], int(room), cmp, int(gx), int(ylo), int(yhi), noa))


def goal(s, g):
    _, room, cmp, gx, ylo, yhi, _n = g
    x = C.abs_x(s)
    if room >= 0 and s['room'] != room:
        return False
    if cmp == 'ge' and x < gx:
        return False
    if cmp == 'le' and x > gx:
        return False
    return ylo <= s['y'] <= yhi


rows = [tuple(r) for r in read_inputs(f)][:N]
hist = [tuple(r) for r in read_inputs(hf)]
e = C.open_emu('a12r3_probe.log')
t0 = time.time()
try:
    e.tick(TICKS)
    e.load(start)
    st = e.run(rows)
    f0 = st['frame']
    print('at', f0, C.abs_x(st), st['y'], 'room', st['room'], flush=True)
    beam = [(e.msave(), C.Enforcer((hist + rows)[-1900:]), [], D0)]
    for si, g in enumerate(stages):
        D = g[0]
        cands = {}
        evals = 0
        for sid, en, rr, Dp in beam:
            variants = [(i, h) for i in range(maxoff + 1) for h in holds] + ([(i, 0) for i in range(maxoff + 1)]
                                                                             if g[6] else [])
            for i, h in variants:
                en2 = en.copy()
                w = [en2.emit(() if Dp == '-' else (Dp,)) for _ in range(i)]
                if h:
                    if not en2.can_press('A'):
                        continue
                    w += [en2.emit((D, 'A')) for _ in range(h)]
                w += [en2.emit((D,)) for _ in range(H)]
                e.mload(sid)
                e.trace(True)
                e.run(w)
                tr = e.last_trace
                evals += 1
                hit = None
                for j, s in enumerate(tr):
                    if s.get('dw'):
                        break
                    if j >= i + h and goal(s, g):
                        hit = j
                        break
                if hit is None:
                    continue
                s = tr[hit]
                key = (s['frame'], C.abs_x(s), s['y'], s.get('vy'), s.get('xsub'))
                if key not in cands:
                    cands[key] = (rr + w[:hit + 1], (i, h))
        ranked = sorted(cands.items(), key=lambda kv: (kv[0][0], kv[0][2]))[:keep]
        print(f'stage {si + 1} {g[:6]}: {len(cands)} distinct of {evals} evals; best',
              [(k[:3], v[1]) for k, v in ranked[:5]], f'{time.time() - t0:.0f}s', flush=True)
        if not ranked:
            print('FAILED at stage', si + 1, flush=True)
            break
        for _, _, _, _ in beam:
            pass
        for sid, *_ in beam:
            e.mfree(sid)
        nb = []
        for k, (rr, ih) in ranked:
            e.load(start)
            e.run(rows)
            en = C.Enforcer((hist + rows)[-1900:])
            rr2 = [en.emit(x) for x in rr]
            assert rr2 == rr
            e.run(rr)
            nb.append((e.msave(), en, rr, D))
        beam = nb
        write_inputs(out, rows + ranked[0][1][0], f'stage_jumps: {si + 1} stages, goal frame {ranked[0][0][0]}')
        print('wrote', out, 'frame', ranked[0][0][0], flush=True)
finally:
    e.close()

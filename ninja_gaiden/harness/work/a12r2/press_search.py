"""Press-timing search (walls, chimneys, jumps): a node holds one direction every frame; a child presses A (2 frames)
with direction D2 (Left / Right) at some frame and then holds D2. A child is kept only if the press sent Ryu up
compared with not pressing (a jump or a wall jump). BFS by node frame; earliest frame with X >= gx (or <= gx with
--xle) and ylo <= y <= yhi wins. Every row goes through the legal Enforcer.
    python work/a12r2/press_search.py <start> <rows> N gx ylo yhi <hist> <out> [--dir Right] [--depth 4]
        [--horizon 140] [--room R] [--xle] [--minutes 20]
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


xle = "--xle" in a
if xle:
    a.remove("--xle")
D0 = opt('--dir', 'Right')
depth = opt('--depth', 4)
H = opt('--horizon', 140)
room = opt('--room', -1)
minutes = opt('--minutes', 20.0)
start, f, N, gx, ylo, yhi, hf, out = a[0], a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6], a[7]
rows = [tuple(r) for r in read_inputs(f)][:N]
hist = [tuple(r) for r in read_inputs(hf)]


def goal(s):
    x = C.abs_x(s)
    return (room < 0 or s['room'] == room) and (x <= gx if xle else x >= gx) and ylo <= s['y'] <= yhi


e = C.open_emu('a12r2_probe.log')
t0 = time.time()
try:
    e.tick(TICKS)
    e.load(start)
    st = e.run(rows)
    f0 = st['frame']
    print('at', f0, C.abs_x(st), st['y'], st['room'], flush=True)
    frontier = [(e.msave(), C.Enforcer((hist + rows)[-1900:]), [], 0, D0)]
    best = None
    seen = set()
    evals = 0
    while frontier and time.time() - t0 < minutes * 60:
        frontier.sort(key=lambda q: len(q[2]))
        sid, en, rr, dp, D = frontier.pop(0)
        if best is not None and f0 + len(rr) >= best[0]:
            continue
        e.mload(sid)
        en_b = en.copy()
        base = [en_b.emit((D,)) for _ in range(H - len(rr))]
        e.trace(True)
        e.run(base)
        tb = e.last_trace
        evals += 1
        hit = next((i for i, s in enumerate(tb) if goal(s)), None)
        if hit is not None and not any(s.get('dw') for s in tb[:hit + 1]):
            fr = tb[hit]['frame']
            if best is None or fr < best[0]:
                best = (fr, dp)
                print('NEW', fr, 'presses', dp, f'{time.time() - t0:.0f}s', flush=True)
                write_inputs(out, rows + rr + base[:hit + 1], f'press search frame {fr}')
        if dp >= depth:
            continue
        for i in range(0, len(base) - 6):
            if best is not None and tb[i]['frame'] >= best[0]:
                break
            if tb[i].get('dw') or (hit is not None and i >= hit):
                break
            for D2 in ('Left', 'Right'):
                e.mload(sid)
                en2 = en.copy()
                pre = [en2.emit((D,)) for _ in range(i)]
                if not en2.can_press('A'):
                    continue
                pr = [en2.emit((D2, 'A')), en2.emit((D2, 'A'))]
                if 'A' not in pr[0]:
                    continue
                post = [en2.emit((D2,)) for _ in range(3)]
                e.run(pre + pr + post)
                tr = e.last_trace
                evals += 1
                if tr[-1]['y'] >= tb[i + 4]['y'] - 1:
                    continue
                e.mload(sid)
                en3 = en.copy()
                r3 = [en3.emit((D,)) for _ in range(i)] + [en3.emit((D2, 'A')), en3.emit((D2, 'A'))]
                s3 = e.run(r3)
                key = (s3['frame'], C.abs_x(s3), s3['y'], s3.get('vy'), D2)
                if key in seen:
                    continue
                seen.add(key)
                frontier.append((e.msave(), en3, rr + r3, dp + 1, D2))
    print('BEST', best, 'evals', evals, f'{time.time() - t0:.0f}s', flush=True)
finally:
    e.close()

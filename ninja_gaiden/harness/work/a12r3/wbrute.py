"""Window brute force: every combination of segment lengths of a small input grammar, legalized by the Enforcer,
from our rows; earliest frame that meets the goal wins.

    python work/a12r3/wbrute.py <start> <rows> N <hist> <out> "<grammar>" "<goal>" [--tail Right] [--horizon 160]
        [--minutes 30] [--hpmin 0]

grammar: segments separated by ';', each "ROW:n1,n2,.." or "ROW:a-b" (lengths, inclusive range), ROW like Right+A,
  Left, - (nothing). Example: "Right:0-12;Left:0,2,3;Right:0-8;Right+A:2-6;-:0,4,8;Right+A:2"
goal: "room,cmp,gx,ylo,yhi" with cmp ge or le, e.g. "3,ge,412,0,90".
After the grammar, the tail row is held to the horizon. Duplicate legalized sequences are evaluated once.
Writes rows[:N] + the best legalized rows up to and including the goal frame.
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


tail = opt('--tail', 'Right')
H = opt('--horizon', 160)
minutes = opt('--minutes', 30.0)
hpmin = opt('--hpmin', 0)
start, f, N, hf, out, gram, goal = a[0], a[1], int(a[2]), a[3], a[4], a[5], a[6]


def prow(s):
    return tuple(x for x in s.split('+') if x and x != '-')


segs = []
for part in gram.split(';'):
    r, ns = part.split(':')
    if '-' in ns and ',' not in ns and not ns.startswith('-'):
        lo, hi = ns.split('-')
        lens = list(range(int(lo), int(hi) + 1))
    else:
        lens = [int(x) for x in ns.split(',')]
    segs.append((prow(r), lens))
groom, gcmp, gx, ylo, yhi = goal.split(',')
groom, gx, ylo, yhi = int(groom), int(gx), int(ylo), int(yhi)
trow = prow(tail)


def ok(s):
    x = C.abs_x(s)
    return (groom < 0 or s['room'] == groom) and (x >= gx if gcmp == 'ge' else x <= gx) and ylo <= s['y'] <= yhi


rows = [tuple(r) for r in read_inputs(f)][:N]
hist = [tuple(r) for r in read_inputs(hf)]
e = C.open_emu('a12r3_probe.log')
t0 = time.time()
try:
    e.tick(TICKS)
    e.load(start)
    st = e.run(rows)
    f0 = st['frame']
    print('at', f0, C.abs_x(st), st['y'], 'room', st['room'], 'hp', st['hp'], flush=True)
    sid = e.msave()
    en0 = C.Enforcer((hist + rows)[-1900:])
    best = None
    seen = set()
    n = 0
    for lens in itertools.product(*[s[1] for s in segs]):
        if time.time() - t0 > minutes * 60:
            print('time up', flush=True)
            break
        want = []
        for (r, _), k in zip(segs, lens):
            want += [r] * k
        want += [trow] * max(0, H - len(want))
        en = en0.copy()
        rr = tuple(en.emit(w) for w in want)
        if rr in seen:
            continue
        seen.add(rr)
        e.mload(sid)
        e.trace(True)
        e.run(list(rr))
        tr = e.last_trace
        n += 1
        hit = None
        for i, s in enumerate(tr):
            if s.get('dw') or s['hp'] < hpmin:
                break
            if best is not None and i >= best[0]:
                break
            if ok(s):
                hit = i
                break
        if hit is not None:
            best = (hit, lens)
            print('NEW', tr[hit]['frame'], 'lens', lens, f'{C.abs_x(tr[hit])},{tr[hit]["y"]} hp {tr[hit]["hp"]}',
                  f'evals {n} {time.time() - t0:.0f}s', flush=True)
            write_inputs(out, rows + list(rr[:hit + 1]), f'wbrute {gram} goal {goal}: frame {tr[hit]["frame"]}')
    print('BEST', (f0 + 1 + best[0]) if best else None, best, 'evals', n, f'{time.time() - t0:.0f}s', flush=True)
finally:
    e.close()

"""Replay the legalized TAS rows from a TAS frame k0 after our own rows, and report where we leave the TAS line.

    python work/a12r3/tasfollow.py <start> <rows> N <hist> k0 kend [--out f] [--tol 2]

After start + rows[:N] our state should equal (in position) TAS frame k0. Then rows TAS[k0 .. kend-1] (row k-1 leads to
frame k), legalized (L+R -> keep the held one, U+D -> drop Down, press cap via the Enforcer), are played. Prints our
(X, y) vs the TAS's per 10 frames and the first frame where |dX| or |dy| > tol (and the TAS rows around it).
--out writes rows[:N] + the legalized rows up to (not including) the first divergence.
"""
import sys
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


out = opt('--out', '')
tol = opt('--tol', 2)
start, f, N, hf, k0, kend = a[0], a[1], int(a[2]), a[3], int(a[4]), int(a[5])
rows = [tuple(r) for r in read_inputs(f)][:N]
hist = [tuple(r) for r in read_inputs(hf)]
T = C.tas_trace()
R = C.tas_rows()


def legal_want(r):
    r = set(r)
    if 'Up' in r and 'Down' in r:
        r.discard('Down')
    return tuple(r)


e = C.open_emu('a12r3_probe.log')
try:
    e.tick(TICKS)
    e.load(start)
    st = e.run(rows)
    s0 = T[k0]
    print('start', st['frame'], C.abs_x(st), st['y'], 'room', st['room'], '| TAS', k0, C.abs_x(s0), s0['y'],
          'room', s0['room'], flush=True)
    en = C.Enforcer((hist + rows)[-1900:])
    rr = [en.emit(legal_want(R[k - 1]), prefer='Right') for k in range(k0 + 1, kend + 1)]
    e.trace(True)
    e.run(rr)
    tr = e.last_trace
    bad = None
    for i, s in enumerate(tr):
        k = k0 + 1 + i
        t = T[k]
        dx, dy = C.abs_x(s) - C.abs_x(t), s['y'] - t['y']
        if s['room'] != t['room'] or abs(dx) > tol or abs(dy) > tol:
            bad = i
            print(f'DIVERGE at our {s["frame"]} = TAS {k}: ours {C.abs_x(s)},{s["y"]} r{s["room"]} hp{s["hp"]} | TAS '
                  f'{C.abs_x(t)},{t["y"]} r{t["room"]} hp{t["hp"]}', flush=True)
            for j in range(max(0, i - 12), min(len(tr), i + 4)):
                kk = k0 + 1 + j
                print(f'   TAS {kk} row {"+".join(R[kk - 1]) or "-"} -> ours {"+".join(rr[j]) or "-"}  ours '
                      f'{C.abs_x(tr[j])},{tr[j]["y"]}  TAS {C.abs_x(T[kk])},{T[kk]["y"]}')
            break
        if i % 20 == 0:
            print(f'  {s["frame"]} TAS {k}: {C.abs_x(s)},{s["y"]} vs {C.abs_x(t)},{t["y"]}', flush=True)
    if bad is None:
        print('IN SYNC to TAS', kend, 'our frame', tr[-1]['frame'])
        bad = len(rr)
    if out:
        write_inputs(out, rows + rr[:bad], f'tasfollow from TAS {k0}, {bad} rows in sync')
        print('wrote', out, len(rows) + bad)
finally:
    e.close()

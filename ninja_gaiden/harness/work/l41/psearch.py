"""Parametric candidate search on Mesen (2 cores): candidates = full stage-row lists sharing the prefix to a start frame.
Library: run(cands, start_frame, prefix_rows, end_frame, metric) -> list of (metric value, cand index).
Each candidate is a list of rows for frames start+1..end (legality checked against history + prefix)."""
import sys, time, threading
sys.path.insert(0, 'work/l41')
from lib import *
import fcka
from pathlib import Path as _P
F.LUA = _P('work/l31t/fastcore_gc.lua').resolve()

_cores = None


def cores(prefix, nw=2):
    global _cores
    if _cores is None:
        _cores = []
        for _ in range(nw):
            c = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
            c.put('s', open(MST, 'rb').read()); c.load('s')
            _cores.append(c)
    for c in _cores:
        c.load('s')
        if prefix: c.step(prefix, record='last')
        c.save('p'); c._ka_slot = 'p'
    return _cores


def legal(prefix, tail):
    return L.check(list(prefix) + list(tail), hist_ctl())['pass']


def run(cands, prefix, metric, chunk=24, nw=2):
    """metric(states list (record all), cand) -> value (lower better) or None. Returns [(value, i)] sorted."""
    cs = cores(prefix, nw)
    f0 = F0 + len(prefix)
    res = []; lock = threading.Lock(); idx = list(range(len(cands)))
    parts = [idx[w::len(cs)] for w in range(len(cs))]

    def work(w):
        c = cs[w]
        for q in range(0, len(parts[w]), chunk):
            ii = parts[w][q:q + chunk]
            rr = c.run_batch('p', [cands[i] for i in ii], record='all', stops=[(0x6D, 'changed', 0)])
            for i, r in zip(ii, rr):
                for j, s in enumerate(r.states): s['frame'] = f0 + j + 1
                v = metric(r.states, i)
                with lock: res.append((v, i))
    th = [threading.Thread(target=work, args=(w,)) for w in range(len(cs))]
    for t in th: t.start()
    for t in th: t.join()
    res.sort(key=lambda t: (t[0] is None, t[0] if t[0] is not None else 0))
    return res


def close():
    global _cores
    for c in _cores or []:
        try: c.close()
        except Exception: pass
    _cores = None

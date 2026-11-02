"""r15 (room 15 of 4-1) experiment helpers on Mesen. Stage rows: row i -> frame F0 + i (F0 = 14,848, q4).
prefix = stage rows up to frame S (len S - F0); candidates = rows for frames S+1.."""
import sys, time, threading
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l41')
from lib import *
import fcka
from pathlib import Path as _P
F.LUA = _P('work/l31t/fastcore_gc.lua').resolve()
FL = dict(FLD)
for j in range(8):
    FL[f't{j}'] = 0x400 + j; FL[f'x{j}'] = 0x460 + j; FL[f'y{j}'] = 0x480 + j
FL['eact'] = 0x73; FL['face'] = 0x84
_cores = []

def mk(n=1, mst=MST):
    global _cores
    while len(_cores) < n:
        c = F.FastCore(boot_rows=None, ticks=True, fields=FL)
        c.put('s', open(mst, 'rb').read()); c.load('s'); c.save('s'); c._ka_slot = 's'
        _cores.append(c)
    return _cores[:n]

def at(prefix, n=2, slot='p'):
    cs = mk(n)
    for c in cs:
        c.load('s')
        if prefix: c.step(list(prefix), record='last')
        c.save(slot); c._ka_slot = slot
    return cs

def run(cands, prefix, chunk=24, n=2, stops=((0x6D, 'changed', 0),), slot='p', setup=True):
    """returns list of state lists (record all), each state has 'frame', 'X'."""
    cs = at(prefix, n, slot) if setup else mk(n)
    f0 = F0 + len(prefix)
    res = [None] * len(cands); idx = list(range(len(cands)))
    parts = [idx[w::len(cs)] for w in range(len(cs))]
    def work(w):
        c = cs[w]
        for q in range(0, len(parts[w]), chunk):
            ii = parts[w][q:q + chunk]
            rr = c.run_batch(slot, [cands[i] for i in ii], record='all', stops=list(stops))
            for i, r in zip(ii, rr):
                for j, s in enumerate(r.states):
                    s['frame'] = f0 + j + 1; s['X'] = C.abs_x(s)
                res[i] = r.states
    th = [threading.Thread(target=work, args=(w,)) for w in range(len(cs))]
    for t in th: t.start()
    for t in th: t.join()
    return res

def bird(s):
    sc = s['scroll_scr'] * 256 + s['scroll']
    out = []
    for j in range(8):
        if s['eact'] >> j & 1: out.append((j, s[f't{j}'], sc + s[f'x{j}'], s[f'y{j}']))
    return out

def fmt(s, r=None):
    en = ' '.join(f"{j}:t{t}@{x},{y}" for j, t, x, y in bird(s))
    return (f"{s['frame']} {'+'.join(r) if r else '-':14s} X {s['X']} y {s['y']} vy {s['vy']} an {s['anim']} hp {s['hp']} "
            f"np {s['ninpo']} inv {s['inv']} rm {s['room']} {en}")

def legal(prefix, tail):
    return L.check(list(prefix) + list(tail), hist_ctl())['pass']

def close():
    global _cores
    for c in _cores:
        fcka.forget(c)
        try: c.close()
        except Exception: pass
    _cores = []

def R(s):
    return () if s in ('-', '') else tuple(sorted(s.split('+')))

def seq(spec):
    """'Right*3,A+Left*2,-' -> rows"""
    out = []
    for part in spec.split(','):
        part = part.strip()
        if not part: continue
        if '*' in part:
            b, n = part.rsplit('*', 1); out += [R(b)] * int(n)
        else: out.append(R(part))
    return out

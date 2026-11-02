"""roof-agent helpers (Mesen). Spec: tokens 'RA:3' (Right+A x3), '-:4' (nothing x4), 'R:20'."""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
MAP = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}
INTRO = C.rows_of('logs/a12_intro.inputs.txt')
BASE = C.rows_of('logs/tk_1-1_s11.inputs.txt')


def spec_rows(spec):
    out = []
    for tok in spec.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        row = tuple(sorted(MAP[c] for c in k if c != '-'))
        out += [row] * int(n)
    return out


def enforce(hist, wanted):
    en = L.Enforcer(list(hist)[-1900:])
    return [en.emit(w) for w in wanted]


def fmt(s):
    return f"{C.abs_x(s)},{s['y']}"


def run_all(P, cands, slot='s', **kw):
    """run_chunked with a chunk size that keeps each worker's reply under ~64 KB (bigger replies kill Mesen's socket)."""
    from ng.solve import fast as FS
    L0 = max(len(c) for c in cands)
    ch = max(2, 2 * (600 // max(1, L0)))
    return FS.run_chunked(P, slot, cands, chunk=ch, log=lambda s: None, **kw)

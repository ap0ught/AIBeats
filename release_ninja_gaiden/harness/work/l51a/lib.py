"""5-1 agent l51a helpers. Chain = logs/l44p_r1920_c2_poweron.inputs.txt (22,628 rows); 5-1 control row 22,629 (blank).
Our frame = TAS frame + LAG (504) at equal pace. Base Mesen state states/mesen/lock_51_pre.mst (after row 22,628).
Stage rows files: row 1 = the control row 22,629."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l51p')
import fcka
from ng import fastcore as F
from ng.solve import common as C
import a56_common as A
import a34_core as K
from lib0 import TM, XY, TF0, NF
CHAIN = 'logs/l44p_r1920_c2_poweron.inputs.txt'
CTL = 22629; LAG = CTL - 22125
BASE = 'states/mesen/lock_51_pre.mst'
TR0 = A.tas_rows()
def T(f): return tuple(sorted(TR0[f - 1]))
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
FLD['rf84'] = 0x84; FLD['hp65'] = 0x65; FLD['np64'] = 0x64; FLD['item'] = 0xC9; FLD['room6e'] = 0x6E; FLD['st6d'] = 0x6D
FLD['x86'] = 0x86; FLD['y8a'] = 0x8A; FLD['e5c'] = 0x5C; FLD['inv95'] = 0x95; FLD['t62'] = 0x62; FLD['t63'] = 0x63
for _j in range(8):
    FLD[f't{_j}'] = 0x400 + _j; FLD[f'ex{_j}'] = 0x460 + _j; FLD[f'ey{_j}'] = 0x480 + _j
def core(mst=BASE):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
    fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc
def RXY(r):
    hi = r['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    return hi*256 + r['scr_lo'] + r['x86'], r['y8a']
def hist():
    return [tuple(sorted(r)) for r in C.rows_of(CHAIN)]
def rows_file(p): return [tuple(sorted(r)) for r in C.rows_of(p)]
def P(r): return '+'.join(sorted(r)) if r else '-'
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def legal_ok(rows, h=None):
    h = hist() if h is None else h
    L = K.Legal(list(h)[-1900:])
    for i, r in enumerate(rows):
        w = L.why(tuple(r))
        if w: return f'{i}:{w}'
        L.push(tuple(r))
    return ''
def wr(path, rows, hdr):
    with open(path, 'w') as fo:
        fo.write('# ' + hdr + '\n')
        for r_ in rows: fo.write(P(r_) .replace('-', '') + '\n')
BASEN = 'states/mesen/l51a_p23100N.mst'   # NesHawk-RAM-equal Mesen state after the p23100 rows (frame 23,100)
_P0 = None
def start_core(rows):
    """(fc, k): a Mesen core positioned after rows[:k]; uses the NesHawk-equal 23,100 state when rows start with p23100."""
    global _P0
    if _P0 is None: _P0 = [tuple(sorted(r)) for r in C.rows_of('work/l51a/p23100.txt')]
    if len(rows) >= len(_P0) and [tuple(sorted(r)) for r in rows[:len(_P0)]] == _P0:
        return core(BASEN), len(_P0)
    return core(), 0
def trace(rows, mst=BASE):
    """Mesen per-frame (frame, X, y, hp, np, item, bf, room, st) of stage rows from the base."""
    if mst == BASE:
        fc, k = start_core(rows)
    else:
        fc, k = core(mst), 0
    _, recs, _ = fc.step(rows[k:], record='all'); fc.close()
    out = []
    for i, s in enumerate(recs):
        X, y = RXY(s); out.append((CTL + k + i, X, y, s['hp65'], s['np64'], s['item'], s['bf'], s['room6e'], s['st6d'], s['e5c']))
    return out

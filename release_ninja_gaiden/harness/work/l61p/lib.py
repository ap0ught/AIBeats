"""6-1/6-2 prep helpers (agent l61p). Frame = power-on row number (NesHawk frame k after row k).
TAS: 5-4 kill 29,314, Start 29,909, 6-1 load 29,911, 6-1 control row 30,063 (Left), room 36 = 6-2 load 31,487, 6-2 control 31,638.
Mesen TAS states: states/mesen/l61p_tas<f>.mst = after row f (mkst.py, from l53p_tas29099.mst, checked vs tas61_ram.bin)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l61p')
import fcka
from ng import fastcore as F
from ng.solve import common as C
import a56_common as A
import a34_core as K
from lib0 import *
TR0 = A.tas_rows()
def T(f): return tuple(sorted(TR0[f - 1]))
TPAD = {f: TM(f)[0x2A] for f in range(TF0 + 1, TF0 + 1 + NF)}
def pad(f): return TM(f)[0x2A]
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
FLD['rf84'] = 0x84; FLD['hp65'] = 0x65; FLD['np64'] = 0x64; FLD['item'] = 0xC9; FLD['room6e'] = 0x6E; FLD['st6d'] = 0x6D
FLD['x86'] = 0x86; FLD['y8a'] = 0x8A; FLD['e5c'] = 0x5C; FLD['inv95'] = 0x95; FLD['t62'] = 0x62; FLD['t63'] = 0x63
for _j in range(8):
    FLD[f't{_j}'] = 0x400 + _j; FLD[f'ex{_j}'] = 0x460 + _j; FLD[f'ey{_j}'] = 0x480 + _j

def core(mst=None):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
    if mst:
        fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc

def tas_mst(f): return f'states/mesen/l61p_tas{f}.mst'

def RXY(r):
    hi = r['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    return hi*256 + r['scr_lo'] + r['x86'], r['y8a']

def tas_xy(f): return XY(TM(f))

def legal_ok(rows, hist=()):
    L = K.Legal(list(hist)[-1900:])
    for i, r in enumerate(rows):
        w = L.why(tuple(r))
        if w: return f'{i}:{w}'
        L.push(tuple(r))
    return ''

def legalize_tas(f1, f2, hist=()):
    """TAS rows f1..f2 legalized: L+R -> Right, U+D -> drop both, 1-frame A/B extended (Enforcer)."""
    want = []
    for f in range(f1, f2 + 1):
        w = set(T(f))
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        want.append(tuple(sorted(w)))
    en = A.Enforcer(list(hist)[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def P(r): return '+'.join(sorted(r)) if r else '-'
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

import os, glob
def core_at(f):
    """Mesen core at TAS frame f (nearest saved l61p state <= f + NesHawk pad bytes)."""
    if os.path.exists(tas_mst(f)): return core(tas_mst(f))
    have = sorted(int(p.split('tas')[-1].split('.')[0]) for p in glob.glob('states/mesen/l61p_tas*.mst'))
    g = max(h for h in have if h <= f)
    fc = core(tas_mst(g))
    fc.step([TM(k)[0x2A] for k in range(g + 1, f + 1)], record='last'); fc.save('s'); fc._ka_slot = 's'
    return fc

"""4-3 prep helpers (agent l43p). Frame = power-on row number (NesHawk frame k after row k).
TAS: Mesen states states/mesen/l43p_tas<f>.mst = after row f (= NesHawk ref4751/10_4-3_control path, 0 RAM diffs).
Chain: states/mesen/l43p_k932a19298.mst = after row 19,298 of logs/l42_w_k932a_poweron.inputs.txt (4-3 control row 19,299).
Lag: chain row = TAS row + 340 on the candidate k932a."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
import a56_common as A
import a34_core as K
TR0 = A.tas_rows()
def T(f): return tuple(sorted(TR0[f - 1]))          # TAS row f
D43 = open('work/l43p/tas43_ram.bin', 'rb').read()
TF0 = int.from_bytes(D43[:4], 'little'); D43 = D43[4:]
def TM(f):                                            # TAS RAM after row f (18,961..21,420)
    i = f - TF0 - 1; return D43[i*2048:(i+1)*2048]
TPAD = {f: D43[(f - TF0 - 1)*2048 + 0x2A] for f in range(TF0 + 1, TF0 + 1 + len(D43)//2048)}
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
FLD['rf84'] = 0x84; FLD['hp65'] = 0x65; FLD['np64'] = 0x64; FLD['item'] = 0xC9; FLD['room6e'] = 0x6E; FLD['st6d'] = 0x6D
FLD['x86'] = 0x86; FLD['y8a'] = 0x8A; FLD['e5c'] = 0x5C
for _j in range(8): FLD[f't{_j}'] = 0x400 + _j
CHAIN_POW = 'logs/l42_w_k932a_poweron.inputs.txt'
CHAIN_MST = 'states/mesen/l43p_k932a19298.mst'
LAG = 340

def core(mst=None):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
    if mst:
        fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc

def tas_mst(f): return f'states/mesen/l43p_tas{f}.mst'

def XY(r):
    """world X, y from a Row (fastcore) or RAM bytes."""
    if isinstance(r, (bytes, bytearray)):
        hi, lo, x, y = r[0x52], r[0x51], r[0x86], r[0x8A]
    else:
        hi, lo, x, y = r['scr_hi'], r['scr_lo'], r['x86'], r['y8a']
    hi = hi - 256 if hi >= 128 else hi
    return hi*256 + lo + x, y

def tas_xy(f): return XY(TM(f))

def legal_ok(rows, hist=()):
    """check_inputs semantics: '' if legal else first reason (rows judged after hist)."""
    L = K.Legal(hist[-1900:])
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

def P(r):
    s = '+'.join(x[0] for x in sorted(r)) if r else '-'
    return s

def hist_chain(n=19298):
    return C.rows_of(CHAIN_POW)[:n]

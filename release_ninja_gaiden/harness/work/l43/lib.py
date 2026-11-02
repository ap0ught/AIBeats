"""4-3 solver helpers (agent l43). Frame = power-on row number (Mesen/NesHawk frame k after row k).
Chain (LOCKED 4-2 = k932b): rows 1-19,296 (history), 4-3 stage rows start at the control row 19,297 (Left).
Base state: states/mesen/l43_k932b19296.mst (after row 19,296). Env L43_CHAIN/L43_CTL/L43_BASE override. TAS lag 338 (our f = TAS f + 338 at equal pace)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C, hitbox as H
import a56_common as A
import a34_core as K

CHAIN_POW = os.environ.get('L43_CHAIN', 'logs/l42_w_k932b_poweron.inputs.txt')
CTL = int(os.environ.get('L43_CTL', '19297'))           # 4-3 control row (first stage row)
BASE_MST = os.environ.get('L43_BASE', 'states/mesen/l43_k932b19296.mst')
LAG = CTL - 18959                                      # TAS control 18,959

FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
FLD['rf84'] = 0x84; FLD['e5c'] = 0x5C; FLD['wpn'] = 0x85
for _j in range(8):
    FLD[f't{_j}'] = 0x400 + _j; FLD[f'ex{_j}'] = 0x460 + _j; FLD[f'ey{_j}'] = 0x480 + _j; FLD[f'eh{_j}'] = 0x490 + _j
for _j in range(4):
    FLD[f'ls{_j}'] = 0x4D1 + _j

_D = open('work/l43p/tas43_ram.bin', 'rb').read()
TF0 = int.from_bytes(_D[:4], 'little'); _D = _D[4:]
NT = len(_D) // 2048
def TM(f):
    i = f - TF0 - 1
    return _D[i*2048:(i+1)*2048] if 0 <= i < NT else None
def XYr(r):
    s = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]
    return s*256 + r[0x51] + r[0x86], r[0x8A]
TX = {}; TY = {}; TRM = {}
for _i in range(NT):
    _r = _D[_i*2048:(_i+1)*2048]; _f = TF0 + 1 + _i
    TX[_f], TY[_f] = XYr(_r); TRM[_f] = _r[0x6E]

def X(s):
    if isinstance(s, (bytes, bytearray)): return XYr(s)[0]
    return C.abs_x(s)

def hist_chain():
    return [tuple(sorted(r)) for r in C.rows_of(CHAIN_POW)[:CTL - 1]]

def rows_file(p):
    return [tuple(sorted(r)) for r in C.rows_of(p)]

def core(mst=BASE_MST):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
    fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def P(r): return '+'.join(sorted(r)) if r else '-'

def legal_ok(rows, hist=()):
    L = K.Legal(list(hist)[-1900:])
    for i, r in enumerate(rows):
        w = L.why(tuple(r))
        if w: return f'{i}:{w}'
        L.push(tuple(r))
    return ''

def enforcer(prefix_rows):
    return A.Enforcer((hist_chain() + list(prefix_rows))[-1900:])

def enemies_s(s):
    """enemies from a fastcore Row (slot, type, world X, y)."""
    sc = C.abs_x(s) - s['x']; out = []
    for j in range(8):
        if (s['eact'] >> j) & 1: out.append((j, s[f't{j}'], sc + s[f'ex{j}'], s[f'ey{j}']))
    return out

def write_rows(p, rows, note=''):
    C.write_inputs(p, [tuple(sorted(r)) for r in rows], note)

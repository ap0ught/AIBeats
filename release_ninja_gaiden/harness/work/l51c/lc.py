"""l51c (third: bird phase) helpers. Our axis = c1 power-on rows; TAS-eq = our - 504 - lag."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
C1 = 'logs/l51_a_c1_poweron.inputs.txt'
def c1rows():
    return [tuple(sorted(r)) for r in C.rows_of(C1)]
def slots(s, scr=None):
    out = []
    X, y = RXY(s)
    hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi; scr = hi*256 + s['scr_lo']
    for j in range(8):
        if s['eact'] >> j & 1:
            out.append(f"s{j} t{s[f't{j}']} ({scr + s[f'ex{j}']},{s[f'ey{j}']})")
    return out
def line(f, s):
    X, y = RXY(s)
    return f"{f} X {X} y {y} hp {s['hp65']} np {s['np64']} BF {s['bf']} | " + '; '.join(slots(s))

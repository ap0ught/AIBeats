"""5-1 second agent (l51b) helpers. Our axis: 5-1 control row CTL = 22,629 (= TAS 22,125 + 504).
Real Mesen state states/mesen/l51b_real22628.mst = after row 22,628 of logs/l44p_r1920_c2_poweron.inputs.txt."""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
OFF = 504; CTL = 22629
REAL0 = 'states/mesen/l51b_real22628.mst'
POW = 'logs/l44p_r1920_c2_poweron.inputs.txt'
def powhist(n=1900):
    return [tuple(sorted(r)) for r in C.rows_of(POW)][-n:]
def tasleg(t1, t2, mods=None):
    """wanted rows for TAS frames t1..t2 with L+R -> Right, U+D dropped; mods {t: set}"""
    out = []
    for t in range(t1, t2 + 1):
        w = set(T(t))
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if mods and t in mods: w = set(mods[t])
        out.append(w)
    return out
def enforce(want, hist):
    en = A.Enforcer(list(hist)[-1900:]); return [tuple(sorted(en.emit(w))) for w in want]
def trackhits(recs, f0, hp=None):
    hits = []
    for i, r in enumerate(recs):
        if hp is None: hp = r['hp65']
        if r['hp65'] != hp:
            X, y = RXY(r); hits.append(f'{f0 + i}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
    return hits

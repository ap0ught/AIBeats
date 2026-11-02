"""l65 (6-5 Demon) helpers. Frame axis = TAS power-on rows; TAS 6-5 control row 38,933 (state 38,932 = before the control row).
bf = $BF at the checkpoint before the control row (TAS 243). Rows files: row 1 = the control row."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
L61.FLD.update({f'eh{j}': 0x490 + j for j in range(8)})
FLD.update({f'eh{j}': 0x490 + j for j in range(8)})
FLD['boss'] = 0x66; FLD['e3e'] = 0x3E; FLD['bf'] = 0xBF
F0 = 38932
def rows_of(path):
    return [row(l.strip()) for l in open(path).read().splitlines() if not l.startswith('#')]
def core65(bf=None, pre=()):
    fc = core_at(F0)
    for a, v in pre: fc.poke(a, v)
    if bf is not None: fc.poke(0xBF, bf)
    fc.save('c0'); fc._ka_slot = 'c0'
    return fc
def slots(s, js=range(4, 8)):
    return [(j, s[f't{j}'], s[f'ex{j}'], s[f'ey{j}'], s[f'eh{j}']) for j in js if s[f't{j}']]

STOPS = [(0x66, '==', 0), (0x65, '==', 0)]
def outcome(r):
    """run_batch Result -> (kill offset k (row number of the kill row, control row = 1) or None, hp, T at the kill)"""
    s = r.states[-1] if r.states else {}
    if r.status == 1 and s.get('boss') == 0 and s.get('hp65', 0) > 0 and s.get('st6d') == 21:
        return (r.rows_played, s['hp65'], s['t63'])
    return (None, s.get('hp65'), s.get('t63'))
def test_bfs(fc, rows, bfs, pre=()):
    """fc at the control-1 state in slot 'c0'; returns {bf: outcome}"""
    out = {}
    for v in bfs:
        fc.load('c0')
        for a, x in pre: fc.poke(a, x)
        fc.poke(0xBF, v); fc.save('cb')
        out[v] = outcome(fc.run_batch('cb', [rows], record='last', stops=STOPS)[0])
    return out

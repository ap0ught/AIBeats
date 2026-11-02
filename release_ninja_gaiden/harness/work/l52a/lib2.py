"""5-2 room-23 agent l52a helpers. Our chain = logs/l51_c3d_poweron.inputs.txt (locked rows 1-24,997).
Our frame = TAS frame + 571 at the control (5-2 control row 24,998 = TAS 24,427). Base Mesen state after row 24,997."""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
CHAIN = 'logs/l51_c3d_poweron.inputs.txt'
OFF = 571; CTL52 = 24998
BASE52 = 'states/mesen/l52a_c3d_24997.mst'
def chain_hist():
    return [tuple(sorted(r)) for r in C.rows_of(CHAIN)][:CTL52 - 1]
def rows_file(p):
    out = []
    for l in open(p):
        l = l.strip()
        if l.startswith('#'): continue
        out.append(() if l in ('', '-') else tuple(sorted(x for x in l.replace('|', '+').split('+') if x)))
    return out
def wr(path, rows, hdr):
    with open(path, 'w') as fo:
        fo.write('# ' + hdr + '\n')
        for r_ in rows: fo.write(('+'.join(sorted(r_)) or '') + '\n')

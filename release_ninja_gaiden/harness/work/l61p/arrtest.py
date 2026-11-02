"""Mesen: TAS state 30062 + enemy-slot bytes ($400-$4FF) copied from a real NesHawk arrival (arr_d<d>.bin, RAM on the row before
the 6-1 control), c kept at 84; run pre61_32595 rows; which bytes break the TAS-equivalence? (all, each single byte)."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
d = sys.argv[1]
arr = open(f'work/l61p/arr_d{d}.bin', 'rb').read(); t = TM(30062)
diff = [a for a in range(0x800) if arr[a] != t[a] and not 0x100 <= a < 0x300 and not 0x400 <= a < 0x500 and a != 0xBF]
rows = [row(l.strip()) for l in open('work/l61p/pre61_32595.txt') if l.strip() and not l.startswith('#')]
fc = core(tas_mst(30062)); fc.save('b'); fc._ka_slot = 'b'
def run(addrs):
    fc.load('b')
    for a in addrs: fc.poke(a, arr[a])
    fc.save('t')
    st = fc.run_batch('t', [rows], record='all')[0].states
    hits = [30063 + i for i in range(1, len(st)) if st[i]['hp65'] < st[i-1]['hp65']]
    rooms = [30063 + i for i in range(1, len(st)) if st[i]['room6e'] != st[i-1]['room6e']]
    return hits[:3], rooms
print('d', d, 'diff bytes', [hex(a) for a in diff], flush=True)
print('all', run(diff), flush=True)
for a in diff: print(hex(a), t[a], '->', arr[a], run([a]), flush=True)
fc.close()

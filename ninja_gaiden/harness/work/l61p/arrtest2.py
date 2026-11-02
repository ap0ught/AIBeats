"""Mesen: TAS state 30062 with ALL 2 KB of RAM copied from a NesHawk arrival file (arr_d<d>.bin), $BF set to 83 (c 84) or kept."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
d = sys.argv[1]; keepbf = '--own' in sys.argv
arr = open(f'work/l61p/arr_d{d}.bin', 'rb').read()
rows = [row(l.strip()) for l in open('work/l61p/pre61_32595.txt') if l.strip() and not l.startswith('#')]
fc = core(tas_mst(30062))
for a in range(0x800):
    if 0x100 <= a < 0x200: continue
    fc.poke(a, arr[a])
if not keepbf: fc.poke(0xBF, 83)
fc.save('t'); fc._ka_slot = 't'
st = fc.run_batch('t', [rows], record='all')[0].states
hits = [i + 1 for i in range(1, len(st)) if st[i]['hp65'] < st[i-1]['hp65']]
rooms = [i + 1 for i in range(1, len(st)) if st[i]['room6e'] != st[i-1]['room6e']]
print('d', d, 'own BF' if keepbf else 'c84', 'hits(rel)', hits[:4], 'rooms(rel)', rooms, 'end', RXY(st[-1]), st[-1]['hp65'], st[-1]['np64'])
fc.close()

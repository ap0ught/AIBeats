import sys
sys.path.insert(0, 'work/l53p')
from lib import *
F0 = int(sys.argv[1]); spec = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
rows = []
for part in spec.split(','):
    r, k = part.split('*') if '*' in part else (part, '1')
    rows += [row(r)] * int(k)
rows = (rows + [rows[-1]] * n)[:n]
st = fc.run_batch('b', [rows], record='all')[0].states
for j, s in enumerate(st):
    print(F0 + 1 + j, P(rows[j]), RXY(s), 'touch %02x' % s['coll'] if 'coll' in s else '', 'hp', s['hp65'], 'rm', s['room6e'], 'np', s['np64'])
fc.close()

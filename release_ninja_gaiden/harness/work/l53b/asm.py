"""l53b: assemble 5-3 stage rows: segments (rows file, first frame); gaps filled with blanks. Writes stage rows (row 1 = 27,360)
and a power-on file (e4 rows 1..27,359 + stage rows). python work/l53b/asm.py out_tag END seg1.txt:F1 seg2.txt:F2 ..."""
import sys
tag, END = sys.argv[1], int(sys.argv[2])
F = 27360
L = open('logs/l52b_e4_poweron.inputs.txt').read().split('\n')[1:27360]
rows = {}
for s in sys.argv[3:]:
    p, f = s.rsplit(':', 1); f = int(f)
    rr = [l.strip() for l in open(p) if l.strip() and not l.startswith('#')]
    for i, r in enumerate(rr): rows[f + i] = r
st = [rows.get(f, '-') for f in range(F, END + 1)]
open(f'work/l53b/{tag}_stage.txt', 'w').write(f'# l53b {tag}: 5-3 stage rows from the control row 27,360 to {END}; segs {sys.argv[3:]}\n' + '\n'.join(st) + '\n')
allr = L + st
with open(f'work/l53b/{tag}_poweron.inputs.txt', 'w') as fo:
    fo.write(f'# frames={len(allr)} power-on: l52b e4 rows 1-27,359 + l53b {tag} 5-3 rows\n')
    for r in allr: fo.write(('' if r == '-' else r) + '\n')
print('rows', len(allr))

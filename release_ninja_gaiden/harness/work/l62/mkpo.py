"""l62: power-on file = base rows 1..KEEP, blanks, Start on S and S+1, blanks to F-1, then stage rows (files, concatenated) from F.
python work/l62/mkpo.py out base KEEP S F stagefile [stagefile ...]"""
import sys, os
sys.path.insert(0, '.')
from ng.inputs import read_inputs
out, basef, KEEP, S, F = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
R = [tuple(r) for r in read_inputs(basef)][:KEEP]
R += [()] * (F - 1 - len(R))
R[S - 1] = ('Start',); R[S] = ('Start',)
for p in sys.argv[6:]:
    R += [() if l.strip() == '-' else tuple(l.strip().split('+')) for l in open(p) if l.strip() and not l.startswith('#')]
tmp = out + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fo:
    fo.write(f'# frames={len(R)}\n')
    for r in R: fo.write('+'.join(r) + '\n')
os.replace(tmp, out)
print(out, len(R))

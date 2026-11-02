"""l62: power-on = locked 1..35,798 (logs/l62_LOCKED_v2_to63_poweron.inputs.txt) + stage rows from 35,799 (files concatenated).
python work/l62/po63.py out stagefile [stagefile ...]"""
import sys, os
src = open('logs/l62_LOCKED_v2_to63_poweron.inputs.txt').read().split('\n')[1:35799]
add = []
for p in sys.argv[2:]:
    L = open(p).read().split(chr(10))
    if L and L[-1] == '': L = L[:-1]
    add += [('' if l.strip() == '-' else l.strip()) for l in L if not l.startswith('#')]
R = src + add
tmp = sys.argv[1] + '.tmp'
open(tmp, 'w').write(f'# frames={len(R)}\n' + '\n'.join(R) + '\n'); os.replace(tmp, sys.argv[1])
print(sys.argv[1], len(R))

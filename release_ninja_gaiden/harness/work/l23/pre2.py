"""Mesen: 2-2 rows with Left on the last `npre` rows, then 2-3 rows (file) with `drop` leading rows removed.
python work/l23/pre2.py <2-3 rows from control> <npre> <drop>[,<drop>..]"""
import sys
sys.path.insert(0, 'work/l23')
from lib import *
s = [tuple(r) for r in C.rows_of('logs/l22_art_t12.inputs.txt')]
k23 = [tuple(r) for r in C.rows_of(sys.argv[1])]
npre = int(sys.argv[2])
fc = L22.core(); fc.step(s[:-npre] + [('Left',)] * npre); fc.save('b')
m = fc.ram(); print('control x', m[0x86], 'BF', m[0xBF])
for d in [int(x) for x in sys.argv[3].split(',')]:
    fc.load('b')
    kill = None
    for i, r in enumerate(k23[d:]):
        fc.step([r]); m = fc.ram()
        if m[0x66] == 0 and m[0x6D] == 4: kill = i + 1; break
    print('npre', npre, 'drop', d, 'kill row from control', kill, 'np', m[0x64], 'hp', m[0x65])
fc.close()

"""Handover: Mesen states states/mesen/l51a_<tag>_<f>.mst + power-on histories work/l51a/h_<tag>_<f>.inputs.txt (rows 1..f).
python work/l51a/mkho.py <stage rows> <tag> f1,f2,..."""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
rows = rows_file(sys.argv[1]); tag = sys.argv[2]; fs = sorted(int(x) for x in sys.argv[3].split(','))
H = hist(); fc, _k = start_core(rows); f = CTL - 1 + _k
for k in fs:
    fc.step(rows[f - CTL + 1:k - CTL + 1], record='last'); f = k
    fc.save('h'); fc.save_file('h', F.STATES / f'l51a_{tag}_{k}.mst', k)
    r = fc.ram(); X, y = RXY({'scr_hi': r[0x52], 'scr_lo': r[0x51], 'x86': r[0x86], 'y8a': r[0x8A]})
    C.write_inputs(f'work/l51a/h_{tag}_{k}.inputs.txt', H + rows[:k - CTL + 1], f'l51a {tag}: power-on rows 1..{k} (chain + 5-1 stage rows {sys.argv[1]})')
    print(k, 'X', X, 'y', y, 'hp', r[0x65], 'np', r[0x64], 'it', r[0xC9], 'BF', r[0xBF], flush=True)
fc.close()

"""Mesen vs NesHawk from l41q_r15 (16,400): python work/r15/nhcmp.py <stage rows> <to>  -> first divergence + eaten edges"""
import sys, subprocess; sys.path.insert(0, 'work/r15')
from rlib import *
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
rows = C.rows_of(sys.argv[1]); to = int(sys.argv[2])
c = F.FastCore(boot_rows=None, ticks=True, fields=FL); c.put('s', open('states/mesen/l41_q16400.mst', 'rb').read()); c.load('s')
_, recs, _ = c.step(list(rows[16400 - F0:to - F0]), record='all'); c.close()
nh = subprocess.run([sys.executable, '-u', 'work/r15/nhtrace.py', sys.argv[1], 'l41q_r15', str(to)], capture_output=True, text=True).stdout.split('\n')
eaten = []; div = None
for l in nh:
    p = l.split()
    if not p or not p[0].isdigit(): continue
    f = int(p[0]); s = recs[f - 16401]; r = rows[f - F0 - 1]
    mask = sum(BITS[b] for b in r); pad = int(p[p.index('pad') + 1])
    if pad != mask and r != rows[f - F0 - 2]: eaten.append(f)
    nv = (int(p[p.index('X') + 1]), int(p[p.index('y') + 1]), int(p[p.index('hp') + 1]))
    mv = (C.abs_x(s), s['y'], s['hp'])
    if div is None and nv != mv: div = (f, 'NH', nv, 'M', mv)
print('eaten', eaten[:15], 'first div', div)

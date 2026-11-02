"""Compose (no emulator): prefix rows[:N] + legal TAS rows at --lags to n rows; write --out.
python work/l32a/comp.py <prefix> N n --lags row:lag,.. --out f [--slash ..] [--set ..] [--keep ..]"""
import sys
sys.path.insert(0, 'work/l32a')
import tmod as T
from lib import *
want = T.compose(T.sl, T.sets)
lg = legal_after([], want)
C.write_inputs(T.out, lg, 'comp ' + ' '.join(sys.argv[1:]))
print('wrote', T.out, len(lg), 'changed by legalization', sum(1 for p, q in zip(lg, want) if p != q))

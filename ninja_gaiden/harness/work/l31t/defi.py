"""X deficit vs the TAS (lag 165) along stage rows: python work/l31t/defi.py <stage rows> [every]"""
import sys
sys.path.insert(0, 'work/l31t'); sys.path.insert(0, '.')
from lib import *
rows = C.rows_of(sys.argv[1]); ev = int(sys.argv[2]) if len(sys.argv) > 2 else 10
r = play(rows)
prev = None
for i, s in enumerate(r.states):
    t = T[9828 + i + 1]
    d = round((ax(t) + t['xsub'] / 256 - ax(s) - s['xsub'] / 256) / 1.5, 1)
    if i % ev == 0 or (prev is not None and abs(d - prev) >= 0.5) or i == len(r.states) - 1:
        print(f"{i} f{F0+i+1} X {ax(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} it {s['item']} | TAS X {ax(t)} y {t['y']} | behind {d} f")
        prev = d

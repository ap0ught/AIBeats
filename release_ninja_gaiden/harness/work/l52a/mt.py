"""Mesen trace: python work/l52a/mt.py <mst|tas:F> "rows spec" [n]   spec: 'Left*3,A+Right*2,Left*40'"""
import sys; sys.path.insert(0, 'work/l52a')
from lib2 import *
FLD.update(dict(act=0x80, tch=0x8C, fl=0x84, vy=0x89, pad=0x28, edge=0x29, spx=0xAD, spxf=0xAC, kb=0x93, a3=0xA3))
def parse(spec):
    out = []
    for part in spec.split(','):
        part = part.strip()
        if not part: continue
        r, _, n = part.partition('*'); out += [row(r)] * (int(n) if n else 1)
    return out
def run(src, rows):
    fc = core_at(int(src[4:])) if src.startswith('tas:') else core(src)
    _, recs, _ = fc.step(rows, record='all'); fc.close(); return recs
if __name__ == '__main__':
    src = sys.argv[1]; rows = parse(sys.argv[2]) if not sys.argv[2].endswith('.txt') else rows_file(sys.argv[2])
    recs = run(src, rows)
    for i, s in enumerate(recs):
        X, y = RXY(s)
        print(i + 1, P(rows[i]), 'X', X, 'xs', s['xsub'], 'y', y, 'act', s['act'], 'tch', hex(s['tch']), 'fl', hex(s['fl']), 'vy', s['vy'],
              'sp', s['spx'], s['spxf'], 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'], 'a3', s['a3'])

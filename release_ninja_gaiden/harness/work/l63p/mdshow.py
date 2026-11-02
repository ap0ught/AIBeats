import sys
sys.path.insert(0, 'work/l63p')
from lib import *
F0 = 37277
spec = sys.argv[1]  # 'a-b=Row;...' overrides, default Right
PK = sys.argv[2] if len(sys.argv) > 2 else '0xC9=133,0x64=5,0xC8=0'
N = int(sys.argv[3]) if len(sys.argv) > 3 else 120
ov = {}
for part in [p for p in spec.split(';') if p]:
    k, v = part.split('=')
    x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
    for f in range(x, y + 1): ov[f] = row(v)
rows = [ov.get(f, ('Right',)) for f in range(F0 + 1, F0 + 1 + N)]
fc = core_at(F0)
for kv in [p for p in PK.split(',') if p]:
    k_, v_ = kv.split('='); fc.poke(int(k_, 0), int(v_, 0))
_, st, _ = fc.step(rows, record='all')
fc.close()
for i, s in enumerate(st):
    f = F0 + 1 + i
    print(f, P(rows[i]), RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'boss', s.get('bosshp'), 'f84', s['rf84'])

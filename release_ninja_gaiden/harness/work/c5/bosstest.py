"""Basaquer idle trajectory from a state with optional DEBUG pokes: compare to the TAS 3-3 control state."""
import sys, json
sys.path.insert(0, '.')
from ng.solve import common as C
N = 300
variants = json.loads(sys.argv[1])   # list of [state, {addr: val}]
e = C.open_emu("c5_bosstest_emu.log")
try:
    trs = []
    for st, pokes in variants:
        e.load(st)
        for a, v in pokes.items():
            e.poke(int(a, 0), v)
        tr = []
        for k in range(N):
            e.run([()])
            r = e.ram_all()
            tr.append(tuple((r[0x400 + i], r[0x460 + i], r[0x480 + i], r[0x490 + i]) for i in range(8)))
        trs.append(tr)
    base = trs[0]
    for (st, pk), tr in zip(variants, trs):
        first = next((k for k in range(N) if [s for s in tr[k] if s[0] == 7 or s[0] == 9] != [s for s in base[k] if s[0] in (7, 9)]), None)
        print(st, pk, "first boss-diff frame", first)
        if first is not None:
            for k in range(max(0, first - 1), min(N, first + 3)):
                print("  ", k, base[k][3:5], tr[k][3:5])
finally:
    e.close()

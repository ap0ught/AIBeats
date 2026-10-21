"""Hop 1 table near the low-ceiling boundary, for every stage-A landing value L0: after the water landing run Left g1, jump Left+A x k,
keep Left until air frame m, then Right to the landing.  Survivors: landing (frame after takeoff, x, $466).  WANT = values from which one
hop under the shaft (k2) ends on 118.   python l9heli_fix_hop1.py [L0 ...]"""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
ins = up14_inputs()
WANT = {87: 1, 159: 2, 205: 3, 60: 4, 180: 5, 59: 6, 219: 7, 152: 8, 118: 0}
allv = json.load(open(LOGS_DIR / "fix" / "heli_stA4.json"))
L0s = [int(v) for v in sys.argv[1:]] or [67]
e = BizHawk(log_name="l9heli_fix_hop1.log", fields=T.FLD)
res = []
for L0 in L0s:
    var = min([o for o in allv if o["land"][4] == L0], key=lambda o: o["land"][0])
    e.load("L9heli_7800")
    for f in range(OFF + 7800, OFF + var["root"]): e.step(bt(ins[f]), 1)
    for b in var["inputs"]: s = e.step(bt(b), 1)
    S0 = e.msave(); idx0 = var["root"] + len(var["inputs"]); shifts = {}
    for g1 in range(12, 19):
        for k in range(1, 13):
            for m in range(3, 11):
                e.mload(S0)
                for i in range(g1): s = e.step(("Left",), 1)
                land = None; bump = None
                for i in range(64):
                    b = ("Left+A" if i < k else "Left") if i < m else ("Right+A" if i < k else "Right")
                    s = e.step(bt(b), 1)
                    if s.hp < 47: break
                    H = (s.h | s.hh << 8) - 6182
                    if bump is None and s.an == 45: bump = (i + 1, H)
                    if i > 2 and s.z == 0: land = (i + 1, s.x | s.xh << 8, s.sub, s.spd, s.sh); break
                if land:
                    shifts.setdefault(((land[4] - L0) % 256, bump), []).append((g1, k, m, land))
                    if land[4] in WANT:
                        print(f"L0 {L0} g1 {g1} k {k} m {m}: bump {bump} land {land} at index {idx0 + g1 + land[0]} <== then one shaft hop k2={WANT[land[4]]}", flush=True)
                        res.append(dict(L0=L0, g1=g1, k=k, m=m, land=land, index=idx0 + g1 + land[0], k2=WANT[land[4]]))
    print("L0", L0, "distinct (shift, bump):", sorted((k, len(v), min(x[3][0] for x in v)) for k, v in shifts.items()), flush=True)
json.dump(res, open(LOGS_DIR / "fix" / ("heli_hop1_" + "_".join(str(v) for v in L0s) + ".json"), "w"))
e.close()

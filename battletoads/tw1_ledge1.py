"""TOWER1 probe 1: is the 67-frame wait at the H-4094 ledge (A12r 5043..5108) needed, and for what?
From bookmark tw1_a_f5000: A12r[5000:5043], then (a) the TAS's own inputs from its frame 4387, (b) wait d + A12r[5109:].
Prints landings / spawns / pole grab for each variant."""
import sys
from tw1_lib import *
A = seg("A12r")
e = BizHawk(log_name="tw1_ledge1.log"); e.load("tw1_a_f5000"); e.step((), 0) if False else None
run(e, A[5000:5043])
root = e.msave()
def track(seq, label, k0=5043, stop=420):
    e.mload(root); prev = rd(e); out = []; k = k0
    for i, b in enumerate(seq[:stop]):
        e.step(bt(b), 1); k += 1; s = rd(e)
        if prev["z"] != 0 and s["z"] == 0: out.append(f"{k}:land({s['x']},{s['H']})t{s['t']}")
        if s["an"] in (94, 95, 96) and prev["an"] not in (94, 95, 96): out.append(f"{k}:POLE({s['x']},{s['H']})")
        if s["faces"] and not prev["faces"]: out.append(f"{k}:FACE cam{s['cam']}")
        n5 = [d for d in s["objs"] if d[0] == 0x5c]; p5 = [d for d in prev["objs"] if d[0] == 0x5c]
        if n5 and not p5: out.append(f"{k}:HORN")
        if n5 and p5 and n5[0][3] < p5[0][3]: out.append(f"{k}:hit{n5[0][3]}")
        if not alive(s): out.append(f"{k}:DEAD hp{s['hp']} lives{s['lives']}"); break
        prev = s
    print(label, " ".join(out), f"| end x={s['x']} H={s['H']} cam={s['cam']}", flush=True)
T = [tasin(r) for r in range(4387, 4387 + 420)]
T = [("Right" if ("Left" in b and "Right" in b and False) else b) for b in T]
Tl = []
for b in T:
    v = set(bt(b))
    if "Left" in v and "Right" in v: v -= {"Left", "Right"}
    Tl.append("+".join(sorted(v, key=ORDER.index)))
track(Tl, "TAS inputs from 4387 (L+R stripped):")
for d in [0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 60, 62, 64, 65, 66, 67, 68, 70]:
    track([""] * d + A[5109:], f"wait {d:3d} + A12r[5109:]:")
e.close()

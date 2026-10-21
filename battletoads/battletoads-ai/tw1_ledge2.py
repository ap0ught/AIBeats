"""TOWER1 probe 2: timelines of the green ledges (0x34 objects) against the frame counter $0B/$0C.
Stand on the H-4094 ledge (A12r 5043) and on the H-4382 ring (A12r 5191) for 560 frames each; log every 0x34's sprite byte ($3D0+q)."""
from tw1_lib import *
A = seg("A12r")
e = BizHawk(log_name="tw1_ledge2.log"); e.load("tw1_a_f5000")
run(e, A[5000:5043])
out = {}
def stand(n, tag):
    for i in range(n):
        e.step((), 1); m = e.ram(0, 0x800)
        for q in range(2, 15):
            if m[0x3C1 + q] == 0x34:
                key = (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8)
                out.setdefault(key, []).append((tag, i, m[0x0B], m[0x0C], m[0x3D0 + q], m[0x4A2 + q], m[0x5A1 + q], m[0x484 + q], m[0x493 + q]))
stand(560, "a")
e.load("tw1_a_f5000"); run(e, A[5000:5191])
s = rd(e); print("at", s["x"], s["H"], s["cam"])
stand(560, "b")
s = rd(e); print("after", s["x"], s["H"], s["cam"], s["hp"])
e.close()
import json
json.dump({f"{k[0]},{k[1]}": v for k, v in out.items()}, open(FIX / "tw1_ledge2.json", "w"))
for k, v in sorted(out.items(), key=lambda kv: kv[0][1]):
    print("LEDGE", k)
    # run-length of sprite byte class: 101 solid-visible, 0 hidden, blink (alternating)
    prev = None; start = None
    def cls(j):
        a = v[j][4]
        nb = [v[x][4] for x in range(max(0, j - 2), min(len(v), j + 3)) if v[x][0] == v[j][0]]
        if len(set(nb)) > 1 and set(nb) <= {0, 101}: return "blink"
        return {101: "shown", 0: "hidden"}.get(a, f"anim{a}")
    for j in range(len(v)):
        c = cls(j)
        if c != prev or v[j][0] != v[j - 1][0]:
            print(f"   {v[j][0]} i={v[j][1]:3d} t={v[j][2]:3d} t2={v[j][3]:3d} -> {c}")
            prev = c

"""TOWER1: the way off wind face 1's pole to the first green ledge (L1 at (304,3968)), old phase (A12r state).
Scan: release frame, then sprint Left round the tower and ONE jump straight onto L1 (jump frame m, A held h, then Left
or nothing to steer).  Prints the earliest L1 landings.   python tw1_exit.py"""
from tw1_lib import *
A = seg("A12r")
e = BizHawk(log_name="tw1_exit.log"); e.load("tw1_a_f4750"); run(e, A[4750:4874])
e.step(bt("Down+Left"), 1)                                   # release input index 4874 (one earlier than A12r's)
k = 4875
while True:
    e.step((), 1); k += 1; s = rd(e)
    if s["z"] == 0 and s["an"] == 1: break
print("free at k", k, fmt(k, "", s)[:100])
root = e.msave(); k0 = k
res = []
for pre in (["Left", "", "Left"], ["Left", "Left", "", "Left"], ["", "Left", "", "Left"]):
    e.mload(root); kk = k0
    for b in pre: e.step(bt(b), 1); kk += 1
    s = rd(e)
    if s["spd"] != 192: print("pre", pre, "no sprint:", s["spd"]); continue
    base = e.msave(); kb = kk
    # run Left until x passes the jump point
    for m in range(30, 62):
        e.mload(base); kk = kb
        for _ in range(m): e.step(bt("Left"), 1); kk += 1
        s = rd(e); xj = s["x"]; jb = e.msave(); kj = kk
        for h in (12, 14, 16, 18, 20, 22, 24):
            for tail in ("Left", "", "Right"):
                e.mload(jb); kk = kj; land = None
                for i in range(40):
                    b = "Left+A" if i < h else tail
                    e.step(bt(b), 1); kk += 1; s = rd(e)
                    if s["z"] == 0:
                        land = (kk, s["x"], s["H"]); break
                    if s["hp"] < 47: break
                if land and land[2] == 3973:
                    res.append((land[0], pre, m, xj, h, tail, land[1]))
        e.mfree(jb)
res.sort(key=lambda r: r[0])
for r in res[:25]: print(f"L1 landed at k={r[0]} x={r[6]} | pre={r[1]} run {r[2]} (jump from x {r[3]}) A held {r[4]} then '{r[5]}'")
print(len(res), "landings on L1; A12r lands on L1 at 5007")
e.close()

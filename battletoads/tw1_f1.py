"""TOWER1 probe: replay the 1-player TAS's own (legal) inputs from one of our states and compare with its RAM rows.
    python tw1_f1.py <our k> <tas r> <n> [verbose]
our k = A12r index whose state stands for TAS row r (state BEFORE our input k == TAS state after its input r);
then our input k+i = TAS input r+1+i."""
import sys
from tw1_lib import *
k0, r0, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); verbose = len(sys.argv) > 4
A = seg("A12r")
e = BizHawk(log_name="tw1_f1.log")
b0 = (k0 // 250) * 250
e.load(f"tw1_a_f{b0}"); run(e, A[b0:k0])
s = rd(e); t = rdm(tasrow(r0))
print("start ours", k0, s["x"], s["H"], s["z"], s["an"], s["spd"], "| tas", r0, t["x"], t["H"], t["z"], t["an"], t["spd"])
lastok = None; bad = 0
for i in range(n):
    r = r0 + 1 + i
    b = tasin(r)
    if banned(b): print("BANNED at tas", r, b); break
    e.step(bt(b), 1); s = rd(e); t = rdm(tasrow(r))
    d = (dx(s["x"], t["x"]), s["H"] - t["H"], s["z"] - t["z"])
    oo = sorted((q[0], q[1], q[2], q[3]) for q in s["objs"] if q[0] in (0x5c, 0x62, 0x36))
    to = sorted((q[0], q[1], q[2], q[3]) for q in t["objs"] if q[0] in (0x5c, 0x62, 0x36))
    same = d == (0, 0, 0) and oo == to
    if verbose or not same:
        print(k0 + i + 1, r, b.ljust(10), f"ours x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} cam={s['cam']} | tas x={t['x']} H={t['H']} z={t['z']} an={t['an']} spd={t['spd']} cam={t['cam']} | d={d}", "" if oo == to else f"OBJ ours {oo} tas {to}")
        bad += not same
    if not alive(s): print("DEAD"); break
    if abs(d[0]) > 40 or abs(d[1]) > 60: print("LOST"); break
    if bad > 60 and not verbose: print("too many diffs"); break
e.close()

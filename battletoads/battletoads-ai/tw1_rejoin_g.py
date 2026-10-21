"""TOWER1: after the patch to the spring behind the cam-4096 Hornhead (piece ends 2 frames after landing on the spring,
= after old input 2720): old inputs to the launch, then air steering (two Right+A blocks) so that the landing on the
(431,2038) ledge and on (454,2078) equal the old run's -> piece standing for old row 2781.
    python tw1_rejoin_g.py <piece> <out>"""
import sys
from tw1_lib import *
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
p = load_piece(sys.argv[1]); out = sys.argv[2]
FIRST = int(sys.argv[3]) if len(sys.argv) > 3 else 2721        # first old input to give (2719 = the piece ends on the landing frame)
e = BizHawk(log_name="tw1_rejoin_g.log"); e.load(p["base"]); run(e, p["inputs"])
def old(r): return rdm(buf[(r + 1) * 2048:(r + 2) * 2048])
for r in range(FIRST, 2741): e.step(bt(A[r]), 1)
launch = e.msave(); oL = old(2772); oM = old(2780); good = []
for n1 in range(0, 10):
    for s2 in range(2746, 2770):
        for n2 in range(0, 24):
            if s2 + n2 > 2770: continue
            seq = ["Right+A" if ((r < 2741 + n1) or (s2 <= r < s2 + n2)) else "A" for r in range(2741, 2770)] + [A[2770], A[2771], A[2772]]
            e.mload(launch)
            for b in seq: e.step(bt(b), 1)
            s = rd(e)
            if (s["H"], s["z"]) == (oL["H"], oL["z"]) and abs(s["x"] - oL["x"]) <= 1:
                for r in range(2773, 2781): e.step(bt(A[r]), 1)
                t = rd(e)
                if (t["x"], t["H"], t["z"], t["spd"], t["cam"]) == (oM["x"], oM["H"], oM["z"], oM["spd"], oM["cam"]):
                    good.append((abs(t["sub"] - oM["sub"]), seq, t["t"] - oM["t"]))
good.sort(key=lambda g: g[0])
print(len(good), "exact rejoins; best sub diff", good[0][0] if good else None, "t diff", good[0][2] if good else None)
if good:
    full = [norm(A[r]) for r in range(FIRST, 2741)] + [norm(b) for b in good[0][1]] + [norm(A[r]) for r in range(2773, 2781)]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + full, rn=2781, parent=sys.argv[1])
    print("saved", out, "k end", p["base_k"] + len(p["inputs"]) + len(full), "G", 2781 - (p["base_k"] + len(p["inputs"]) + len(full)))
e.close()

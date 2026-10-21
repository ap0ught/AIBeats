"""TOWER1 route A: after the cam-4096 Hornhead's kill (piece = ... + old inputs to 2639, landed), stand until the frame
counter is in the OLD run's phase (mod 256) and do the old run's own run-up (walk Left, brake, sprint Right, jump)
so that the jump to the spring starts on the old run's exact frame-counter value, x and speed.
    python tw1_joinA.py <piece standing for old row 2640> <out>
-> piece standing for old row 2680 (one frame into the jump: x 289, H 1827, speed 192)."""
import sys
from tw1_lib import *
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
def oldm(r): return buf[(r + 1) * 2048:(r + 2) * 2048]
p = load_piece(sys.argv[1]); out = sys.argv[2]
e = BizHawk(log_name="tw1_joinA.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
m = e.ram(0, 0x800); s = rdm(m); om = oldm(2639); o = rdm(om)
need = (om[0x0B] - m[0x0B]) % 256                              # ticks we are ahead of the old run
L = 40 + need
print(f"now x={s['x']} t={s['t']}; old row 2640 x={o['x']} t={o['t']}: {need} extra frames to stand -> {L} inputs to the jump frame")
tm = oldm(2679); tgt = rdm(tm)
print("target (old after input 2679):", tgt["x"], tgt["sub"], tgt["H"], tgt["z"], tgt["spd"], tgt["face"], "t", tgt["t"], "Hsub", tm[0x466])
good = []
for b in range(8, 40):
    for gap in (1, 2):
        for c in range(6, 40):
            a = L - (b + 1 + gap + c + 2)
            if a < 4: continue
            seq = [""] * a + ["Left"] * b + ["Right"] + [""] * gap + ["Right"] * c + ["", "Right+A"]
            e.mload(root); run(e, seq); mm = e.ram(0, 0x800); t = rdm(mm)
            if (t["z"], t["H"], t["spd"], t["face"]) == (tgt["z"], tgt["H"], tgt["spd"], tgt["face"]):
                good.append((abs(dx(t["x"], tgt["x"])), abs(t["sub"] - tgt["sub"]), b, gap, c, a, t["x"], t["sub"], mm[0x0B] - tm[0x0B], mm[0x466] - tm[0x466], seq))
good.sort(key=lambda g: g[:2])
for g in good[:8]: print("dx", g[0], "sub diff", g[1], "Left", g[2], "gap", g[3], "Right", g[4], "idle", g[5], "x", g[6], g[7], "t diff", g[8], "Hsub diff", g[9])
if good and good[0][0] == 0:
    seq = good[0][-1]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + [norm(b) for b in seq], rn=2680, parent=sys.argv[1])
    k = p["base_k"] + len(p["inputs"]) + len(seq)
    print("saved", out, "k end", k, "G", 2680 - k)
e.close()

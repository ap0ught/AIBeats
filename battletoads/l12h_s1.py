"""L12h stage 1 probe: after the pre-face-2 boot kill (L12g 5329), follow the TAS's double pump: launch as soon as the boot
recovery ends (face 2 spawns ~28 frames sooner), come down on the spring, pump again, fly Left to the x-480 pole.
Scans the frame of the first A press; prints the trajectory against the TAS's rows."""
import sys
from l12h_lib import *
G = seg("L12g"); T = tas()
e = BizHawk(log_name="fix_l12h_s1.log"); e.load("L12h_g_f5250")
run(e, G[5250:5331]); base = e.msave()
def attempt(a0, verbose=False):
    """idle to frame a0, then the TAS's inputs from f74231 (first A) shifted so that they start at our frame a0."""
    e.mload(base); k = 5331; seq = []
    while k < a0: e.step((), 1); k += 1; seq.append("")
    ev = {}; f = 74231
    while f <= 74376 + 40:
        b = tbtn(f, air="", ground="") if f <= 74376 else "Left+A"
        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e); f += 1
        if verbose and (f % 3 == 0): print(k, "ours", s["x"], s["H"], s["z"], s["an"], "cam", s["cam"], "spring", ob(s, 0x36, 4407, 40), "| TAS", f - 1, T[f - 1]["x"], T[f - 1]["h"] + 4352, T[f - 1]["z"], T[f - 1]["p"], flush=True)
        if not alive(s): ev["dead"] = k; break
        if s["z"] == 8 and "launch" not in ev: ev["launch"] = k
        if s["faces"] and "face" not in ev: ev["face"] = k
        if "launch" in ev and s["z"] == 0 and "land" not in ev: ev["land"] = (k, s["x"], s["H"])
        if "land" in ev and s["z"] == 8 and "launch2" not in ev: ev["launch2"] = k
        if s["an"] in (94, 95, 96): ev["pole"] = (k, s["x"], s["H"]); break
    return ev, seq
for a0 in range(5350, 5372):
    ev, seq = attempt(a0)
    print("A from", a0, ev, flush=True)
if len(sys.argv) > 1:
    attempt(int(sys.argv[1]), True)
e.close()

"""L12h stage 0: shift the toad right in the green column (Right held n frames from frame r0 during a vertical hop) so that the
pre-face-2 fight starts at the TAS's x (350 at the landing 5225 instead of 345). Reports the landing at 5225."""
from l12h_lib import *
G = seg("L12g"); T = tas()
e = BizHawk(log_name="fix_l12h_s0.log"); e.load("L12h_g_f5000")
run(e, G[5000:5140]); base = e.msave()
for r0 in (5150, 5168):
    for n in range(0, 12):
        e.mload(base); seq = list(G[5140:5232])
        for i in range(n):
            j = r0 - 5140 + i
            seq[j] = "Right+A" if seq[j] == "A" else seq[j]
        k = 5140; lands = []; pz = 8; hh = None
        for b in seq:
            e.step(bt(b), 1); k += 1; s = rd(e)
            if pz != 0 and s["z"] == 0: lands.append((k, s["x"], s["H"], s["spd"]))
            pz = s["z"]
            if k == 5225: hh = ob(s, 0x5c)
        print("r0", r0, "n", n, lands, "hornhead@5225", hh, "(TAS 350 / 372)", flush=True)
e.close()

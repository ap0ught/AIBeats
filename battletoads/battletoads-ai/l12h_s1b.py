"""L12h stage 1b probe: what does face 2's wind do to a toad on the floor (H 4382) under the x-480 pole? From the early-launch
variant (A from 5363: face 5425, lands on the floor at 5469, x 470): hold a button for 460 frames, print the track."""
import sys
from l12h_lib import *
G = seg("L12g"); T = tas()
e = BizHawk(log_name="fix_l12h_s1b.log"); e.load("L12h_g_f5250")
run(e, G[5250:5331]); 
k = 5331; seq = []
while k < 5363: e.step((), 1); k += 1; seq.append("")
f = 74231
while True:
    b = tbtn(f, air="", ground=""); e.step(bt(b), 1); k += 1; seq.append(b); f += 1; s = rd(e)
    if s["z"] == 0 and k > 5420: break
print("landed", k, s["x"], s["H"], flush=True); base = e.msave(); k0 = k
for hold in sys.argv[1:]:
    e.mload(base); k = k0; out = []
    for i in range(470):
        b = "" if hold == "idle" else hold
        e.step(bt(b), 1); k += 1; s = rd(e)
        if i % 10 == 0 or not alive(s): out.append(f"{k}:{s['x']},{s['H']},z{s['z']},a{s['an']},w{s['wind']},f{s['faces']}")
        if not alive(s): out.append("DEAD"); break
    print(hold, " ".join(out), flush=True)
e.close()

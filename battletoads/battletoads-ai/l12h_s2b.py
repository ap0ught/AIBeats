"""L12h stage 2 probe: ways off the pole. From L12g's pole at frame D press each candidate for 3 frames then hold `after`; print the track."""
import sys
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_s2b.log"); e.load("L12h_g_f5250")
D = int(sys.argv[1])
run(e, G[5250:5700]); e.step((), D - 5700); base = e.msave()
for cand in sys.argv[2:]:
    first, after = cand.split("/")
    e.mload(base); k = D; out = []
    for i in range(70):
        b = first if i < 3 else after
        e.step(bt(b), 1); k += 1; s = rd(e)
        out.append(f"{k}:{s['x']},{s['H']},a{s['an']},z{s['z']}")
        if not alive(s): out.append("DEAD"); break
    print(cand, " ".join(out[::4]), flush=True)
e.close()

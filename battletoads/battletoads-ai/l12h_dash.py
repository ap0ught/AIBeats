"""L12h probe: can a spring launch come out at sprint speed (192)? Riding the lower spring (L12g 6800), A from 6801 (launch 6825):
brute force over Left on/off in the frames around the launch; report the leftward distance 20 frames after the launch."""
import itertools, sys
from l12h_lib import *
G = seg("L12g"); DIR = sys.argv[1] if len(sys.argv) > 1 else "Left"
e = BizHawk(log_name="fix_l12h_dash.log"); e.load("L12h_g_f6750"); run(e, G[6750:6800]); run(e, ["A"] * 15); base = e.msave()   # at 6815
res = []
for pat in itertools.product((0, 1), repeat=11):          # frames 6816..6826
    e.mload(base); seq = [(DIR + "+A") if p else "A" for p in pat] + [DIR + "+A"] * 19
    run(e, seq); s = rd(e)
    res.append((s["x"], s["spd"], s["H"], "".join(map(str, pat))))
res.sort()
print("most left:", res[:12]); print("most right:", res[-12:])
import collections
print(collections.Counter(r[1] for r in res))
e.close()

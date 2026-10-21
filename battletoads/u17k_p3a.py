"""Track K2, phase 3 stage 1: the jump at the rising head of snake 3 (K6 index 1508) k frames earlier (k < 0: later), by
cutting k frames at index `cut`; where do the head pauses go, when does the head reach (112, 7984), where is the toad then.
    python u17k_p3a.py <cut index> <k list> [hold list = lengths of the Right hold after Right+A x20 (K6 43)]"""
import sys, json
from u17k_sim import *
k6 = seg("K6")
cut = int(sys.argv[1])
ks = [int(v) for v in sys.argv[2].split(",")]
holds = [int(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else [43]
s = Sim(f"u17k_p3a_{cut}.log")
s.set_base(k6, 1500, every=20)
out = []
for k in ks:
    for hold in holds:
        pre = k6[:cut] + k6[cut + k:1508] if k >= 0 else k6[:cut] + [""] * (-k) + k6[cut:1508]
        ins = pre + ["Right+A"] * 20 + ["Right"] * hold + [""] * 400
        turn = [None]

        def stop(tr):
            if turn[0] is None and tr["head"] and tr["head"][0] == 112 and tr["head"][1] < 7984 and tr["n"] > 1600:
                turn[0] = tr["n"]            # the frame of the 16-px drop at the corner = K6's 1710
            return turn[0] is not None and tr["n"] >= turn[0] + 12
        tr = s.run(ins, 1760, stop=stop)
        line = (f"cut {cut} k {k} hold {hold}: jump at {len(pre)}; head pauses {[p for p in tr['hp'] if p > 1500]}; head at the (112,7984) corner at {turn[0]} "
                f"(K6 1710); toad 12 frames later {tr['toad']} (K6 (126, 7998, 0, 0, 1, 0)); hpmin {tr['hp_min']}; tail pauses {[p for p in tr['tp'] if p > 1500]}")
        print(line, flush=True)
        out.append(line)
open(FIX / f"u17k_p3a_{cut}.txt", "a").write("\n".join(out) + "\n")
s.close()

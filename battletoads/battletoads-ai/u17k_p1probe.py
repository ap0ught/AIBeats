import sys
from u17k_sim import *
k6 = seg("K6")
s = Sim("u17k_p1probe.log")
s.set_base(k6, 450, every=10)
runs = rle(k6[:409])
for st, b, n in runs:
    end = st + n
    if end < 255 or end >= 409:
        continue
    for kind, d in (("ins", 1), ("ins", 2), ("del", 1), ("ext", 1), ("ext", 2)):
        if kind == "ins":
            c = k6[:end] + [""] * d + k6[end:450 - d]
        elif kind == "del":
            if n <= d: continue
            c = k6[:end - d] + k6[end:450] + [""] * d
        else:
            c = list(k6[:450]); c[end:end + d] = [b] * d
        tr = s.run(c + [""] * 200, 640, stop=lambda t: len(t["tgone"]) >= 1)
        print(kind, end, d, "tgone", tr["tgone"], "tp", tr["tp"], "hp", tr["hp"], "toad", tr["toad"][:4], "hpmin", tr["hp_min"], flush=True)
s.close()

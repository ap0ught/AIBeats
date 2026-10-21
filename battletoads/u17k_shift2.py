"""Track K2: time-shift invariance.  P1 variants (single mutations of K6 between 300 and 409) whose snake-1 tail is gone at
579 + j with the toad standing at (449, 7678); behind each, K6[450:1992] shifted by j: does everything replay j later?"""
import sys, hashlib
from u17k_sim import *
k6 = seg("K6")
s = Sim("u17k_shift2.log")
tr0 = s.set_base(k6, 1992, every=10)
ram0 = None
s.run(k6, 579); ram0 = bytes(s.e.ram(0, 0x800))
print("K6: tgone", tr0["tgone"], "happ", tr0["happ"])
runs = rle(k6[:409])
seen = set()
for st, b, n in runs:
    end = st + n
    if end < 300 or end >= 409:
        continue
    for d in (1, 2):
        for kind in ("ins", "del", "ext"):
            if kind == "ins":
                c = k6[:end] + [""] * d + k6[end:450 - d]
            elif kind == "del":
                if n <= d: continue
                c = k6[:end - d] + k6[end:450] + [""] * d
            else:
                c = list(k6[:450]); c[end:end + d] = [b] * d
            tr = s.run(c + [""] * 200, 640, stop=lambda t: len(t["tgone"]) >= 1)
            if not tr["tgone"]:
                continue
            j = tr["tgone"][0] - 579
            ok = tr["toad"][:4] == (449, 7678, 0, 0) and tr["hp_min"] == 47
            if not ok or j == 0 or j in seen:
                continue
            ram = bytes(s.e.ram(0, 0x800))
            diff = [hex(i) for i in range(0x800) if ram[i] != ram0[i] and not 0x100 <= i < 0x200]
            full = c[:450] + [""] * j + k6[450:1992] if j > 0 else c[:450 + j] + k6[450:1992]
            tr2 = s.run(full + [""] * 60, 1992 + j + 20, stop=lambda t: len(t["happ"]) >= 4)
            print(f"{kind} {end} {d}: shift {j}; RAM bytes differing at tail-gone: {len(diff)} {diff[:24]}; shifted replay happ {tr2['happ']} "
                  f"tgone {tr2['tgone']} (expect {[x + j for x in tr0['happ'][1:]]}) hpmin {tr2['hp_min']} head pauses {[p - j for p in tr2['hp'] if p > 579 + j] == [p for p in tr0['hp'] if p > 579]} "
                  f"tail pauses {[p - j for p in tr2['tp'] if p > 579 + j] == [p for p in tr0['tp'] if p > 579]}", flush=True)
            seen.add(j)
s.close()

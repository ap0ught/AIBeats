"""TOWER1 probe: the cam-4458 Hornhead (63 hp) with a GROUND kick as the first hit (750 points instead of the flying
kick's 1,000 - the score at the tower's end has to equal the old run's). From piece st2 cut before the TAS's air kick.
Stage 1 scan: fly on without B, land, wait w, [brake], dir+B -> first hit (+750)."""
import sys
from tw1_lib import *
p = load_piece("st2")
ins = p["inputs"]
# find the air kick of the second Hornhead: the first input with B after k=1500
k = p["base_k"]; cut = None
for i, b in enumerate(ins):
    if k >= 1520 and "B" in bt(b): cut = i; break
    k += 1
print("cut at piece index", cut, "k", p["base_k"] + cut, "input", ins[cut])
e = BizHawk(log_name="tw1_e2a.log"); e.load(p["base"]); run(e, ins[:cut]); root = e.msave()
def sc(m): return int("".join(str(m[0x5F4 + i] & 15) for i in range(6)))
def horn(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x5c: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q])
m = e.ram(0, 0x800); s = rdm(m); print("state:", fmt(p["base_k"] + cut, "", s)[:110], "score", sc(m), "horn", horn(m))
res = []
for air in ("Right", ""):
  for w in range(0, 26):
    for pre in ([], [""], ["Left"], ["", ""], ["Left", ""]):
        for kick in ("Right+B", "B"):
            e.mload(root); seq = []
            # fly on without the kick until landed
            n = 0
            while True:
                mm = e.ram(0, 0x800)
                if mm[0x475] == 0 and n > 0: break
                e.step(bt(air), 1); seq.append(air); n += 1
                if n > 40: break
            seq2 = ["Right"] * w + pre + [kick]
            sc0 = sc(e.ram(0, 0x800)); hit = None; an = set()
            for j, b in enumerate(seq2 + [""] * 26):
                e.step(bt(b), 1); mm = e.ram(0, 0x800)
                if j >= len(seq2) - 1: an.add(mm[0x3B5])
                if mm[0x51A] < 47: break
                if sc(mm) != sc0: hit = (len(seq) + j + 1, sc(mm) - sc0, mm[0x3FD] | mm[0x3EE] << 8, horn(mm)); break
            if hit: res.append((hit[0], air, w, pre, kick, hit[1], hit[2], hit[3], sorted(an)))
res.sort(key=lambda r: r[0])
for r in res[:30]: print(r)
print(len(res), "hits")
e.close()

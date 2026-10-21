"""probe: which RAM bytes differ in Level 9's first frames behind a new Level 8 tail (old = behind L8c)
    python u16a_p2.py <fight json> <start> <first> [n=40]"""
import json, sys
from u16a_lib import *
fj = json.load(open(sys.argv[1])); start = int(sys.argv[2]); first = sys.argv[3]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 40
old = seg("L8c"); nxt = seg("L9heli_c2")
pre = old[:3113] + list(fj["arrival_prefix"]) + list(fj["inputs"])
e = BizHawk(log_name="u16a_p2.log")
e.load("L8c_end0"); REF = []
for b in nxt[:N]:
    e.step(bt(b), 1); REF.append(bytes(e.ram(0, 0x800)))
e.load("L6c_end0")
for b in pre: e.step(bt(b), 1)
pat = ("A", "B") if first == "A" else ("B", "A"); stage = 0
for k in range(1200):
    b = "" if k < start else pat[(k - start) % 2]
    s = e.step(bt(b), 1)
    if stage == 0 and s.level == 11: stage = 1
    if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0: stage = 2
    if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0: break
print("placed at", len(pre) + k + 1)
for j in range(N):
    e.step(bt(nxt[j]), 1); m = bytes(e.ram(0, 0x800))
    d = [a for a in range(0x800) if m[a] != REF[j][a] and not (0x100 <= a < 0x200)]
    print(j + 1, len(d), [(hex(a), REF[j][a], m[a]) for a in d][:14])
e.close()

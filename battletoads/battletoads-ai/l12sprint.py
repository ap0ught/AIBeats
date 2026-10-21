"""Revolution cluster 1: legal double-tap sprint jump from the x-298 platform (replaces the TAS's L+R+A at step 861)."""
import json, re, sys
from toads.emulator import BizHawk, PROJECT
rows = []
for ln in open(PROJECT / "tas" / "watch_1p_l12.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", ln)
    if m: rows.append(tuple(int(v) for v in m.groups()))
pl = next(i for i, r in enumerate(rows) if r[1] == 136 and r[2] == 30); rows = rows[pl:]
TAS = [tuple(b for b in s.split("+") if b) for s in json.load(open(PROJECT / "knowledge" / "tas1p_l12_inputs.json"))]
def st(r): return (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x475], r[0x4B1], r[0x3B5], r[0x565], r[0x51A])
e = BizHawk(log_name="l12sprint.log"); e.load("L12_r1_solved")
e.step((), 1); print("after 857", st(e.ram_all()), "TAS", rows[858][1:6])
e.step((), 1); print("after 858", st(e.ram_all()), "TAS", rows[859][1:6])
root = e.msave()
L, N, LA = ("Left",), (), ("Left", "A")
variants = {
  "tas-like(859 idle,860 L,861 -,862+ LA)": [N, L, N] + [LA] * 21 + [L] * 14,
  "859 L,860 -,861+ LA": [L, N] + [LA] * 22 + [L] * 14,
  "859 -,860 L,861 -,862 L,863+ LA": [N, L, N, L] + [LA] * 20 + [L] * 14,
}
for name, seq in variants.items():
    e.mload(root); tr = []
    for i, b in enumerate(seq):
        e.step(b, 1); tr.append(st(e.ram_all()))
    for i in range(20): e.step(L if i < 1 else (), 1); tr.append(st(e.ram_all()))
    print("==", name)
    for i in range(0, len(tr), 3):
        s = 859 + i; t = rows[s + 1] if s + 1 < len(rows) else None
        print(f"  s{s} x{tr[i][0]} h{tr[i][1]} z{tr[i][2]} st{tr[i][3]} an{tr[i][4]} spd{tr[i][5]} hp{tr[i][6]}   TAS x{t[1]} h{t[2]} z{t[3]} an{t[5]}")
e.close()

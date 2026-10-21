"""TOWER1 route A: the exact rejoin after the cam-4096 Hornhead, second version (tight frame budget).
Target = the old run one frame into its jump to the spring (old row 2680): x, x sub-pixel, height sub-pixel, speed, $0B.
  - two hops (A held 8 and 10 frames) put the height sub-pixel on the old run's line;
  - Left / Right held for some of their air frames shifts x by sub-pixel amounts at no cost in frames;
  - then standing, and the old run's kind of run-up (Left x b, Right, gap, Right x c, -, Right+A).
Hop drift and run-up are tabulated separately (flat ground: translation invariant) and combined.
    python tw1_joinA4.py <piece standing for old row 2640> <out> [h1 h2]"""
import sys, itertools
from tw1_lib import *
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
def oldm(r): return buf[(r + 1) * 2048:(r + 2) * 2048]
p = load_piece(sys.argv[1]); out = sys.argv[2]
H1, H2 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (8, 10)
e = BizHawk(log_name="tw1_joinA4.log"); e.load(p["base"]); run(e, p["inputs"])
m = e.ram(0, 0x800); om = oldm(2639); need = (om[0x0B] - m[0x0B]) % 256; L = 40 + need
for _ in range(4): e.step((), 1)
pre0 = e.msave(); L -= 4
tm = oldm(2679); tgt = rdm(tm); PT = tgt["x"] * 256 + tgt["sub"]
def P(mm): return (mm[0x3FD] | mm[0x3EE] << 8) * 256 + mm[0x448]
def line(mm): return (mm[0x466] - (81 - 79 * mm[0x0B])) % 256
def hops(d1, n1, d2, n2):
    """hop H1 with direction d1 held for its first n1 air frames, hop H2 with d2 for n2; -> (inputs, ram) once standing still"""
    e.mload(pre0); seq = []
    for h, d, n in ((H1, d1, n1), (H2, d2, n2)):
        j = 0; first = True
        while True:
            mm = e.ram(0, 0x800)
            if mm[0x475] == 0 and not first: break
            b = ("A" if j < h else "")
            if d and j < n: b = norm(b + "+" + d)
            e.step(bt(b), 1); seq.append(norm(b)); j += 1; first = False
            if j > 90: return None, None
        for _ in range(3): e.step((), 1); seq.append("")
    j = 0
    while True:
        mm = e.ram(0, 0x800)
        if mm[0x565] == 0 and mm[0x3B5] == 1: break
        e.step((), 1); seq.append(""); j += 1
        if j > 40: return None, None
    return seq, mm
s0, m0 = hops("", 0, "", 0)
assert line(m0) == 0, f"hops {H1},{H2} do not give the old height sub-pixel phase (offset {line(m0)})"
FACE0 = m0[0x4A2] & 64; root = e.msave(); P0 = P(m0)
print(f"budget {L} frames; plain hops {len(s0)} frames; standing at x {P0 // 256}.{P0 % 256}; target shift {PT - P0}")
# run-ups from the standing state
mains = []
for b in range(6, 30):
    for gap in (1, 2):
        for c in range(4, 26):
            seq = ["Left"] * b + ["Right"] + [""] * gap + ["Right"] * c + ["", "Right+A"]
            if len(s0) + len(seq) > L: continue
            e.mload(root); run(e, seq); mm = e.ram(0, 0x800); t = rdm(mm)
            if (t["z"], t["H"], t["spd"], t["face"]) == (tgt["z"], tgt["H"], tgt["spd"], tgt["face"]):
                mains.append((P(mm) - P0, seq))
print(len(mains), "run-ups fit; shifts", sorted(set(d for d, _ in mains))[:30], "...")
need_shift = {}
for dm, seq in mains: need_shift.setdefault(PT - P0 - dm, []).append(seq)
found = None
for d1, d2 in itertools.product(("", "Left", "Right"), repeat=2):
    for n1 in (range(1, 30) if d1 else [0]):
        for n2 in (range(1, 32) if d2 else [0]):
            seq, mm = hops(d1, n1, d2, n2)
            if seq is None or line(mm) != 0 or (mm[0x4A2] & 64) != FACE0: continue
            dh = P(mm) - P0
            if dh in need_shift:
                for ru in sorted(need_shift[dh], key=len):
                    if len(seq) + len(ru) <= L:
                        full = seq + [""] * (L - len(seq) - len(ru)) + ru
                        e.mload(pre0); run(e, full); m2 = e.ram(0, 0x800); t = rdm(m2)
                        ok = (t["x"], t["sub"], t["z"], t["H"], t["spd"], t["face"]) == (tgt["x"], tgt["sub"], tgt["z"], tgt["H"], tgt["spd"], tgt["face"]) and m2[0x466] == tm[0x466] and m2[0x0B] == tm[0x0B]
                        if ok: found = full; break
            if found: break
        if found: break
    if found: break
if found:
    seq = [""] * 4 + found
    save_piece(out, p["base"], p["base_k"], p["inputs"] + [norm(b) for b in seq], rn=2680, parent=sys.argv[1])
    e.load(p["base"]); run(e, p["inputs"] + seq); mm = e.ram(0, 0x800)
    d = [(a, mm[a], tm[a]) for a in range(0x3B5, 0x5B0) if mm[a] != tm[a]]
    k = p["base_k"] + len(p["inputs"]) + len(seq)
    print(f"saved {out}: k end {k} (old 2680): G {2680 - k}; object-table bytes that differ:", " ".join(f"${a:03X}:{x:02x}/{y:02x}" for a, x, y in d)[:300])
    e.save(f"tw1_{out}_end")
else:
    print("no exact rejoin found")
e.close()

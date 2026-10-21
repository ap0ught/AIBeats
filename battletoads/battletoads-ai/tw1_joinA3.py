"""TOWER1 route A: the exact rejoin after the cam-4096 Hornhead (x, x sub-pixel, height sub-pixel, speed, $0B all the
old run's on the jump frame, old row 2680).  A 12-frame hop (height sub-pixel), a small walk that sets the x
sub-pixel, standing, then the old run's kind of run-up (Left x b, Right, gap, Right x c, -, Right+A).
Walks on flat ground are translation invariant, so the small walk and the run-up are tabulated separately and combined.
    python tw1_joinA3.py <piece standing for old row 2640> <out>"""
import sys
from tw1_lib import *
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
def oldm(r): return buf[(r + 1) * 2048:(r + 2) * 2048]
p = load_piece(sys.argv[1]); out = sys.argv[2]
e = BizHawk(log_name="tw1_joinA3.log"); e.load(p["base"]); run(e, p["inputs"])
m = e.ram(0, 0x800); om = oldm(2639); need = (om[0x0B] - m[0x0B]) % 256; L = 40 + need
# the hop: A held h frames; the height sub-pixel then counts -79 a frame on the ground, in the old run it is
# (81 - 79 * $0B) mod 256 on this ledge (old row 2641: $0B 0, sub-pixel 81)
pre0 = e.msave(); hop = None
def do_hops(hs, a1=4):
    e.mload(pre0); cand = [""] * a1
    run(e, cand)
    for h in hs:
        run(e, ["A"] * h); cand += ["A"] * h; n = 0
        while True:
            mm = e.ram(0, 0x800)
            if mm[0x475] == 0 and n > 0: break
            e.step((), 1); cand.append(""); n += 1
            if n > 90: break
        for _ in range(3): e.step((), 1); cand.append("")
    for _ in range(3): e.step((), 1); cand.append("")
    mm = e.ram(0, 0x800)
    return cand, (mm[0x466] - (81 - 79 * mm[0x0B])) % 256
opts = []
c0, d0 = do_hops([])
if d0 == 0: opts.append(c0)
for h in range(1, 26):
    c, d = do_hops([h])
    if d == 0: opts.append(c)
if not opts:
    for h1 in range(1, 21):
        for h2 in range(h1, 21):
            c, d = do_hops([h1, h2])
            if d == 0: opts.append(c)
assert opts, "no hop puts the height sub-pixel in the old phase"
hop = min(opts, key=len)
print("hops:", len(hop), "frames, A held", sum(1 for b in hop if b == "A"))
e.mload(pre0); run(e, hop)
root = e.msave(); L2 = L - len(hop)
def P(mm): return (mm[0x3FD] | mm[0x3EE] << 8) * 256 + mm[0x448]
mm = e.ram(0, 0x800); P0 = P(mm); FACE0 = mm[0x4A2] & 64; print("after the hop: x", P0 // 256, "sub", P0 % 256, "spd", mm[0x565], "facing", mm[0x4A2] & 64, "frames left", L2)
tm = oldm(2679); tgt = rdm(tm); PT = tgt["x"] * 256 + tgt["sub"]
# 1. small walks that end standing still, facing as at the start
pres = {(): (0, 0)}
pats = []
for nL in range(1, 13):
    for nR in range(0, 13):
        for st in (8, 14):
            pats.append(["Left"] * nL + [""] * st + (["Right"] * nR + [""] * st if nR else []))
            pats.append(["Right"] * nL + [""] * st + (["Left"] * nR + [""] * st if nR else []))
for seq in pats:
    e.mload(root); run(e, seq); mm = e.ram(0, 0x800)
    if mm[0x565] == 0 and mm[0x475] == 0 and mm[0x3B5] == 1 and (mm[0x4A2] & 64) == FACE0:
        pres[tuple(seq)] = (P(mm) - P0, mm[0x4A2] & 64)
print(len(pres), "small walks; shifts (1/256 px):", sorted(set(v[0] for v in pres.values()))[:40])
# 2. the run-up from the root state, per facing at its start
mains = []
for b in range(8, 36):
    for gap in (1, 2):
        for c in range(6, 34):
            seq = ["Left"] * b + ["Right"] + [""] * gap + ["Right"] * c + ["", "Right+A"]
            e.mload(root); run(e, seq); mm = e.ram(0, 0x800); t = rdm(mm)
            if (t["z"], t["H"], t["spd"], t["face"]) == (tgt["z"], tgt["H"], tgt["spd"], tgt["face"]):
                mains.append((P(mm) - P0, seq))
print(len(mains), "run-ups; target shift", PT - P0)
cands = []
for pre, (dp, face) in pres.items():
    for dm, seq in mains:
        if dp + dm == PT - P0 and len(pre) + len(seq) <= L2:
            cands.append((len(pre) + len(seq), list(pre), seq))
cands.sort(key=lambda c: c[0])
print(len(cands), "combinations predicted exact")
ok = None
for tot, pre, seq in cands[:60]:
    full = pre + [""] * (L2 - tot) + seq
    e.mload(root); run(e, full); mm = e.ram(0, 0x800); t = rdm(mm)
    good = (t["x"], t["sub"], t["z"], t["H"], t["spd"], t["face"]) == (tgt["x"], tgt["sub"], tgt["z"], tgt["H"], tgt["spd"], tgt["face"]) and mm[0x466] == tm[0x466] and mm[0x0B] == tm[0x0B]
    if good:
        ok = full; break
    else:
        nfail = globals().get("nfail", 0) + 1; globals()["nfail"] = nfail
        if nfail <= 3: print("  predicted but not exact:", (t["x"], t["sub"], t["z"], t["H"], t["spd"], t["face"]), "Hsub", mm[0x466], "t", mm[0x0B], "| want", (tgt["x"], tgt["sub"], tgt["z"], tgt["H"], tgt["spd"], tgt["face"]), tm[0x466], tm[0x0B])
if ok:
    seq = hop + ok
    save_piece(out, p["base"], p["base_k"], p["inputs"] + [norm(b) for b in seq], rn=2680, parent=sys.argv[1])
    e.load(p["base"]); run(e, p["inputs"] + seq); mm = e.ram(0, 0x800)
    d = [(a, mm[a], tm[a]) for a in range(0x3B5, 0x5B0) if mm[a] != tm[a]]
    k = p["base_k"] + len(p["inputs"]) + len(seq)
    print(f"saved {out}: k end {k} (old 2680): G {2680 - k}; object-table bytes that differ from the old frame:", " ".join(f"${a:03X}:{x:02x}/{y:02x}" for a, x, y in d))
    e.save(f"tw1_{out}_end")
else:
    print("no exact combination verified")
e.close()

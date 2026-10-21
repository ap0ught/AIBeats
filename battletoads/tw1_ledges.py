"""TOWER1: from wind face 1's pole to the H-4382 ring over the six green ledges, in whatever phase of $0B the run is.

    python tw1_ledges.py <piece> <drop> <out>     piece minus its last <drop> inputs must stand for the old run
                                                   after its input 4873 (hanging on the pole, one frame before the release)
Line: release (Down+Left) on the old run's frame, drop, wait w0, sprint Left round the tower, one jump straight onto
L1 (found by tw1_exit.py: Left, -, Left x52, Left+A x20, Left), hops L1 -> L2 -> H 4094 with enough Left in the air to
stand on x 303 like the old run, then the old run's own inputs from the H-4094 ledge to the ring (A12r[5114:5191]).
w0 is the smallest wait for which every ledge is there AND the ring is reached with $0B ≡ the old run's (mod 8) -
the enemies behind it are clocked on that. Prints the timeline; saves logs/fix/tw1_<out>.json (stands for old row 5191)."""
import sys
from tw1_lib import *

src, drop, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
def old(r): return rdm(buf[(r + 1) * 2048:(r + 2) * 2048])
p = load_piece(src); pre = p["inputs"][:len(p["inputs"]) - drop] if drop else p["inputs"]
e = BizHawk(log_name=f"tw1_ledges_{out}.log"); e.load(p["base"]); run(e, pre)
s = rd(e); o = old(4873)
print("start", fmt(p["base_k"] + len(pre), "", s)[:120], "| old 4873:", o["x"], o["H"], o["an"], "| t", s["t"], "old t", o["t"])
assert s["an"] in (94, 95, 96), "not on the pole"
seq = ["Down+Left"]; e.step(bt("Down+Left"), 1)
while True:
    e.step((), 1); seq.append(""); s = rd(e)
    if s["z"] == 0 and s["an"] == 1: break
    assert len(seq) < 80 and s["hp"] >= 47, "the drop went wrong"
free = e.msave(); print("free after", len(seq), "frames at", s["x"], s["H"], "t", s["t"])
RUNJ = ["Left", "", "Left"] + ["Left"] * 52 + ["Left+A"] * 20
oR = old(5190)

def landed(H):
    s = rd(e); return s["z"] == 0 and s["H"] == H and s["hp"] >= 47

def attempt(w0):
    """-> (inputs after `free`, info) or (None, why)"""
    e.mload(free); ins = [""] * w0 + RUNJ
    run(e, ins)
    k = 0
    while not rd(e)["z"] == 0:                                # steer Left until something is landed on
        e.step(bt("Left"), 1); ins.append("Left"); k += 1
        if k > 30: return None, "no landing after the jump"
    s = rd(e)
    if s["H"] != 3973: return None, f"L1 missed (landed at H {s['H']})"
    a_t = s["t"]; x1 = s["x"]
    onl1 = e.msave(); best = None
    for w1 in range(0, 70):
        for n in range(0, 15):
            e.mload(onl1)
            hop = [""] * w1 + ["Left+A"] * n + ["A"] * (14 - n) + [""]
            run(e, hop)
            if not landed(4029): continue
            c_t = rd(e)["t"]
            hop2 = [norm(A[r]) for r in range(5027, 5043)]    # A x14, Left+A (tap), '' -> H 4094
            run(e, hop2)
            s = rd(e)
            if not landed(4094): continue
            if s["x"] != 303: continue
            best = (w1, n, hop + hop2, c_t); break
        if best: break
    e.mfree(onl1)
    if not best: return None, f"L1 at t {a_t} x {x1}: no way over L2 to x 303 on the H-4094 ledge"
    ins += best[2]
    e.mload(free); run(e, ins)
    up = [norm(A[r]) for r in range(5114, 5191)]
    run(e, up); s = rd(e)
    ok = (s["x"], s["H"], s["z"], s["spd"], s["an"], s["face"]) == (oR["x"], oR["H"], oR["z"], oR["spd"], oR["an"], oR["face"]) and s["hp"] >= 47
    if not ok: return None, f"L1 t {a_t}, L2 t {best[3]} (wait on L1 {best[0]}, Left x{best[1]}): upper ledges failed, end x={s['x']} H={s['H']} z={s['z']} hp={s['hp']}"
    return ins + up, dict(w0=w0, a_t=a_t, w1=best[0], n=best[1], c_t=best[3], ring_t=s["t"], mod8=(s["t"] - oR["t"]) & 7, cam=s["cam"], oldcam=oR["cam"], sub=s["sub"], oldsub=oR["sub"])

found = None
for w0 in range(0, 300):
    ins, info = attempt(w0)
    if ins is None:
        if w0 % 8 == 0 or w0 < 3: print(f"w0={w0}: {info}", flush=True)
        continue
    print(f"w0={w0}: OK {info}", flush=True)
    if info["mod8"] == 0:
        found = (ins, info); break
if found:
    ins, info = found
    full = pre + seq + ins
    assert not any(banned(b) for b in full)
    save_piece(out, p["base"], p["base_k"], [norm(b) for b in full], rn=5191, parent=src, ledges=info)
    e.load(p["base"]); run(e, full); e.save(f"tw1_{out}_end")
    k = p["base_k"] + len(full)
    print(f"saved {out}: ring reached at k={k} (old run 5191): net gain {5191 - k} frames; camera {info['cam']} (old {info['oldcam']})")
else:
    print("no line found")
e.close()

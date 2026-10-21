"""TOWER1: the big walker (0x62, 111 hp, camera 3408) starts its flight on a random frame after it has risen to
(400,2622) (old run: row 3458, the first possible). Find Select presses (old rows 3380..3457 of a piece standing for
old row <rn>) that make it start on a row s with s ≡ <want> (mod 16), s as small as possible, and build the piece:
old inputs to 3457 with those Selects, then (s - 3458) idle frames on the ledge -> stands for old row 3458 again
(the old fight then runs s - 3458 frames later, in the old run's phase of $0B modulo 16).
    python tw1_wstart.py <piece (rn <= 3380)> <want: s mod 16> <out> [max s]"""
import sys, random
from tw1_lib import *
src, want, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; smax = int(sys.argv[4]) if len(sys.argv) > 4 else 3500
A = seg("A12r")
p = load_piece(src); r0 = p["rn"]
e = BizHawk(log_name="tw1_wstart.log"); e.load(p["base"]); run(e, p["inputs"])
pre = []
for r in range(r0, 3380): e.step(bt(A[r]), 1); pre.append(norm(A[r]))
root = e.msave()
def walk(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x62: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x583 + q])
    return None
def trial(sel):
    e.mload(root); st = None
    for r in range(3380, smax + 2):
        b = A[r] if r < 3458 else ""                           # from 3458 the toad just stands on the ledge
        if r in sel: b = norm(b + "+Select")
        e.step(bt(b), 1)
        if r >= 3440:
            m = e.ram(0, 0x800); w = walk(m)
            if m[0x51A] < 47: return None
            if w and w[2] == 1: return r
    return None
rnd = random.Random(7); best = None; hist = {}
cands = [frozenset()] + [frozenset([j]) for j in range(3457, 3379, -1)]
for t in range(1500): cands.append(frozenset(j for j in range(3380, 3458) if rnd.random() < rnd.choice((0.03, 0.08, 0.2))))
for i, sel in enumerate(cands):
    s = trial(sel)
    hist[s] = hist.get(s, 0) + 1
    if s is not None and s % 16 == want % 16 and (best is None or s < best[0]):
        best = (s, sel); print(f"try {i}: start at {s} with Select on {sorted(sel)}", flush=True)
        if s <= 3458 + 16: break
    if best and i > 400: break
print("start-row histogram (top):", sorted(((v, k) for k, v in hist.items()), reverse=True)[:14])
if best:
    s, sel = best
    ins = pre + [norm(A[r] + ("+Select" if r in sel else "")) for r in range(3380, 3458)] + [""] * (s - 3458)
    e.load(p["base"]); run(e, p["inputs"] + ins)
    m = e.ram(0, 0x800); print("end:", fmt(p["base_k"] + len(p["inputs"]) + len(ins), "", rdm(m))[:120], "walker", walk(m))
    save_piece(out, p["base"], p["base_k"], p["inputs"] + ins, rn=3458, parent=src, wstart=s, sel=sorted(sel))
    e.save(f"tw1_{out}_end")
    print(f"saved {out}: walker starts at old row {s} (+{s - 3458}), G loses {s - 3458}")
e.close()

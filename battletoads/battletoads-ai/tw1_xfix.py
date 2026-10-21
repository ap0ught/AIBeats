"""TOWER1: one or two input replacements inside a stretch of old (A12r) inputs so that the toad arrives at an old row with
the old run's exact x / height / speed / camera (removes a 1-3 px offset picked up earlier).
    python tw1_xfix.py <piece> <old row r0 the piece stands for> <first row> <last row> <check row> <out piece>"""
import sys, itertools
from tw1_lib import *
src, r0, ra, rb, rc, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
old = rdm(buf[(rc + 1) * 2048:(rc + 2) * 2048])
p = load_piece(src)
e = BizHawk(log_name="tw1_xfix.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def test(repl):
    e.mload(root)
    for r in range(r0 + 1, rc + 1):
        e.step(bt(repl.get(r, A[r])), 1)
    s = rd(e)
    return s
s = test({}); print("plain:", s["x"], s["H"], s["z"], s["spd"], s["cam"], "| old:", old["x"], old["H"], old["z"], old["spd"], old["cam"], "t par", (s["t"] - old["t"]) & 1)
TB = ["", "Left", "Left+A", "A", "Right", "Right+A"]
good = []
singles = [(r, b) for r in range(ra, rb + 1) for b in TB if b != A[r]]
for (r, b) in singles:
    s = test({r: b})
    if (s["x"], s["H"], s["z"], s["spd"]) == (old["x"], old["H"], old["z"], old["spd"]):
        good.append(({r: b}, s["cam"] - old["cam"], s["sub"])); print("single", r, repr(b), "cam diff", s["cam"] - old["cam"], "sub", s["sub"], "old sub", old["sub"], flush=True)
if not [g for g in good if g[1] == 0]:
    for (r1, b1), (r2, b2) in itertools.combinations(singles, 2):
        if r1 == r2: continue
        s = test({r1: b1, r2: b2})
        if (s["x"], s["H"], s["z"], s["spd"]) == (old["x"], old["H"], old["z"], old["spd"]):
            good.append(({r1: b1, r2: b2}, s["cam"] - old["cam"], s["sub"])); print("pair", r1, repr(b1), r2, repr(b2), "cam diff", s["cam"] - old["cam"], "sub", s["sub"], flush=True)
            if s["cam"] == old["cam"] and len([g for g in good if g[1] == 0]) >= 6: break
best = sorted(good, key=lambda g: (abs(g[1]), abs(g[2] - old["sub"])))
if best:
    repl = best[0][0]; print("using", repl)
    ins = [norm(repl.get(r, A[r])) for r in range(r0 + 1, rc + 1)]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + ins, rn=rc + 1, parent=src, repl={str(k): v for k, v in repl.items()})
e.close()

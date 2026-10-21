"""TOWER1: re-roll the dice behind a new prefix so that a stretch of the old run (A12r) replays: Select presses are
added (or taken away) one divergence at a time, like rngfit.py, but the presses may also go on the last frames of
the prefix piece (the frames before the old stretch starts), and the comparison tolerances are explicit.

    python tw1_dice.py <piece> <tail W> <old row to reach> <out piece> [env]
piece: stands for the old run after its input rn-1 (piece["rn"]); the old inputs rn..<row> are appended.
tail W: how many of the piece's own last frames may get a Select.
env TW1_DT (toad x tolerance, default 0), TW1_DE (enemy x/height tolerance, default 1), TW1_DW (window back from a
divergence, default 170), TW1_DM (frames a fix must hold, default 10), TW1_DRAND (random subsets tried, default 800),
TW1_DBTN (extra dice buttons besides Select: e.g. 'Up,Down' - only used on frames whose input has no direction)
Compared every frame: toad x / 16-bit height / airborne / health and every Hornhead / walker (id, x, height, health).
-> logs/fix/tw1_<out>.json, bookmark tw1_<out>_end. Prints each re-roll."""
import os, random, sys, time
from tw1_lib import *

src, W, rend, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
DT = int(os.environ.get("TW1_DT", 0)); DE = int(os.environ.get("TW1_DE", 1)); DW = int(os.environ.get("TW1_DW", 170))
DM = int(os.environ.get("TW1_DM", 10)); DRAND = int(os.environ.get("TW1_DRAND", 800))
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
p = load_piece(src); r0 = p["rn"]
tail = p["inputs"][len(p["inputs"]) - W:] if W else []
head = p["inputs"][:len(p["inputs"]) - W]
seq = [norm(b) for b in tail] + [norm(A[r]) for r in range(r0, rend + 1)]
N = len(seq)

def old(i):
    """old state after seq[i] (i >= W), None for the prefix's own frames"""
    if i < W: return None
    r = r0 + (i - W)
    return rdm(buf[(r + 1) * 2048:(r + 2) * 2048])

def differs(s, o):
    if s["z"] != o["z"] or s["H"] != o["H"] or s["hp"] != o["hp"] or abs(dx(s["x"], o["x"])) > DT: return "toad"
    a = sorted((d[0], d[3], d[1], d[2]) for d in s["objs"] if d[0] in (0x5c, 0x62))
    b = sorted((d[0], d[3], d[1], d[2]) for d in o["objs"] if d[0] in (0x5c, 0x62))
    if len(a) != len(b): return "count"
    for u, v in zip(a, b):
        if u[0] != v[0] or u[1] != v[1] or abs(dx(u[2], v[2])) > DE or abs(u[3] - v[3]) > DE: return "enemy"
    return None

e = BizHawk(log_name=f"tw1_dice_{out}.log"); e.load(p["base"]); run(e, head)
CK = 8
ck = {0: e.msave()}                                            # index -> savestate under the CURRENT accepted `sel`
sel = set(); sel_btn = {}

def inp(i, s, sb):
    b = seq[i]
    if i in s: b = norm(b + "+Select")
    if i in sb: b = norm(b + "+" + sb[i])
    return b

def evalsel(s, sb, start, stop, keep=False):
    """first index >= start whose state differs from the old run's (N if none up to stop); start must be a checkpoint"""
    e.mload(ck[start]); why = None
    for i in range(start, min(stop, N)):
        e.step(bt(inp(i, s, sb)), 1)
        o = old(i)
        if o is not None:
            why = differs(rd(e), o)
            if why: return i, why
        if keep and (i + 1) % CK == 0:
            if i + 1 in ck: e.mfree(ck[i + 1])
            ck[i + 1] = e.msave()
    return min(stop, N), None

def base_ck(j): return max(k for k in ck if k <= j)

t0 = time.time(); fixes = []; rnd = random.Random(1)
pos = 0
while True:
    start = base_ck(pos)
    for k in [k for k in ck if k > start]: e.mfree(ck.pop(k))
    d, why = evalsel(sel, sel_btn, start, N, keep=True)
    if d >= N:
        break
    for k in [k for k in ck if k > d]: e.mfree(ck.pop(k))      # checkpoints past the divergence are of no use
    lo = max(0, d - DW)
    cands = [("t", (j,)) for j in range(d, lo - 1, -1)]
    best = (d, None)
    tried = 0
    def attempt(kind, js):
        """quick look first (does the variant get DM frames past the divergence?), only then the long one"""
        global best, tried
        s2 = set(sel) ^ set(js)
        j0 = min(js)
        tried += 1
        if tried % 200 == 0: print(f"    ... index {d} (old row {r0 + d - W}) [{why}]: {tried} tries, best holds to {best[0]}; {time.time() - t0:.0f}s", flush=True)
        r, _ = evalsel(s2, sel_btn, base_ck(j0), min(N, d + DM + 1))
        if r <= d + DM and r < N:
            if r > best[0] and best[0] <= d: best = (r, s2)   # (kept only as a fallback: some progress)
            return r
        r, _ = evalsel(s2, sel_btn, base_ck(j0), min(N, d + 400))
        if r > best[0]: best = (r, s2)
        return r
    for kind, js in cands:
        attempt(kind, js)
        if best[0] >= min(N, d + 400): break
    if best[0] < d + DM:
        free = list(range(lo, d + 1))
        for t in range(DRAND):
            dens = rnd.choice((0.03, 0.06, 0.12, 0.25, 0.5))
            js = tuple(j for j in free if rnd.random() < dens)
            if not js: continue
            attempt("r", js)
            if best[0] >= min(N, d + 400): break
    if best[1] is None or best[0] <= d:
        print(f"STUCK at seq index {d} (old row {r0 + d - W if d >= W else 'prefix'}) [{why}] after {tried} tries, {time.time() - t0:.0f}s", flush=True)
        break
    changed = sorted(set(sel) ^ best[1])
    sel = best[1]
    fixes.append((d, changed))
    pos = min(changed)
    print(f"  index {d} (old row {r0 + d - W}) [{why}]: Select toggled on {changed if len(changed) < 8 else str(len(changed)) + ' frames'} "
          f"({tried} tries) -> holds to index {best[0]} (old row {r0 + best[0] - W}); {time.time() - t0:.0f}s", flush=True)
# final replay and save
e.load(p["base"]); run(e, head)
final = [inp(i, sel, sel_btn) for i in range(N if d >= N else d)]
run(e, final)
s = rd(e)
print(f"{'DONE' if d >= N else 'PARTIAL'}: {len(final)} of {N} frames; Selects added {sorted(sel)}; end {fmt(p['base_k'] + len(head) + len(final), '', s)[:120]}", flush=True)
assert not any(banned(b) for b in final)
save_piece(out, p["base"], p["base_k"], head + final, rn=(rend + 1) if d >= N else (r0 + d - W), parent=src, sel=sorted(sel), done=d >= N)
e.save(f"tw1_{out}_end")
e.close()

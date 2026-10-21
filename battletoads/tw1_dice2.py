"""TOWER1: tw1_dice.py with lag handling (use this one for long stretches).

Re-rolls the dice behind a new prefix so that a stretch of the old run (A12r) replays: Select presses are added or
taken away one divergence at a time (nearest single frames first, then random subsets), like rngfit.py; the presses
may also go on the prefix's own last W frames; tolerances are explicit; frames the game drops (lag: $0B does not
tick) are handled the way rngfit does - a frame WE drop gets its input again, a frame only the OLD run dropped is
skipped (its next ticking frame's input is given instead).

    python tw1_dice2.py <piece> <tail W> <old row to reach> <out piece>
piece["rn"] = first old input to give.  env: TW1_DT (toad x tol, default 1), TW1_DE (enemy tol, default 1),
TW1_DW (window back, 170), TW1_DM (frames a fix must hold, 10), TW1_DRAND (random subsets, 800), TW1_DLOOK (400),
TW1_DEND=1: the stretch ends with the level change - the last 320 rows are only checked for the toad being alive and
the run counts as done when the level byte leaves 5.
-> logs/fix/tw1_<out>.json (rn = next old input), bookmark tw1_<out>_end."""
import os, random, sys, time
from tw1_lib import *

src, W, rend, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
DT = int(os.environ.get("TW1_DT", 1)); DE = int(os.environ.get("TW1_DE", 1)); DW = int(os.environ.get("TW1_DW", 170))
DM = int(os.environ.get("TW1_DM", 10)); DRAND = int(os.environ.get("TW1_DRAND", 800)); DLOOK = int(os.environ.get("TW1_DLOOK", 400))
DEND = int(os.environ.get("TW1_DEND", 0))
NOBODY = int(os.environ.get("TW1_DNOBODY", 1))               # dead bodies (health 0) are not compared
TWEAK = int(os.environ.get("TW1_DTWEAK", 60))                 # frames back in which one input may be replaced on a toad mismatch
DH = int(os.environ.get("TW1_DH", 1))                      # airborne height tolerance (the height sub-pixel differs after a different landing)
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
p = load_piece(src); r0 = p["rn"]
tail = p["inputs"][len(p["inputs"]) - W:] if W else []
head = p["inputs"][:len(p["inputs"]) - W]
seq = [norm(b) for b in tail] + [norm(A[r]) for r in range(r0, rend + 1)]
N = len(seq)
def oldrow(i): r = r0 + (i - W); return buf[(r + 1) * 2048:(r + 2) * 2048]
_oc = {}
def old(i):
    if i < W: return None
    if i not in _oc: m = oldrow(i); _oc[i] = (rdm(m), m[0x0B])
    return _oc[i]
def otick(i):
    """did the old run's logic run on seq index i (>= W)?"""
    r = r0 + (i - W)
    return buf[(r + 1) * 2048 + 0x0B] != buf[r * 2048 + 0x0B]
def nxt_tick(i):
    j = i
    while j < N and not otick(j): j += 1
    return j

def differs(s, o):
    if s["lvl"] != o["lvl"]: return "level"
    if s["z"] != o["z"] or abs(s["H"] - o["H"]) > (DH if s["z"] else 0) or s["hp"] != o["hp"] or abs(dx(s["x"], o["x"])) > DT: return "toad"
    a = sorted((d[0], d[3], d[1], d[2]) for d in s["objs"] if d[0] in (0x5c, 0x62) and (d[3] > 0 or not NOBODY))
    b = sorted((d[0], d[3], d[1], d[2]) for d in o["objs"] if d[0] in (0x5c, 0x62) and (d[3] > 0 or not NOBODY))
    if len(a) != len(b): return "count"
    for u, v in zip(a, b):
        if u[0] != v[0] or u[1] != v[1] or abs(dx(u[2], v[2])) > DE or abs(u[3] - v[3]) > DE: return "enemy"
    return None

e = BizHawk(log_name=f"tw1_dice2_{out}.log"); e.load(p["base"]); run(e, head)
CK = 8
ck = {0: (e.msave(), 0)}                                       # seq index -> (savestate, inputs given so far) under the accepted sel
sel = set()

def inp(i, s):
    b = seq[i]
    return norm(b + "+Select") if i in s else b

def evalsel(s, start, stop, keep=False, record=None):
    """play from checkpoint `start`; -> (first index whose state differs from the old run's or min(stop, N), why)"""
    sid, glen = ck[start]
    e.mload(sid); i = start; lagrun = 0; given = glen
    tb = e.byte(0x0B)
    while i < min(stop, N):
        if keep and i % CK == 0 and i != start and lagrun == 0:
            if i in ck: e.mfree(ck[i][0])
            ck[i] = (e.msave(), given)
        if i < W:
            b = inp(i, s); e.step(bt(b), 1); given += 1
            if record is not None: record.append(b)
            tb = e.byte(0x0B); i += 1
            continue
        ot = otick(i)
        if not ot:
            sv = e.msave()
            b = inp(i, s); e.step(bt(b), 1); m = e.ram(0, 0x800)
            if m[0x0B] != tb:                                  # the old run dropped / froze this frame, we did not
                j = nxt_tick(i)
                if j - i > 3 or j >= N:
                    e.mfree(sv); return i, "freeze"
                e.mload(sv); i = j
                b = inp(i, s); e.step(bt(b), 1); m = e.ram(0, 0x800)
            e.mfree(sv)
        else:
            b = inp(i, s); e.step(bt(b), 1); m = e.ram(0, 0x800)
            if m[0x0B] == tb:                                  # we dropped a frame the old run did not: same input again
                given += 1; lagrun += 1
                if record is not None: record.append(b)
                if lagrun > 8: return i, "stall"
                continue
        lagrun = 0; given += 1
        if record is not None: record.append(b)
        tb = m[0x0B]
        sn = rdm(m); o = old(i)[0]
        if DEND and i >= N - 320:
            if sn["lvl"] != 5: return N, None                  # the level change: done
            if sn["hp"] < 47 or sn["lives"] < 4: return i, "dead"
        else:
            why = differs(sn, o)
            if why: return i, why
        i += 1
    return min(stop, N), None

def base_ck(j): return max(k for k in ck if k <= j)

t0 = time.time(); rnd = random.Random(int(os.environ.get("TW1_DSEED", 1))); pos = 0; d = 0; why = None; safe = -1; tweaks = []
while True:
    start = base_ck(pos)
    for k in [k for k in ck if k > start]: e.mfree(ck.pop(k)[0])
    d, why = evalsel(sel, start, N, keep=True)
    if d >= N: break
    for k in [k for k in ck if k > d]: e.mfree(ck.pop(k)[0])
    lo = max(0, d - DW)
    best = (d, None); tried = 0
    def attempt(js):
        global best, tried
        s2 = set(sel) ^ set(js); j0 = min(js); tried += 1
        if tried % 200 == 0: print(f"    ... index {d} (old row {r0 + d - W}) [{why}]: {tried} tries, best holds to {best[0]}; {time.time() - t0:.0f}s", flush=True)
        r, _ = evalsel(s2, base_ck(j0), min(N, d + DM + 1))
        if r <= d + DM and r < N:
            if r > best[0] and best[0] <= d: best = (r, s2)
            return r
        r, _ = evalsel(s2, base_ck(j0), min(N, d + DLOOK))
        if r > best[0]: best = (r, s2)
        return r
    tw = None
    if why in ("toad", "stall", "freeze") and TWEAK:
        # a pixel of drift at an edge (our x sub-pixel is not the old run's): one input replaced on one of the last
        # TWEAK frames, kept when the old track then holds DM frames; the one that holds longest wins
        for j in range(d, max(W, d - TWEAK) - 1, -1):
            keepb = seq[j]
            for b in ("", "Left", "Right", "A", "Left+A", "Right+A", "B", "Left+B", "Right+B", "Down"):
                if norm(b) == keepb: continue
                seq[j] = norm(b); tried += 1
                r, _ = evalsel(sel, base_ck(j), min(N, d + DM + 1))
                if r > d + DM or r >= N:
                    r, _ = evalsel(sel, base_ck(j), min(N, d + DLOOK))
                    if tw is None or r > tw[0]: tw = (r, j, norm(b))
            seq[j] = keepb
            if tw and tw[0] >= min(N, d + DLOOK): break
        if tw:
            seq[tw[1]] = tw[2]; pos = tw[1]
            print(f"  index {d} (old row {r0 + d - W}) [{why}]: input {tw[1]} (old row {r0 + tw[1] - W}) given {tw[2]!r} instead ({tried} tries) -> holds to index {tw[0]} (old row {r0 + tw[0] - W}); {time.time() - t0:.0f}s", flush=True)
            tweaks.append((r0 + tw[1] - W, tw[2]))
            continue
    for j in range(d, lo - 1, -1):
        attempt((j,))
        if best[0] >= min(N, d + DLOOK): break
    if best[0] < d + DM:
        free = list(range(max(lo, safe + 1), d + 1))             # (not before the last divergence already fixed: its luck must stay)
        if len(free) < 6: free = list(range(lo, d + 1))
        for t in range(DRAND):
            dens = rnd.choice((0.03, 0.06, 0.12, 0.25, 0.5))
            js = tuple(j for j in free if rnd.random() < dens)
            if js: attempt(js)
            if best[0] >= min(N, d + DLOOK): break
    if best[1] is None or best[0] <= d:
        print(f"STUCK at seq index {d} (old row {r0 + d - W if d >= W else 'prefix'}) [{why}] after {tried} tries, {time.time() - t0:.0f}s", flush=True)
        break
    changed = sorted(set(sel) ^ best[1]); sel = best[1]; pos = min(changed); safe = d
    print(f"  index {d} (old row {r0 + d - W}) [{why}]: Select toggled on {changed if len(changed) < 8 else str(len(changed)) + ' frames'} "
          f"({tried} tries) -> holds to index {best[0]} (old row {r0 + best[0] - W}); {time.time() - t0:.0f}s", flush=True)
# final replay: record what was actually given (lag frames repeat an input)
for k in [k for k in ck if k > 0]: e.mfree(ck.pop(k)[0])
rec = []
dd, _ = evalsel(sel, 0, N if d >= N else d, record=rec)
s = rd(e)
done = d >= N
print(f"{'DONE' if done else 'PARTIAL'}: {len(rec)} inputs for {dd} of {N} old frames ({len(rec) - dd:+d} lag); Selects on {len(sel)} frames; "
      f"end {fmt(p['base_k'] + len(head) + len(rec), '', s)[:110]} lvl {s['lvl']} lives {s['lives']} score {s['score']}", flush=True)
assert not any(banned(b) for b in rec)
save_piece(out, p["base"], p["base_k"], head + rec, rn=(rend + 1) if done else (r0 + dd - W), parent=src, sel=sorted(sel), done=done, tweaks=tweaks)
e.save(f"tw1_{out}_end")
e.close()

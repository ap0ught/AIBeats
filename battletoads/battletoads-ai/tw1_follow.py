"""TOWER1 (2026-10-10): follow the 1-player TAS's Level 12 with LEGAL inputs, frame by frame, and repair where our run
parts from it.  The TAS reference is its per-frame RAM (logs/fix/tas_l12.ram, rows relative to its placement frame).

    python tw1_follow.py <start piece or K:<A12r index>> <tas row r0> <tas row r1> <out piece> [env ...]

start: 'K:868' = the A12r state after 868 inputs (from the tw1_a_f* bookmarks), or the name of a tw1 piece
       (logs/fix/tw1_<piece>.json; the run continues at its end).  The start state stands for TAS row r0
       (our next input = the TAS's input r0+1).  The run stops at TAS row r1, or where nothing repairs it.
out:   logs/fix/tw1_<out>.json  {base, base_k, inputs (ALL inputs since the base bookmark), rn (next TAS row), edits}

What is compared after every frame: the toad's x (within TW1_XT px), 16-bit height, airborne flag, health; the
Hornheads / walkers (ids 5c, 62): count, health, x / height within TW1_ET.
Repairs, tried in this order when the tracks part at TAS row `bad`:
  toad:  one input replaced on one of the last TW1_WT frames; one frame put in (delay) or left out; two neighbours replaced
  enemy: Select added on one earlier frame (TW1_WS back), then pairs, then Up/Down singles (dice re-rolls)
A repair counts when the tracks then agree through bad+TW1_M; of those the one that holds longest is kept.
The TAS's Left+Right / Up+Down frames are given without the pair (legal); such frames usually need a repair or a
hand-made piece (see tw1_dash.py).  Nothing here writes memory.
"""
import json, os, sys, time
from tw1_lib import *

XT = int(os.environ.get("TW1_XT", 4))
ET = int(os.environ.get("TW1_ET", 3))
HT = int(os.environ.get("TW1_HT", 2))
PARITY = int(os.environ.get("TW1_PARITY", 1))
SPAWN_LAG = int(os.environ.get("TW1_SPAWN_LAG", 0))
PW = int(os.environ.get("TW1_PW", 320))
PW2 = int(os.environ.get("TW1_PW2", 130))
WT0 = int(os.environ.get("TW1_WT", 45))
WSP = int(os.environ.get("TW1_WSP", 170))
WS = int(os.environ.get("TW1_WS", 150))
M = int(os.environ.get("TW1_M", 14))
LOOK = int(os.environ.get("TW1_LOOK", 240))
ENEMY = (0x5c, 0x62)
TB = ["", "A", "Left", "Left+A", "Right", "Right+A"]
VERB = int(os.environ.get("TW1_VERB", 0))


def legal(b):
    v = set(bt(b))
    if "Left" in v and "Right" in v: v -= {"Left", "Right"}
    if "Up" in v and "Down" in v: v -= {"Up", "Down"}
    v.discard("Start")
    return "+".join(sorted(v, key=ORDER.index))


REFMODE = os.environ.get("TW1_REF", "tas")                  # 'tas' = the 1-player TAS; 'old' = our own A12r run (row r = after its input r)
_ref = {}
_oldram = None
_oldin = None
def refrow(r):
    global _oldram
    if REFMODE == "tas": return tasrow(r)
    if _oldram is None: _oldram = open(FIX / "tw1_a.ram", "rb").read()
    return _oldram[(r + 1) * 2048:(r + 2) * 2048]
def refin(r):
    global _oldin
    if REFMODE == "tas": return tasin(r)
    if _oldin is None: _oldin = seg("A12r")
    return _oldin[r]
def ref(r):
    if r not in _ref:
        m = refrow(r); _ref[r] = (rdm(m), m[0x0B])
    return _ref[r]

def rtick(r): return ref(r)[1] != ref(r - 1)[1]

def nxt_tick(r):
    while not rtick(r): r += 1
    return r


def compare(s, t):
    """None when our state s agrees with the TAS state t, else 'toad' / 'enemy'"""
    if s["z"] != t["z"] or abs(s["H"] - t["H"]) > HT or s["hp"] != t["hp"] or abs(dx(s["x"], t["x"])) > XT:
        return "toad"
    a = sorted((d[0], d[3], d[1], d[2]) for d in s["objs"] if d[0] in ENEMY)
    b = sorted((d[0], d[3], d[1], d[2]) for d in t["objs"] if d[0] in ENEMY)
    if PARITY and any(v[1] > 0 for v in b) and (s["t"] - t["t"]) & 1:
        return "parity"                                       # hits are only tested on every other tick of $0B: be in the TAS's phase
    if len(a) != len(b): return "spawn"
    for u, v in zip(a, b):
        if u[0] != v[0] or u[1] != v[1] or abs(dx(u[2], v[2])) > ET or abs(u[3] - v[3]) > ET: return "enemy"
    return None


class Follower:
    def __init__(self, e, base, base_k, pre, rn):
        """e stands at the state after `pre` (inputs since bookmark `base`, A12r index base_k); next TAS row = rn"""
        self.e, self.base, self.base_k = e, base, base_k
        self.out = list(pre)
        self.n0 = len(pre)
        self.rn = rn
        self.repl, self.sel, self.btn2, self.ins, self.skip = {}, set(), {}, {}, set()
        self.insdone = {}
        self.lagrun = 0; self.lags = 0; self.gain = 0; self.spawnlag = 0
        m = e.ram(0, 0x800); self.tb = m[0x0B]; self.s = rdm(m)
        self.why = None
        self.sv = {}
        self.snap()

    # ---- savestates -------------------------------------------------------------------------------------------
    def snap(self):
        n = len(self.out)
        if n in self.sv: self.e.mfree(self.sv[n][0])
        self.sv[n] = (self.e.msave(), self.rn, self.tb, dict(self.insdone), self.lagrun, self.s, self.spawnlag)
        if n % 64 == 0:                                       # thin out old ones
            for k in [k for k in self.sv if k < n - 420 and k % 16 and k != self.n0]:
                self.e.mfree(self.sv.pop(k)[0])

    def rewind_n(self, n):
        k = max(q for q in self.sv if q <= n)
        for q in [q for q in self.sv if q > k]:
            self.e.mfree(self.sv.pop(q)[0])
        sid, self.rn, self.tb, ins, self.lagrun, self.s, self.spawnlag = self.sv[k]
        self.insdone = dict(ins)
        self.e.mload(sid)
        del self.out[k:]

    def rewind_row(self, r):
        """back to the last saved point at which nothing for TAS row >= r has been given yet"""
        ks = [k for k, v in self.sv.items() if v[1] <= r and not v[3].get(r, 0) and not any(q >= r for q in v[3])]
        self.rewind_n(max(ks) if ks else self.n0)

    # ---- one frame ----------------------------------------------------------------------------------------------
    def button(self, r):
        b = self.repl.get(r, legal(refin(r)))
        if r in self.sel: b = norm(b + "+Select")
        if r in self.btn2: b = norm(b + "+" + self.btn2[r])
        return b

    def give(self, b):
        self.e.step(bt(b), 1)
        m = self.e.ram(0, 0x800)
        return m, rdm(m)

    def step(self):
        """one frame; True while on the TAS's track"""
        e = self.e
        while self.rn in self.skip: self.rn += 1
        r = self.rn
        q = self.insdone.get(r, 0)
        if q < len(self.ins.get(r, [])):                      # a frame put in before row r: not compared
            b = self.ins[r][q]; self.insdone[r] = q + 1
            m, s = self.give(b); self.out.append(b); self.tb = m[0x0B]; self.s = s
            self.snap()
            return alive(s)
        tt = rtick(r)
        b = self.button(r)
        if not tt:
            # the TAS's game logic did not run on row r (hit freeze, lag). Same here -> fine. Otherwise this logic frame
            # gets what the TAS's next logic frame got
            sid = e.msave()
            m, s = self.give(b)
            if m[0x0B] != self.tb:
                r2 = nxt_tick(r)
                if r2 - r > 3:
                    e.mfree(sid); self.out.append(b); self.tb = m[0x0B]; self.s = s; self.rn = r + 1; self.why = "freeze"; self.snap()
                    return False
                e.mload(sid); r = r2; b = self.button(r)
                m, s = self.give(b); self.gain += r2 - self.rn
            e.mfree(sid)
        else:
            m, s = self.give(b)
            if m[0x0B] == self.tb:                             # we dropped a frame the TAS did not (or froze)
                self.out.append(b); self.s = s; self.lagrun += 1; self.lags += 1
                self.snap()
                if self.lagrun <= 10: return True
                self.why = "stall"; return False
        self.lagrun = 0
        self.out.append(b); self.tb = m[0x0B]; self.s = s
        self.rn = r + 1
        self.why = compare(s, ref(r)[0])
        if self.why == "spawn" and SPAWN_LAG:                  # an enemy that comes in a frame or two off is let through
            self.spawnlag += 1
            if self.spawnlag <= SPAWN_LAG: self.why = None
        elif self.why is None:
            self.spawnlag = 0
        if self.why is None and not alive(s): self.why = "dead"
        self.snap()
        return self.why is None

    def play(self, to_r):
        """-> None when row to_r is reached on track, else the TAS row where the tracks part"""
        while self.rn < to_r:
            r = self.rn
            if not self.step():
                return r
        return None

    def k(self): return self.base_k + len(self.out)


def describe(F, r):
    s, t = F.s, ref(min(r, F.rn - 1) if F.rn > 0 else r)[0]
    eo = [(hex(d[0]), d[1], d[2], d[3]) for d in s["objs"] if d[0] in ENEMY]
    et = [(hex(d[0]), d[1], d[2], d[3]) for d in t["objs"] if d[0] in ENEMY]
    return (f"ours k={F.k()} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} hp={s['hp']} {eo} | "
            f"tas r={F.rn - 1} x={t['x']} H={t['H']} z={t['z']} an={t['an']} spd={t['spd']} {et}")


def repair(F, bad, why, log):
    """try edits; keep the one that holds longest. -> True when the tracks agree through bad+M"""
    base = (dict(F.repl), set(F.sel), dict(F.btn2), {k: list(v) for k, v in F.ins.items()}, set(F.skip))

    def restore():
        F.repl, F.sel, F.btn2, F.ins, F.skip = dict(base[0]), set(base[1]), dict(base[2]), {k: list(v) for k, v in base[3].items()}, set(base[4])

    def cands_toad():
        WT = WT0 if why != "spawn" else WSP
        for r in range(bad, bad - WT, -1):                    # (bad itself: the frame whose result differs)
            cur = norm("+".join(v for v in bt(F.button(r)) if v != "Select"))
            for b in TB:
                if b != cur:
                    yield ("repl", r, b)
            if "B" in bt(cur):                                 # an attack frame: keep the B, vary the rest
                for b in TB:
                    b2 = norm(b + "+B")
                    if b2 != cur: yield ("repl", r, b2)
            elif why in ("freeze", "enemy"):                   # ... or throw the attack a frame off
                for b in ("B", "Left+B", "Right+B"):
                    yield ("repl", r, b)
        for r in range(bad, bad - WT, -1):
            yield ("ins", r, "")
            yield ("ins", r, F.button(r))
            yield ("ins", r, F.button(r - 1))
            yield ("skip", r, None)
        for r in range(bad, bad - WT, -1):
            for b in TB:
                yield ("repl2", r, b)

    def cands_enemy():
        for r in range(bad - 1, bad - WS, -1):
            if r not in F.sel: yield ("sel", r, None)
        for r in range(bad - 1, bad - WS, -1):
            for b2 in ("Up", "Down"):
                if r not in F.btn2 and b2 not in F.button(r) and not ({"Up", "Down"} & set(bt(F.button(r)))): yield ("btn2", r, b2)
        for r in range(bad - 1, bad - WS, -3):
            for r2 in range(r - 1, max(bad - WS, r - 40), -2):
                if r not in F.sel and r2 not in F.sel: yield ("sel2", r, r2)

    def apply(c):
        kind, r, x = c
        if kind == "repl": F.repl[r] = x; return r
        if kind == "repl2": F.repl[r] = x; F.repl[r - 1] = x; return r - 1
        if kind == "ins": F.ins[r] = F.ins.get(r, []) + [x]; return r
        if kind == "insn": F.ins[r] = F.ins.get(r, []) + [""] * x; return r
        if kind == "skip": F.skip.add(r); return r
        if kind == "sel": F.sel.add(r); return r
        if kind == "btn2": F.btn2[r] = x; return r
        if kind == "sel2": F.sel.add(r); F.sel.add(x); return min(r, x)

    def cands_wait():
        """the enemy came in a few frames off (the camera that spawns it sits a few pixels off): stand a little longer
        somewhere before - where the TAS's toad stood on the ground. Even counts first (they keep the hit phase)."""
        for n in (2, 4, 1, 3, 6, 5, 8):
            for r in range(bad, bad - PW2, -1):
                if ref(r - 1)[0]["z"] == 0:
                    yield ("insn", r, n)

    def cands_parity():
        """one frame less or one more somewhere before: nearest first, a frame gained before a frame lost"""
        for r in range(bad, bad - PW, -1):
            yield ("skip", r, None)
        for r in range(bad, bad - PW, -1):
            yield ("ins", r, F.button(r))
            yield ("ins", r, "")
            yield ("ins", r, F.button(r - 1))

    order = [cands_toad, cands_enemy, cands_wait] if why != "enemy" else [cands_enemy, cands_wait, cands_toad]
    if why == "spawn":                                        # the enemy came in on another frame: the camera sits a pixel off
        order = [cands_toad, cands_wait]
    if why == "parity": order = [cands_parity]
    best = None; tried = 0; t0 = time.time()
    budget = float(os.environ.get("TW1_REPAIR_S", 240))
    for gen in order:
        for c in gen():
            if c[1] <= ref_floor[0]: continue
            tried += 1
            restore()
            r_first = apply(c)
            F.rewind_row(r_first)
            b2 = F.play(bad + M)
            if b2 is None:
                b3 = F.play(bad + LOOK)
                reach = (bad + LOOK) if b3 is None else b3
                cost = len(F.out)                              # frames used to get there (fewer = better at equal reach)
                if VERB: print(f"      cand {c} holds to {reach}", flush=True)
                if best is None or reach > best[0]:
                    best = (reach, c)
                if reach >= bad + LOOK:
                    F.rewind_row(r_first)
                    break
            F.rewind_row(r_first)                              # (drops the savestates made under this variant)
            if time.time() - t0 > budget and best: break
        if best: break
    restore()
    if best is None:
        F.rewind_row(bad - 1)
        F.play(bad)                                            # (the piece then ends right before the row that cannot be had)
        log(f"  row {bad} ({why}): NO repair in {tried} tries, {time.time() - t0:.0f}s")
        return False
    r_first = apply(best[1])
    F.rewind_row(r_first)
    log(f"  row {bad} ({why}): repaired by {best[1]} after {tried} tries ({time.time() - t0:.0f}s), holds to {best[0]}")
    return True


ref_floor = [0]


def main():
    start, r0, r1, outname = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    r0 = (load_piece(start)["rn"] - 1) if r0 == "-" else int(r0)       # '-' = continue a piece where it stopped
    A = seg("A12r")
    e = BizHawk(log_name=f"tw1_follow_{outname}.log")
    if start.startswith("K:"):
        k0 = int(start[2:]); b0 = (k0 // 250) * 250
        base, base_k = f"tw1_a_f{b0}", b0
        pre = A[b0:k0]
    else:
        p = load_piece(start); base, base_k, pre = p["base"], p["base_k"], p["inputs"]
    e.load(base); run(e, pre)
    F = Follower(e, base, base_k, pre, r0 + 1)
    ref_floor[0] = r0
    if os.environ.get("TW1_EDITS"):                            # edits found by an earlier run from the SAME start
        ed = load_piece(os.environ["TW1_EDITS"])["edits"]
        F.repl = {int(k): v for k, v in ed["repl"].items()}; F.sel = set(ed["sel"]); F.btn2 = {int(k): v for k, v in ed["btn2"].items()}
        F.ins = {int(k): list(v) for k, v in ed["ins"].items()}; F.skip = set(ed["skip"])
    logf = open(FIX / f"tw1_follow_{outname}.txt", "a")
    def log(t):
        print(t, flush=True); logf.write(t + "\n"); logf.flush()
    log(f"== follow {start} -> TAS rows {r0}..{r1}, out {outname}; start k={F.k()} {fmt(F.k(), '', F.s)[:90]}")
    t0 = time.time(); stuck = None
    while True:
        bad = F.play(r1)
        if bad is None: break
        why = F.why
        log(f"row {bad} ({why}): {describe(F, bad)}")
        if why == "dead" or not repair(F, bad, why, log):
            stuck = bad; break
    n_done = len(F.out)
    s = F.s
    log(f"{'STUCK at row ' + str(stuck) if stuck else 'DONE'}: k={F.k()} rn={F.rn} delay(k-rn)={F.k() - F.rn} x={s['x']} H={s['H']} z={s['z']} cam={s['cam']} t={s['t']} hp={s['hp']} lives={s['lives']} "
        f"edits: repl {len(F.repl)} sel {len(F.sel)} btn2 {len(F.btn2)} ins {sum(len(v) for v in F.ins.values())} skip {len(F.skip)} lags {F.lags}; {time.time() - t0:.0f}s")
    if os.environ.get("TW1_TRACE"):                           # per-frame ours / TAS listing of the last TW1_TRACE rows
        nrows = int(os.environ["TW1_TRACE"]); stop_rn = F.rn
        F.rewind_row(max(r0 + 1, stop_rn - nrows))
        with open(FIX / f"tw1_trace_{outname}.txt", "w") as tf:
            while F.rn < stop_rn:
                r = F.rn; F.step(); s = F.s; t = ref(F.rn - 1)[0]
                tf.write(f"k={F.k()} r={F.rn - 1} {F.out[-1]:12s} ours x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} cam={s['cam']} t={s['t']} |"
                         + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in s["objs"] if d[0] in ENEMY + (0x36,))
                         + f" || tas x={t['x']} H={t['H']} z={t['z']} an={t['an']} spd={t['spd']} cam={t['cam']} t={t['t']} |"
                         + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in t["objs"] if d[0] in ENEMY + (0x36,)) + f" why={F.why}" + chr(10))
    inputs = [norm(b) for b in F.out]
    assert not any(banned(b) for b in inputs)
    save_piece(outname, base, base_k, inputs, rn=F.rn, stuck=stuck,
               edits=dict(repl={str(k): v for k, v in F.repl.items()}, sel=sorted(F.sel), btn2={str(k): v for k, v in F.btn2.items()},
                          ins={str(k): v for k, v in F.ins.items()}, skip=sorted(F.skip)))
    e.save(f"tw1_{outname}_end")
    e.close()
    return stuck is None


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

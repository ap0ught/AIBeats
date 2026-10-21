"""Chain A: build Level 8 segment A8 = L8c[0:3113] + arrival + fight + death wait + A,B mash to the Terra Tubes placement.

    python u16a_build8.py <out segment name> <fight json> [arrival json]
        fight json   = {inputs: [...]} from control after the arrival cutscene (early_l8fight / u16a_l8fight format;
                       its own 'arrival_prefix' is used when no arrival json is given)
    -> logs/pbeam_<out>.json (bookmark L6c_end0), states/<out>_end0b.State (bookmark replay; the replay-exact one is made
       by u16a_mkentry.py), logs/fix/u16a_build8_<out>.txt

Steps: (1) reference = L8c replayed from L6c_end0: where does the placement detector fire, what is the end state;
(2) the new line to the kill; (3) scan of the mash: start offset after the kill x who presses first (A or B), each
played to the placement; the earliest placement wins (ties: the latest mash start = fewest presses);
(4) the chosen line replayed once more in one piece from the bookmark, compared with L8c's end state.
"""
import json
import sys

from u16a_lib import *

out = sys.argv[1]
fj = json.load(open(sys.argv[2]))
aj = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
arrival = list(aj["inputs"]) if aj else list(fj.get("arrival_prefix", []))
fight = list(fj["inputs"])
CUT = 3113
logf = open(FIX / f"u16a_build8_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


old = seg("L8c")
e = BizHawk(log_name=f"u16a_build8_{out}.log")


class Det:
    """the placement detector of early_l8verify.py: level 11, then toad hp 0 and x 0, then hp > 0 and x > 0"""

    def __init__(self):
        self.stage, self.left, self.kill, self.prev_sc, self.minhp = 0, None, None, None, 99

    def feed(self, m, n):
        t = toad(m)
        if t["level"] == 7:
            self.minhp = min(self.minhp, t["hp"])
            if self.prev_sc is not None and t["score"] - self.prev_sc >= 10000 and self.kill is None:
                self.kill = n
            self.prev_sc = t["score"]
        if self.left is None and t["level"] in (254, 255):
            self.left = n
        if self.stage == 0 and t["level"] == 11:
            self.stage = 1
        if self.stage == 1 and t["hp"] == 0 and t["x"] == 0:
            self.stage = 2
        if self.stage == 2 and t["hp"] > 0 and t["x"] > 0:
            self.stage = 3
            return True
        return False


# ---- 1. the reference
e.load("L6c_end0")
d = Det()
placed_ref = None
for n, b in enumerate(old, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if d.feed(m, n) and placed_ref is None:
        placed_ref = n
m_ref = bytes(e.ram(0, 0x800))
log(f"reference L8c: {len(old)} inputs; detector: kill {d.kill}, level byte left 7 at {d.left}, placement at {placed_ref}; min hp {d.minhp}; end {toad(m_ref)}")
assert placed_ref == len(old), "the detector does not fire on L8c's last frame"

# ---- 2. the new line to the kill
e.load("L6c_end0")
pre = old[:CUT] + arrival + fight
d = Det()
for n, b in enumerate(pre, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    d.feed(m, n)
    if n == CUT + len(arrival):
        log(f"control after the arrival at input {n}: {toad(m)}")
assert d.kill is not None, "the fight does not kill"
log(f"new line: kill at input {d.kill} (L8c: 4394 by the same detector?), min hp {d.minhp}, state {toad(m)}")
kill = d.kill
base = e.msave()
base_det = (d.stage, d.left, d.kill, d.prev_sc, d.minhp)


TEND = (m_ref[0x0B], m_ref[0x0C])
KEYS = ("level", "x", "h", "depth", "z", "hp", "lives", "score")
T_REF = toad(m_ref)


def run(start, first, sel=()):
    """idle to `start` frames after the last fight input, then alternate (first, other) until the toad is placed (toad,
    health, lives, score as at L8c's end).  `sel` = frames of the tail that also carry Select (dice).
    -> (segment length, tail inputs, detector, 0)"""
    e.mload(base)
    dd = Det()
    dd.stage, dd.left, dd.kill, dd.prev_sc, dd.minhp = base_det
    tail = []
    pat = ("A", "B") if first == "A" else ("B", "A")
    for k in range(1200):
        b = "" if k < start else pat[(k - start) % 2]
        if k in sel:
            b = (b + "+Select").lstrip("+")
        e.step(bt(b), 1)
        tail.append(b)
        m = e.ram(0, 0x800)
        if dd.feed(m, len(pre) + k + 1):
            # the placement frame IS the old run's last frame: three frames later the level starts its clock ($0B := 0,
            # dice seeded) whatever $0B was on the black page (1 behind L8c's A mash, 0 behind an A,B mash) - u16a_p1.py
            t = toad(m)
            if all(t[q] == T_REF[q] for q in KEYS):
                return len(pre) + len(tail), tail, dd, 0
            return None, tail, dd, None
    return None, tail, dd, None


# ---- 3. the mash scan
res = []
first_try = run(300, "A")
log(f"mash from +300 (A first): segment ends at {first_try[0]} (placement + {first_try[3]} idle), level byte left 7 at {first_try[2].left}")
left = first_try[2].left - len(pre)                        # frames after the last fight input at which the level byte leaves 7
starts = sorted(set([0, 50, 100, 150, 200, 250, 300, 350] + list(range(max(0, left - 60), left + 12, 2))))
for st in starts:
    for first in ("A", "B"):
        p, tail, dd, w = run(st, first)
        res.append((p if p else 10 ** 9, -st, first, ()))
        log(f"  mash start +{st} {first} first: segment end {p} (idle {w}), level left {dd.left}, min hp {dd.minhp}")
res.sort()
log(f"mash scan: segment ends {sorted(set(r[0] for r in res))[:8]}; best {res[0]}")
# dice: one Select on one of the last frames before the level byte changes (and on the page), on top of the two best mash
# variants and the latest-start one.  Each variant is resumed from a savestate 64 frames before the level byte changes.
tops = [res[0], res[1], min(res, key=lambda r: (r[0] > res[0][0] + 1, r[1]))]
seen = set()
for p0, nst, first, _ in tops:
    if (nst, first) in seen or res[0][0] - (len(pre) + left) <= 44:   # 44 frames after the level byte changes = the fastest page seen
        continue
    seen.add((nst, first))
    for j in range(max(0, left - 64), left + 40):
        p, tail, dd, w = run(-nst, first, sel=(j,))
        res.append((p if p else 10 ** 9, nst, first, (j,)))
        if p and p < res[0][0]:
            log(f"  mash +{-nst} {first} first + Select on tail frame {j}: segment end {p}")
    res.sort()
    log(f"after the Select scan on (+{-nst}, {first}): ends {sorted(set(r[0] for r in res))[:8]}; best {res[0]}")
p, nst, first, selc = res[0]
log(f"best: segment end {p} with the mash from +{-nst}, {first} first, Select on {selc}")
_, tail, dd, w = run(-nst, first, sel=selc)
ins = pre + tail
e.mfree(base)

# ---- 4. one more replay in one piece
e.load("L6c_end0")
for b in ins:
    e.step(bt(b), 1)
m = bytes(e.ram(0, 0x800))
e.save(out + "_end0b")
t_new, t_ref = toad(m), toad(m_ref)
dif = diff(m, m_ref)
log(f"new end: {t_new}")
log(f"old end: {t_ref}")
log(f"RAM bytes that differ from L8c's end (stack excluded): {len(dif)}: {[hex(a) for a in dif][:60]}")
same_core = all(t_new[k] == t_ref[k] for k in ("level", "x", "h", "depth", "z", "hp", "lives", "score"))
lr, ud, st, sel = banned(ins)
log(f"{out}: {len(ins)} inputs (L8c {len(old)}: {len(old) - len(ins)} saved); toad/health/lives/score equal to L8c's end: {same_core}; "
    f"banned presses: Left+Right {lr}, Up+Down {ud}, Start {st}; frames with Select {sel}")
if same_core and lr == ud == st == 0:
    write_seg(out, {"bookmark": "L6c_end0", "inputs": ins, "slack": 0, "kill_at": kill,
                    "built_from": {"L8c": [0, CUT], "arrival": len(arrival), "fight": sys.argv[2], "fight_frames": len(fight),
                                   "mash_start_after_fight": -nst, "mash_first": first, "tail_select": list(selc), "idle_after_placement": w},
                    "note": "LEVEL 8: INTRUDER EXCLUDER. The climb as before; the last jump is steered right so the arrival cutscene hands control "
                            "back at x 183, next to Robo-Manus. Only the jump-smash keeps him in his corner: which attack B gives is a dice "
                            "roll, and a Select press on an earlier frame re-rolls it.||"
                            f"{len(ins)} frames (was {len(old)}); kill at {kill}; A and B on alternate frames skip the next page"})
    log(f"wrote pbeam_{out}.json")
else:
    log("NOT written")
e.close()

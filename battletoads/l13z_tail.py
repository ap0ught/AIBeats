"""The ending after the Dark Queen's last hit, optimised (2026-10-09, timing fix, track L13).

What the game does after the 21st hit (measured: l13z_tailstat.py, l13z_tail1..6.py; frames):
    kill -> her body (object 0x46) flies up, lands, bounces, drops through the floor ......... 154 (kill at h 44) .. 169 (h 153)
    her object is back (0x7E at x 128 under the floor), its counter $583+slot counts 207 -> 0 . 207
    she rises 1 px/frame to the tower's top (h 156) ........................................... 171
    she waits there, then the cut to her speech (level byte 13 -> 254) ........................ ~122
    the speech loads (8, 10 or 12 frames - depends on CPU timing) and is skipped with A ........ 9 / 11 / 13
    last scene at the tower, then the cut to PROFESSOR T. BIRD (level byte 13 -> 254 again) .... 356 .. 600 (!)
The last scene's length is NOT fixed. Her AI timer ($4ED+slot, with a state byte $4DE+slot) keeps running while she
rises: whenever it reaches 0 it is reloaded from the random numbers (33-96 for a 'wander' state, small values for a
'go to the hover height' state, 255 for the state after that). The value left when she reaches the top is frozen and
counts down again in the last scene, which ends when it reaches 0 after the captives have dropped in:
    scene = 182 + timer_at_top   for timer_at_top >= 174  (174 -> 356 frames, 255 -> 437)
    smaller values expire before the captives arrive, the timer reloads once more and the scene runs 438-600 frames
    (the published run: 491).
The random numbers depend on the buttons held (Select does nothing else), so Select presses during the rise re-roll every
reload: a search over them picks the reload chain that leaves a timer just above 174. Select presses while she waits at
the top re-roll the speech's loading time (9 is the shortest).
One hazard: a toad within ~30 px of x 128 is hit by the rising queen (+9 frames of hit-stop, or dead: +27). The toad
is walked to the nearer side first.

    best = optimise(e, kill_sid, kill_f, log)  ->  dict(inputs=[...], total=frames from the kill state to the T. Bird cut, ...)
"""
import random

import l13z_beam as zb

TOP_H = 156
RISE = 171                 # frames from the rise's first frame to the top
SCENE_MIN = 356
C_FROM = 143               # rise step from which a reload can start the 'go to the hover height' state (she is at h 128), followed by
                           # the 255 state: timer at the top 255 - (171 - 144) = 228 at best -> last scene 410 frames


def scene_len(e2_top):
    """the last scene's length when the timer does not expire early (exact for e2_top >= 174)"""
    return 182 + e2_top if e2_top >= 174 else None


def _step(e, b):
    return e.xp(None, [((b or "-"),)])[0][1]


def to_rise(e, sid, f0, log=print):
    """From the kill state: walk the toad to the nearer side, idle until the rise's first frame (her counter at 0, object under
    the floor). Returns (sid at the rise start, inputs, features there)."""
    e.mload(sid)
    side = "Right" if f0.tx >= 128 else "Left"
    ins = []
    f = f0
    hp = 99
    for _ in range(700):
        far = (f.tx >= 196) if side == "Right" else (f.tx <= 60)
        b = "" if far else side
        f = _step(e, b)
        ins.append(b)
        hp = min(hp, f.thp)
        if f.qid == zb.QUEEN and f.ctr == 0 and f.qh > 200:
            break
    else:
        return None, ins, f
    if hp < 47:
        log(f"    (toad health {hp} before the rise)")
    return e.msave(), ins, f


def predict(top):
    """predicted last-scene length for a timer value at the top (exact from 174 up; guesses below, checked by the play-out)"""
    if top >= 174:
        return 182 + top
    if top >= 114:
        return 365          # expires just before the captives land; seen 358-389 on a snapshot (depends on one more reload)
    return 440 + top


class _N:
    """a state during the rise at step f (frames since the rise start) with the timer showing e2"""
    __slots__ = ("sid", "f", "e1", "e2", "ins", "lb", "tries", "depth")

    def __init__(self, sid, f, e1, e2, ins, depth=0):
        self.sid, self.f, self.e1, self.e2, self.ins, self.tries, self.depth = sid, f, e1, e2, ins, 0, depth
        nxt = f + e2                                    # the step at which the timer runs out
        if nxt > RISE:                                  # not before the top: the value left there is known
            self.lb = predict(e2 - (RISE - f))
        elif nxt >= C_FROM:                             # high enough: the short state can follow, its timer wraps to 255
            self.lb = 267 + nxt
        else:                                           # one more wander state (32-96 frames) must end on step 143 or later:
            self.lb = 267 + max(nxt + 32, C_FROM) + 3 + 6 * depth   # a lottery; deeper tickets are no better than the root's

    @property
    def terminal(self):
        return self.f + self.e2 > RISE

    @property
    def top(self):
        return self.e2 - (RISE - self.f)


def rise_search(e, S0, fS0, rng, budget=1500, log=print, keep=4):
    """Best-first search over Select patterns during the rise. A node is expanded by playing its timer out with random
    Select presses and reading what the timer shows next: a reload (a new node), or 0 = the short state, whose timer wraps
    to 255 on the following frame (a terminal: the value at the top is then known). Returns the best terminals with a
    saved state at the top [(predicted scene length, node)] and the number of simulations."""
    global RISE, C_FROM, TOP_H
    # calibrate this rise: its length (171 or 172 steps, the top is h 156 or 157) and the step at which she passes h 128
    e.mload(S0)
    hs = [fS0.qh]
    for _ in range(190):
        hs.append(_step(e, "").qh)
    RISE = next(k for k in range(1, 186) if hs[k] == hs[k + 1] == hs[k + 2])
    TOP_H = hs[RISE]
    C_FROM = next((k for k in range(1, RISE + 1) if hs[k] == 128), 143)
    root = _N(S0, 0, fS0.qe1, fS0.qe2, [])
    terms = {}
    made = []
    sims = 0
    best = 9999
    open_ = []

    def add_term(c):
        nonlocal best
        tk = (c.e1, c.top)
        pr = predict(c.top)
        if tk in terms:
            return
        c.sid = e.msave(); made.append(c.sid)
        terms[tk] = (pr, c)
        if pr < best:
            best = pr
            log(f"    rise: timer {c.top} at the top (state {c.e1}), last change at step {c.f} -> scene ~{pr} ({sims} sims)")

    if root.terminal or root.e2 == 0:
        e.mload(S0)
        add_term(root)
    else:
        open_.append(root)
    dens = [0.08, 0.25, 0.5, 0.15]
    while open_ and sims < budget:
        open_.sort(key=lambda n: (n.lb + 4 * n.tries, -(n.f + n.e2)))
        n = open_[0]
        if n.lb >= best:
            break
        n.tries += 1
        K = 96 if n.f + n.e2 < C_FROM else 4
        seen = set()
        for i in range(K):
            e.mload(n.sid)
            p = dens[i % 4] if (i or n.tries > 1) else 0.0     # the first sample: no presses at all
            pat = []
            f = None
            for j in range(n.e2):
                b = "Select" if rng.random() < p else ""
                f = _step(e, b)
                pat.append(b)
            sims += 1
            key = (f.qe1, f.qe2)
            if key in seen:
                continue
            seen.add(key)
            step = n.f + n.e2
            if f.qe2 == 0:                               # the short state ran out: the timer wraps to 255 on the next frame
                if step + 1 > RISE:
                    continue
                f = _step(e, "")
                pat.append("")
                c = _N(None, step + 1, f.qe1, f.qe2, n.ins + pat, n.depth + 1)
                if f.qe2 == 255:
                    add_term(c)
                continue
            c = _N(None, step, f.qe1, f.qe2, n.ins + pat, n.depth + 1)
            if c.terminal:
                add_term(c)
            elif c.lb < best:
                c.sid = e.msave(); made.append(c.sid)
                open_.append(c)
        if n.tries >= 3:
            open_.remove(n)
    out = []
    for pr, c in sorted(terms.values(), key=lambda t: t[0])[:keep]:
        e.mload(c.sid)                                   # play the terminal out to the top and save the state there
        pat = []
        f = None
        for _ in range(RISE - c.f + 2):
            f = _step(e, "")
            pat.append("")
        if f.qh != TOP_H:
            continue
        m = _N(e.msave(), RISE + 2, f.qe1, f.qe2, c.ins + pat)
        out.append((predict(f.qe2), m))
    e.xfree([x for x in made if x != S0])
    return out, sims


def playout(e, sid, wait_pat):
    """From a state at the top: wait_pat inputs while she waits (then idle), A mash through the speech, idle to the T. Bird cut.
    -> (inputs, cut1 index, tower index, tbird index) counted from the state, or None"""
    e.mload(sid)
    ins = []
    phase, k = 0, 0
    ev = {}
    f = None
    while len(ins) < 1500:
        if phase == 0:
            b = wait_pat[len(ins)] if len(ins) < len(wait_pat) else ""
        elif phase == 1:
            b = "A" if k % 2 == 0 else ""
        else:
            b = ""
        f = _step(e, b)
        ins.append(b)
        k += 1
        if phase == 0 and f.lvl != 13:
            phase, k = 1, 0
            ev["cut1"] = len(ins)
        elif phase == 1 and f.lvl == 13:
            phase, k = 2, 0
            ev["tower"] = len(ins)
        elif phase == 2 and f.lvl == 254:
            ev["tbird"] = len(ins)
            return ins, ev
    return None


def optimise(e, kill_sid, kill_f, log=print, seed=1, budget=1500, tops=3, waits=12, quick=False):
    """Full tail from a kill state. Returns dict(inputs, total, body_gone, cut1, tower, tbird, scene, load, e2_top) or None."""
    rng = random.Random(seed)
    S0, ins0, fS0 = to_rise(e, kill_sid, kill_f, log)
    if S0 is None:
        return None
    n0 = len(ins0)                                        # kill state -> rise start (= body flight + 207)
    res, sims = rise_search(e, S0, fS0, rng, budget=budget, log=log)
    if not res:
        return None
    best = None
    for pred, node in res[:tops]:
        got9 = False
        for w in range(waits):
            p = 0.0 if w == 0 else rng.choice([0.05, 0.2, 0.5])
            wait_pat = ["Select" if rng.random() < p else "" for _ in range(110)]
            r = playout(e, node.sid, wait_pat)
            if r is None:
                continue
            ins2, ev = r
            total = n0 + len(node.ins) + ev["tbird"]
            scene = ev["tbird"] - ev["tower"]
            load = ev["tower"] - ev["cut1"]
            if best is None or total < best["total"]:
                best = dict(inputs=ins0 + node.ins + ins2, total=total, rise_start=n0, cut1=n0 + len(node.ins) + ev["cut1"],
                            tower=n0 + len(node.ins) + ev["tower"], tbird=total, scene=scene, load=load, e2_top=node.e2, e1_top=node.e1,
                            E0=fS0.qe2, e1_0=fS0.qe1, sims=sims)
            if load <= 9 and scene_len(node.e2) is not None:
                break                                      # the scene is fixed for this top state and the load is minimal
            if quick and w >= 1:
                break
    e.xfree([S0] + [n.sid for _, n in res])
    return best

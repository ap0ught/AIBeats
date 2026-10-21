"""Beam search on the exact boss model (base_bsim.Sim): finds the input sequence for a base boss fight offline.

A node is a model state plus the press history of the five buttons the fight uses (Left, Right, Up, A, B), so every
sequence the search produces already obeys the input rules (new press of a button at most once per 5 frames, held
at least 2 frames, released at least 2 frames). Nodes are ranked inside a layer (= one frame) by

    HP still to remove after the bullets already in the air have landed (exact: a rollout of the model without
    further input)  +  alpha x (frames the ten bullet slots stay busy)  +  a term for HP that is far from Bill

and the layer keeps the best few of every bucket (Bill's x, airborne phase, which parts have been damaged), so that
positions and orders that have not paid yet are not pruned away by lines that fired early.
"""
from __future__ import annotations

import time

from . import base_bsim as bs

BTN = ("Left", "Right", "Up", "A", "B")
IL, IR, IU, IA, IB = range(5)
PERIOD, HOLD, RELEASE = 5, 2, 2
ROW_ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


def _btn_tables():
    """Per-button press-history state (hold length 0/1/2+, frames since the press started capped at PERIOD, frames
    released capped at RELEASE) -> [state if not held, state if held] (-1 = not allowed)."""
    states = [(h, p, r) for h in (0, 1, 2) for p in range(PERIOD + 1) for r in range(RELEASE + 1)]
    idx = {s: i for i, s in enumerate(states)}
    nxt = []
    for (h, p, r) in states:
        p1 = min(PERIOD, p + 1)
        if h == 0:
            up = idx[(0, p1, min(RELEASE, r + 1))]
            dn = idx[(1, 1, 0)] if (p >= PERIOD and r >= RELEASE) else -1
        elif h == 1:
            up = -1
            dn = idx[(2, p1, 0)]
        else:
            up = idx[(0, p1, 1)]
            dn = idx[(2, p1, 0)]
        nxt.append((up, dn))
    return states, idx, nxt


PSTATES, PIDX, PNEXT = _btn_tables()
P_FREE = PIDX[(0, PERIOD, RELEASE)]
P_HELD = [1 if s[0] else 0 for s in PSTATES]
P_MUST = [1 if s[0] == 1 else 0 for s in PSTATES]
P_CAN = [1 if PNEXT[i][1] >= 0 and not s[0] else 0 for i, s in enumerate(PSTATES)]


def pad_from_rows(rows):
    """Press-history state of (Left, Right, Up, A, B) after the given rows (only the last 12 matter)."""
    pad = [P_FREE] * 5
    for r in list(rows)[-12:]:
        for k, b in enumerate(BTN):
            n = PNEXT[pad[k]][1 if b in r else 0]
            if n < 0:           # history that breaks the rules: fall back to the nearest legal state
                n = PIDX[(2, PERIOD, 0)] if b in r else PIDX[(0, 0, 1)]
            pad[k] = n
    return tuple(pad)


def act_of_row(row):
    return sum(1 << k for k, b in enumerate(BTN) if b in row)


def act_row(act):
    """Held mask over BTN -> button tuple in the harness order."""
    held = [BTN[k] for k in range(5) if act >> k & 1]
    return tuple(b for b in ROW_ORDER if b in held)


def sim_inputs(pad, act):
    """(d-pad nibble, new A press, new B press, next pad) for a held mask on top of a press history."""
    np_ = (PNEXT[pad[0]][act & 1], PNEXT[pad[1]][act >> 1 & 1], PNEXT[pad[2]][act >> 2 & 1],
           PNEXT[pad[3]][act >> 3 & 1], PNEXT[pad[4]][act >> 4 & 1])
    a_new = 1 if (act & 8) and not P_HELD[pad[3]] else 0
    b_new = 1 if (act & 16) and not P_HELD[pad[4]] else 0
    dpad = (2 if act & 1 else 0) | (1 if act & 2 else 0) | (8 if act & 4 else 0)
    return dpad, a_new, b_new, np_


class Node:
    __slots__ = ("sim", "pad", "act", "prev", "rem", "busy", "jf", "score", "aux")

    def __init__(self, sim, pad, act, prev, rem, busy, jf):
        self.sim, self.pad, self.act, self.prev, self.rem, self.busy, self.jf = sim, pad, act, prev, rem, busy, jf
        self.aux = None
        self.score = 0.0

    def acts(self):
        out = []
        n = self
        while n.prev is not None:
            out.append(n.act)
            n = n.prev
        out.reverse()
        return out

    def rows(self):
        return [act_row(a) for a in self.acts()]


def rollout(sim, rem_fn, horizon=70, more=None, probe_t=None):
    """Let the bullets in the air land (and go on while more(model) is true, e.g. until a part's window has closed).
    Returns (remaining HP by rem_fn, slot-frames still busy, the rolled model, free slots at model frame probe_t or
    None when that frame is already past)."""
    if isinstance(probe_t, tuple):
        return _rollout_multi(sim, rem_fn, horizon, more, probe_t)
    s = sim.copy()
    busy = 0
    br = s.br
    n = 0
    probe = br.count(0) if probe_t is not None and s.t == probe_t else None
    while n < horizon and s.nlive:
        s.step(0, 0, 0)
        n += 1
        busy += 10 - br.count(0)
        if s.t == probe_t:
            probe = br.count(0)
    busy += sum(s.bt[i] for i in range(10) if br[i] == 2) + 30 * s.nlive
    if more is not None:
        while n < 2 * horizon and more(s):
            s.step(0, 0, 0)
            n += 1
            if s.t == probe_t:
                probe = br.count(0)
    if probe is None and probe_t is not None and s.t < probe_t:
        probe = 10 - sum(1 for i in range(10) if br[i] == 2 and s.t + s.bt[i] > probe_t)
    return rem_fn(s), busy, s, probe


def _rollout_multi(sim, rem_fn, horizon, more, probe_ts):
    """rollout() with several probe frames (third pass, the Eye): the fourth value is a tuple, free slots at each of
    the frames if nothing more is pressed (9 = that frame is already past)."""
    s = sim.copy()
    busy = 0
    br = s.br
    n = 0
    t0 = s.t
    seen = {}
    if t0 in probe_ts:
        seen[t0] = br.count(0)
    last = max(probe_ts)
    while n < horizon and (s.nlive or (2 in br and s.t < last)):
        s.step(0, 0, 0)
        n += 1
        busy += 10 - br.count(0)
        if s.t in probe_ts:
            seen[s.t] = br.count(0)
    busy += sum(s.bt[i] for i in range(10) if br[i] == 2) + 30 * s.nlive
    if more is not None:
        while n < 2 * horizon and more(s):
            s.step(0, 0, 0)
            n += 1
            if s.t in probe_ts:
                seen[s.t] = br.count(0)
    out = []
    for pt in probe_ts:
        if pt in seen:
            out.append(seen[pt])
        elif pt < t0:
            out.append(9)
        else:
            out.append(10 - s.nlive - sum(1 for i in range(10) if br[i] == 2 and s.t + s.bt[i] > pt))
    return rem_fn(s), busy, s, tuple(out)


class Planner:
    """rem_fn(sim) -> HP still to remove (called on a rolled-out model); goal_fn(sim) -> reached;
    vec_fn(sim) -> per-part HP vector (kept in the node); sig_fn(vector) -> extra bucket key (keeps lines that
    damaged different parts apart); far_fn(px, vector) -> extra cost for HP that is far from where Bill is."""

    def __init__(self, rem_fn, goal_fn, alpha=0.03, k_bucket=4, width=8000, xb=4, jb=3, allow_fire=None,
                 prune_fn=None, tie_fn=None, verbose=False, hz_margin=1, allow_jump=None, vec_fn=None, sig_fn=None,
                 far_fn=None, roll_horizon=70, no_move=False, horizontal_shots=False, repeat=(), deadline=None,
                 diagonal_shots=True, roll_more=None, allow_move=None, cost_fn=None, probe_t=None):
        self.rem_fn, self.goal_fn, self.alpha = rem_fn, goal_fn, alpha
        self.k_bucket, self.width, self.xb, self.jb = k_bucket, width, xb, jb
        self.allow_fire = allow_fire        # f(sim) -> may a new B press start on the next frame?
        self.allow_jump = allow_jump
        self.prune_fn = prune_fn            # f(sim) -> True to drop the node
        self.tie_fn = tie_fn                # f(node) -> secondary key among goal nodes of one frame (smaller = better)
        self.vec_fn, self.sig_fn, self.far_fn = vec_fn, sig_fn, far_fn
        self.verbose = verbose
        self.hz_margin = hz_margin
        self.roll_horizon = roll_horizon
        self.roll_more = roll_more
        self.probe_t = probe_t              # vec_fn then gets (rolled model, free slots at that frame)
        self.cost_fn = cost_fn              # f(goal node) -> frames its end state will cost afterwards
        self.allow_move = allow_move        # f(sim) -> may Left/Right be pressed on the next frame?
        self.no_move = no_move
        self.horizontal_shots = horizontal_shots
        self.diagonal_shots = diagonal_shots
        self.shot_fn = None                 # optional f(sim) -> (horizontal, diagonal) overriding the two flags
        # layer indices (0 = the first planned frame) on which the game will see the previous frame's pad again
        # (controller read lost to the DMC conflict): the held buttons must not change on those frames
        self.repeat = set(repeat)
        self.deadline = deadline            # wall-clock limit in seconds (the best line so far is not returned: no goal)
        self.stats = {}

    def actions(self, sim, pad):
        """Legal, useful held-button masks for the next frame."""
        pl, pr, pu, pa, pb = pad
        hs = []
        if P_MUST[pl] and not self.no_move:
            hs.append(1)
        elif P_MUST[pr] and not self.no_move:
            hs.append(2)
        elif self.no_move or (self.allow_move is not None and not self.allow_move(sim)):
            hs.append(0)
        elif P_MUST[pl]:
            hs.append(1)
        elif P_MUST[pr]:
            hs.append(2)
        else:
            hs.append(0)
            if P_HELD[pl] or P_CAN[pl]:
                hs.append(1)
            if P_HELD[pr] or P_CAN[pr]:
                hs.append(2)
        if P_MUST[pb]:
            bs_ = (16,)
            bnew = False
        elif P_CAN[pb] and (self.allow_fire is None or self.allow_fire(sim)):
            bs_ = (0, 16)
            bnew = True
        else:
            bs_ = (0,)
            bnew = False
        if P_MUST[pa]:
            as_ = (8,)
        elif P_CAN[pa] and not sim.jump and (self.allow_jump is None or self.allow_jump(sim)):
            as_ = (0, 8)
        else:
            as_ = (0,)
        out = []
        mu = P_MUST[pu]
        cu = P_CAN[pu]
        hz = self.horizontal_shots
        dg = self.diagonal_shots
        if self.shot_fn is not None:
            hz, dg = self.shot_fn(sim)          # (horizontal, diagonal) shots allowed on the next frame
        for h in hs:
            for b in bs_:
                for a in as_:
                    if mu:
                        out.append(h | 4 | a | b)
                    elif b and bnew and h:
                        if not dg and not hz:
                            continue                       # fire straight up only: no d-pad on the press frame
                        if cu and dg:
                            out.append(h | 4 | a | b)      # diagonal shot
                        if hz or not cu:
                            out.append(h | a | b)          # horizontal shot
                    else:
                        out.append(h | a | b)
        return out

    def run(self, sim0, pad0, t_max, extra_layers=0, prev_act=0):
        """Returns the goal nodes found on the first layer that has any (plus `extra_layers` more layers), best first.
        prev_act = held mask of the frame before the first planned one (needed for a `repeat` on layer 0)."""
        bs.HZ_MARGIN = self.hz_margin
        t0 = time.time()
        rem_fn, goal_fn = self.rem_fn, self.goal_fn
        vec_fn, sig_fn, far_fn = self.vec_fn, self.sig_fn, self.far_fn
        probe_t = self.probe_t
        rem, busy, rs, pr = rollout(sim0, rem_fn, self.roll_horizon, self.roll_more, probe_t)
        root = Node(sim0.copy(), tuple(pad0), prev_act, None, rem, busy, 0)
        root.aux = (vec_fn(rs, pr) if probe_t is not None else vec_fn(rs)) if vec_fn else None
        layer = [root]
        goals = []
        first_goal = None
        nexp = nroll = 0
        alpha = self.alpha
        depth = 0
        for depth in range(t_max):
            buckets = {}
            seen = set()
            rep = depth in self.repeat
            for nd in layer:
                sim, pad = nd.sim, nd.pad
                rcache = {}
                if rep:
                    acts = [nd.act] if all(PNEXT[pad[k]][nd.act >> k & 1] >= 0 for k in range(5)) else []
                else:
                    acts = self.actions(sim, pad)
                for act in acts:
                    dpad, a_new, b_new, np_ = sim_inputs(pad, act)
                    s = sim.copy()
                    s.step(dpad, a_new, b_new)
                    nexp += 1
                    if s.dead or (self.prune_fn is not None and self.prune_fn(s)):
                        continue
                    key = (s.px, s.py, s.pvy, s.pdir, tuple(s.br), tuple(s.bx), tuple(s.by), s.hits, np_)
                    if key in seen:
                        continue
                    seen.add(key)
                    jf = nd.jf + 1 if s.jump else 0
                    goal = goal_fn(s)
                    if b_new and s.shots != sim.shots:
                        rc = rcache.get(dpad)
                        if rc is None:
                            rem, busy, rs, pr = rollout(s, rem_fn, self.roll_horizon, self.roll_more, probe_t)
                            nroll += 1
                            rc = rcache[dpad] = (rem, busy, (vec_fn(rs, pr) if probe_t is not None else vec_fn(rs))
                                                 if vec_fn else None)
                        rem, busy, aux = rc
                        if rem >= nd.rem and not goal:
                            continue                    # a press that removes nothing: never better than not pressing
                    else:
                        rem, busy, aux = nd.rem, nd.busy - (10 - sim.br.count(0)), nd.aux
                        if busy < 0:
                            busy = 0
                    c = Node(s, np_, act, nd, rem, busy, jf)
                    c.aux = aux
                    if goal:
                        goals.append(c)
                        continue
                    c.score = rem + alpha * busy + (far_fn(s.px, aux) if far_fn else 0.0)
                    bk = (s.px // self.xb, 0 if not s.jump else 1 + jf // self.jb, s.pdir,
                          sig_fn(aux) if sig_fn else 0)
                    lst = buckets.get(bk)
                    if lst is None:
                        buckets[bk] = [c]
                    else:
                        lst.append(c)
            if goals and first_goal is None:
                first_goal = depth
            if first_goal is not None and depth >= first_goal + extra_layers:
                break
            nxt = []
            kb = self.k_bucket
            for lst in buckets.values():
                if len(lst) > kb:
                    # best first, but one node of every exact (x, airborne frame) in the bucket before any second
                    # one: otherwise ties keep copies of one position and the others never spread out
                    lst.sort(key=lambda n: n.score)
                    picked, rest, sub = [], [], set()
                    for n in lst:
                        sk = (n.sim.px, n.jf)
                        if sk in sub:
                            rest.append(n)
                        else:
                            sub.add(sk)
                            picked.append(n)
                    lst[:] = (picked + rest)[:kb]
                nxt.extend(lst)
            if len(nxt) > self.width:
                # too many: the best of every bucket first, then fill up by score
                firsts = [lst[0] for lst in buckets.values()]
                if len(firsts) >= self.width:
                    firsts.sort(key=lambda n: n.score)
                    nxt = firsts[:self.width]
                else:
                    rest = [n for lst in buckets.values() for n in lst[1:]]
                    rest.sort(key=lambda n: n.score)
                    nxt = firsts + rest[:self.width - len(firsts)]
            layer = nxt
            if self.verbose and depth % 20 == 0:
                b = min(layer, key=lambda n: n.score) if layer else None
                print(f"  layer {depth} t{b.sim.t if b else '-'} nodes {len(layer)} buckets {len(buckets)} best "
                      f"{b.score if b else 0:.2f} rem {b.rem if b else None} exp {nexp} roll {nroll} {time.time() - t0:.0f}s", flush=True)
            if not layer:
                break
            if self.deadline and time.time() - t0 > self.deadline:
                break
        self.stats = {"expanded": nexp, "rollouts": nroll, "secs": round(time.time() - t0, 1), "layers": depth + 1}
        if self.cost_fn:
            goals.sort(key=lambda n: (n.sim.t + self.cost_fn(n), n.sim.t))
        elif self.tie_fn:
            goals.sort(key=lambda n: (n.sim.t, self.tie_fn(n)))
        else:
            goals.sort(key=lambda n: n.sim.t)
        return goals


def play(sim, pad, acts):
    """Step a copy of the model through held masks; returns (model, pad)."""
    s = sim.copy()
    pad = tuple(pad)
    for a in acts:
        dpad, a_new, b_new, pad = sim_inputs(pad, a)
        s.step(dpad, a_new, b_new)
    return s, pad

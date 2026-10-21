"""Stage 2 boss, the Eye: a dedicated plan for the 64-frame wait and the first jump (third pass, 2026-10-12).

Why: at the top of a jump (air frames 20-38) a press of THREE pellets from straight below puts all three into the
Eye, a full spray wastes two for 37 frames, and anywhere else only the centre pellet hits. So the fight is decided
by how many slots are free on the frames of the first jump's presses, and that is prepared during the wait: sprays
fired then fly through the shut Eye and free their slots 22-57 frames later, pellet by pellet ("blockers"). The
generic beam (base_bplan) never finds this (nothing has hit yet, so nothing ranks the lines); here it is searched
directly on the exact model (base_bsim, about 90,000 frames a second):

  stage 1  Bill walks to a lane under the Eye and stands; up to two blocker sprays (straight up when he stands,
           horizontal or diagonal in the walking direction when he walks); A at t_A. Every (lane, t_A, blockers) is
           played to the jump, ranked by a count of what its free slots allow in the jump, and the best are played
           through the jump with a narrow beam over the B presses (straight up) to 20 frames after the opening.
  stage 2  the best few states go to the generic planner for the rest (second jump, following the Eye).

plan(sim, pad, ...) returns the held-button masks (base_bplan order) from now to the boss-defeated flag, or None.
"""
from __future__ import annotations

import itertools
import time

from . import base_bplan as bp
from . import base_bsim as bs

E_R, E_D, E_V1 = bs.E_R, bs.E_D, bs.E_V1
L, R, U, A, B = 1, 2, 4, 8, 16          # held-mask bits (base_bplan.BTN = Left, Right, Up, A, B)


def eye_hp(s):
    for e in s.en:
        if e[0] == bs.T_EYE:
            return 0 if e[E_R] >= 5 else (16 if e[E_R] < 3 else e[E_V1] - (1 if e[E_R] == 4 else 0))
    return 0


def legal(pad, act):
    return all(bp.PNEXT[pad[k]][act >> k & 1] >= 0 for k in range(5))


def _step(s, pad, act):
    dpad, a_new, b_new, pad = bp.sim_inputs(pad, act)
    s.step(dpad, a_new, b_new)
    return pad


def run_script(sim0, pad0, lane, blockers, t_A, n_frames, prev_act=0, repeat=()):
    """Walk to the lane, fire the blockers [(frame, aim)] (frame 1 = the first planned frame), press A on frame t_A.
    aim: 'U' straight up (standing), 'H' horizontal / 'D' diagonal in the walking direction. Returns (sim, pad,
    acts) after n_frames frames, or None if a row is illegal or Bill is hit. repeat = frames (1-based) on which the
    pad is known not to be read: the buttons may not change there."""
    s = sim0.copy()
    pad = tuple(pad0)
    acts = []
    blk = dict(blockers)
    hold_b = hold_u = hold_a = 0
    last = prev_act
    for i in range(1, n_frames + 1):
        act = 0
        d = lane - s.px
        pl, pr = pad[0], pad[1]
        if not s.jump and i < t_A:
            if bp.P_MUST[pl]:
                act |= L
            elif bp.P_MUST[pr]:
                act |= R
            elif d <= -1 and (bp.P_HELD[pl] or (bp.P_CAN[pl] and d <= -2)):
                act |= L
            elif d >= 1 and (bp.P_HELD[pr] or (bp.P_CAN[pr] and d >= 2)):
                act |= R
        aim = blk.get(i)
        if aim is not None:
            if (aim == "U") == bool(act & (L | R)):
                return None
            hold_b = 2
            if aim == "D":
                hold_u = 2
        if hold_b:
            act |= B
            hold_b -= 1
        if hold_u:
            act |= U
            hold_u -= 1
        if i == t_A:
            hold_a = 2
        if hold_a:
            act |= A
            hold_a -= 1
        if ((i - 1) in repeat and act != last) or not legal(pad, act):
            return None
        pad = _step(s, pad, act)
        acts.append(act)
        last = act
        if s.dead:
            return None
    return s, pad, acts


def usable_from(sim, horizon=70):
    """Sorted frames (model time) from which each of the ten slots can take a new press if nothing more is fired."""
    s = sim.copy()
    out = [s.t + 1 if s.br[i] == 0 else None for i in range(10)]
    for _ in range(horizon):
        if None not in out:
            break
        s.step(0, 0, 0)
        for i in range(10):
            if out[i] is None and s.br[i] == 0:
                out[i] = s.t + 1
    return sorted(x if x is not None else 10 ** 6 for x in out)


def window_yield(U, t_jump, t_open):
    """Rough count of the hits the first jump can make with slots that become usable at the frames U (model time):
    presses every 5 frames from some first frame; a press on air frames 20-38 scores up to 3, another one 1, and
    only if its pellets arrive after the Eye has opened (about 15 frames of flight). Returns (hits, -wasted)."""
    best = (0, 0)
    for p1 in range(t_jump + 12, t_jump + 32):
        u = list(U)
        hits = waste = 0
        p = p1
        n = 0
        while p <= t_jump + 44 and n < 7:
            k = 0
            for x in u:
                if x <= p:
                    k += 1
            if k == 0:
                p += 1
                continue
            k = min(5, k)
            af = p - t_jump
            if p + 15 >= t_open:
                h = min(3, k) if 20 <= af <= 38 else 1
                hits += h
                waste += k - h
            del u[:k]                   # U is sorted: the usable ones are the first
            p += 5
            n += 1
        if (hits, -waste) > best:
            best = (hits, -waste)
    return best


def air_beam(s0, pad0, n_frames, width=12, first=1, repeat=(), prev_act=0):
    """Narrow beam over B presses only (no d-pad: straight up) for n_frames frames; value = Eye HP after the
    bullets in the air have landed, then the free slots. Returns [(hp, sim, pad, acts)], best first."""
    layer = [(s0, pad0, [], None, prev_act)]
    for i in range(n_frames):
        frame = first + i
        nxt = []
        seen = set()
        for s, pad, acts, val, last in layer:
            for act in (0, B):
                if (act == 0 and bp.P_MUST[pad[4]]) or not legal(pad, act) or ((frame - 1) in repeat and act != last):
                    continue
                s2 = s.copy()
                sh = s2.shots
                p2 = _step(s2, pad, act)
                if s2.dead:
                    continue
                key = (tuple(s2.br), tuple(s2.bx), tuple(s2.by), s2.hits, p2[4])
                if key in seen:
                    continue
                seen.add(key)
                if s2.shots != sh or val is None:
                    r = s2.copy()
                    for _ in range(45):
                        if not r.nlive:
                            break
                        r.step(0, 0, 0)
                    v = (eye_hp(r), -r.br.count(0))
                else:
                    v = val
                nxt.append((s2, p2, acts + [act], v, act))
        nxt.sort(key=lambda x: x[3])
        layer = nxt[:width]
        if not layer:
            return []
    out = [(eye_hp(s), s, pad, acts) for s, pad, acts, v, _ in layer]
    out.sort(key=lambda x: (x[0], -x[1].br.count(0)))
    return out


def stage1(sim0, pad0, prev_act=0, repeat=(), lanes=(128, 126, 130), n_exact=48, n_keep=6, verbose=False,
           hz_margin=2, after=20):
    """Returns [(hp at opening + `after`, free slots, lane, t_A, blockers, acts, sim, pad)] best first (acts covers
    the frames from now to opening + after)."""
    bs.HZ_MARGIN = hz_margin
    eye = next(e for e in sim0.en if e[0] == bs.T_EYE)
    if eye[E_R] != 2:
        return []
    D = eye[E_D]                       # the Eye can be hit on planned frame D
    t0 = time.time()
    cands = []
    n_scripts = 0
    for lane in lanes:
        # the walk alone tells when Bill stands on the lane
        for t_A in range(max(2, D - 41), D - 33):
            times = range(1, t_A - 1)
            sets = [()]
            sets += [((a, aim),) for a in times for aim in "UHD"]
            sets += [((a, aa), (b, ab)) for a, b in itertools.combinations(times, 2) if b - a >= 5
                     for aa in "UHD" for ab in "UHD"]
            for blk in sets:
                out = run_script(sim0, pad0, lane, blk, t_A, t_A, prev_act, repeat)
                if out is None:
                    continue
                s, pad, acts = out
                if s.px != lane and abs(s.px - lane) > 1:
                    continue
                n_scripts += 1
                y = window_yield(usable_from(s), s.t, sim0.t + D)
                cands.append((y, lane, t_A, blk))
    cands.sort(key=lambda c: (-c[0][0], -c[0][1], abs(c[1] - 128), c[2]))
    res = []
    for y, lane, t_A, blk in cands[:n_exact]:
        out = run_script(sim0, pad0, lane, blk, t_A, t_A + 1, prev_act, repeat)
        if out is None:
            continue
        s, pad, acts = out
        fin = air_beam(s, pad, D + after - (t_A + 1), first=t_A + 2, repeat=repeat, prev_act=acts[-1])
        if fin:
            hp, s2, p2, a2 = fin[0]
            res.append((hp, s2.br.count(0), lane, t_A, blk, acts + a2, s2, p2))
    res.sort(key=lambda r: (r[0], -r[1]))
    if verbose:
        print(f"   eye stage 1: {n_scripts} scripts, {len(cands)} ranked, {len(res)} played, {time.time() - t0:.0f} s; "
              f"best HP {[r[0] for r in res[:n_keep]]} at opening + {after}", flush=True)
    return res[:n_keep]

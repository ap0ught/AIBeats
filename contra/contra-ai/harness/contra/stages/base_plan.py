"""Abstract model of a base room and a planner for the press schedule ("hose" building).

Facts the model uses (all checked in the emulator, see knowledge/s2_notes.md):
* A Spread press creates min(5, free slots) pellets (centre, +4, -5, +9, -10 px at the wall), slots 0..9.
* A pellet can hit a wall-plane enemy only on its arrival frame = press frame + 20 (Rapid).
* A pellet that hits frees its slot for a press 27 frames after its own press; a miss frees it after 28.
* Enemies are processed from slot 15 down, each takes at most one pellet (the highest slot = highest pellet index).
* Centre pellet lands at floor(0.375 * px + 81) (standing, facing right; 2 less facing left); Y = 104 standing.
"""
from __future__ import annotations

FLIGHT, BUSY_HIT, BUSY_MISS, CAP = 20, 27, 28, 5
PELLET_DX = (0, 4, -5, 9, -10)
PXMIN, PXMAX = 48, 208
NPX = PXMAX - PXMIN + 1
FULL = (1 << NPX) - 1
# bullet collision boxes by collision code: (dy, dx, h, w) from collision_box_codes_04 (bank7.asm)
BOX = {0: (-18, -11, 36, 22), 1: (-4, -4, 8, 8), 2: (-11, -11, 22, 22), 3: (-17, -17, 34, 34), 4: (-32, -16, 8, 32),
       5: (-6, -6, 12, 12), 6: (-13, -6, 22, 12), 7: (-28, -28, 56, 56)}
STAND_Y, CROUCH_Y = 104, 116
SKIP_TYPES = (0x00, 0x01, 0x12, 0x19, 0x1A, 0x1B, 0x1D, 0x20)


def centre_x(px, facing_left=False):
    return (3 * px + 648) // 8 - (2 if facing_left else 0)


def in_box(bx, by, ex, ey, code):
    dy, dx, h, w = BOX[code]
    return 0 <= by - (ey + dy) - 1 < h and 0 <= bx - (ex + dx) - 1 < w


class Ent:
    """A thing a pellet can hit at the wall: kind 'core' (required), 'turret', 'soldier'."""

    def __init__(self, eid, kind, slot, first, code, etype):
        self.eid, self.kind, self.slot, self.first, self.code, self.etype = eid, kind, slot, first, code, etype
        self.hp0 = 0
        self.track = {}      # T -> (x, y, hittable)
        self.open = None     # first T it was hittable

    def __repr__(self):
        ts = sorted(self.track)
        x, y, _ = self.track[ts[0]]
        return f"<{self.kind}#{self.eid} slot{self.slot} t{self.etype:02x} hp{self.hp0} T{ts[0]}-{ts[-1]} open{self.open} at({x},{y}) code{self.code}>"


def entities_from_trace(tr):
    """tr[T] = State at room frame T (T = 0: the frame the room's enemies appear), recorded without hitting
    anything. Returns [Ent]."""
    ents, cur = [], {}
    for T, s in enumerate(tr):
        for i in range(16):
            r, t = s[f"er{i}"], s[f"et{i}"]
            if not r or t in SKIP_TYPES:
                cur.pop(i, None)
                continue
            e = cur.get(i)
            if e is None or e.etype != t:
                kind = {0x14: "core", 0x13: "turret", 0x11: "roller"}.get(t, "soldier")
                e = Ent(len(ents), kind, i, T, s[f"ec{i}"] & 15, t)
                e.attr = s[f"ea{i}"]
                cur[i] = e
                ents.append(e)
            hp, st = s[f"eh{i}"], s[f"es{i}"]
            hit = (st & 0x80) == 0 and 0 < hp < 0xF0 and (st & 0x20) == 0 and (s[f"ep{i}"] != 0 or t in (0x13, 0x14))
            if hit:
                e.code = s[f"ec{i}"] & 15
                if e.open is None:
                    e.open = T
                    e.hp0 = hp
            e.track[T] = (s[f"ex{i}"], s[f"ey{i}"], hit)
    return ents


class Plan:
    def __init__(self, presses, finish):
        self.presses = presses      # [(T, k, mask_px_right, mask_px_left, hits ((eid, pellet), ...), pose 0 stand / 1 crouch)]
        self.finish = finish        # T of the last required hit

    def __repr__(self):
        return f"Plan(finish={self.finish}, presses={[(p[0], str(p[1]) + {0: 's', 1: 'c', 2: 'a', 3: 'j', 9: 'J'}[p[5]], [h[0] for h in p[4]]) for p in self.presses]})"


def mask_range(a, b):
    a, b = max(a, PXMIN), min(b, PXMAX)
    if a > b:
        return 0
    return ((1 << (b - a + 1)) - 1) << (a - PXMIN)


def mask_list(m):
    return [PXMIN + i for i in range(NPX) if m >> i & 1]


def plan_room(ents, t_start, px_lo, px_hi, hp_over=None, t_max=420, beam=6000, ntop=8, verbose=False, pre=None,
              y_shot=STAND_Y, cd0=CAP, forbid=None, no_press=None, face0=0, not_before=None,
              air=None, plated=(), jump_y=None, danger=(), kill_by=None):
    """Frame-synchronous beam search over (cooldown, slot free times, entity HP, reachable px).

    t_start: first frame a standing press is possible; [px_lo, px_hi] reachable then (either facing).
    pre: free times of the 10 slots at t_start (default all free). cd0: frames since the last B press start.
    forbid: set of (T, eid) hits that the emulator refused (model errors found by the executor).
    Returns up to ntop Plans sorted by finish time (T of the last required core hit)."""
    hp_over = hp_over or {}
    forbid = forbid or set()
    no_press = no_press or set()
    not_before = not_before or {}
    air = air or {}          # T -> (px, arrival Y) for presses while airborne (before t_start)
    plated = set(plated)
    cores = [e.eid for e in ents if e.kind == "core"]
    hp0 = tuple(hp_over.get(e.eid, e.hp0 if e.kind in ("core", "turret") else (1 if e.kind == "soldier" else 0))
                for e in ents)
    by_slot = sorted((e for e in ents if e.kind in ("core", "turret", "soldier")), key=lambda e: -e.slot)
    ocache = {}

    def outcomes(ta, k, hps):
        live = tuple((e.eid, e.track[ta][0], e.track[ta][1],
                      (2 if hps[e.eid] > 8 else 5) if e.eid in plated else e.code) for e in by_slot
                     if hps[e.eid] > 0 and ta in e.track and e.track[ta][2] and (ta, e.eid) not in forbid
                     and ta >= not_before.get(e.eid, 0))
        key = (k, live)
        r = ocache.get(key)
        if r is not None:
            return r
        res = {}
        for pose, ys in ((0, STAND_Y), (1, CROUCH_Y)):
            if not any(in_box(ex, ys, ex, ey, code) for _, ex, ey, code in live) and pose == 1:
                continue        # a crouch shot that can hit nothing is never needed (standing miss is equivalent)
            for face in (0, 1):
                for px in range(PXMIN, PXMAX + 1):
                    c = centre_x(px, face or pose)
                    used = 0
                    hits = []
                    for eid, ex, ey, code in live:
                        for j in range(k - 1, -1, -1):
                            if not (used >> j & 1) and in_box(c + PELLET_DX[j], ys, ex, ey, code):
                                used |= 1 << j
                                hits.append((eid, j))
                                break
                    m = res.setdefault((pose, tuple(hits)), [0, 0])
                    m[face] |= 1 << (px - PXMIN)
        r = {hk: (m[0], m[1]) for hk, m in res.items()}
        ocache[key] = r
        return r

    def outcomes_jump(ta, k, hps, ya):
        live = tuple((e.eid, e.track[ta][0], e.track[ta][1],
                      (2 if hps[e.eid] > 8 else 5) if e.eid in plated else e.code) for e in by_slot
                     if hps[e.eid] > 0 and ta in e.track and e.track[ta][2] and (ta, e.eid) not in forbid
                     and ta >= not_before.get(e.eid, 0))
        key = (k, live, ya)
        r = ocache.get(key)
        if r is not None:
            return r
        res = {}
        for px in range(PXMIN, PXMAX + 1):
            c = (3 * px + 640) // 8
            used = 0
            hits = []
            for eid, ex, ey, code in live:
                for j in range(k - 1, -1, -1):
                    if not (used >> j & 1) and in_box(c + PELLET_DX[j], ya, ex, ey, code):
                        used |= 1 << j
                        hits.append((eid, j))
                        break
            m = res.setdefault(tuple(hits), [0])
            m[0] |= 1 << (px - PXMIN)
        r = {hk: m[0] for hk, m in res.items()}
        ocache[key] = r
        return r

    J = len(jump_y) if jump_y else 0

    def outcome_air(t, k, hps):
        px, ya = air[t]
        ta = t + FLIGHT
        c = (3 * px + 640) // 8
        used = 0
        hits = []
        for e in by_slot:
            if hps[e.eid] > 0 and ta in e.track and e.track[ta][2] and (ta, e.eid) not in forbid:
                code = (2 if hps[e.eid] > 8 else 5) if e.eid in plated else e.code
                for j in range(k - 1, -1, -1):
                    if not (used >> j & 1) and in_box(c + PELLET_DX[j], ya, e.track[ta][0], e.track[ta][1], code):
                        used |= 1 << j
                        hits.append((e.eid, j))
                        break
        return tuple(hits)

    start_slots = tuple(sorted(pre)) if pre else (0,) * 10
    R0 = mask_range(px_lo, px_hi)
    # reachable player positions as bit masks: I = standing still, A = moved one frame (must go on one more),
    # M = moving with the d-pad held >= 2 frames; index 0 facing right, 1 facing left
    states = {(cd0, start_slots, hp0, 0): ((0, R0, 0, 0, 0, 0) if face0 else (R0, 0, 0, 0, 0, 0), None)}
    best = []
    best_fin = t_max + 100

    def dilate(R):
        I0, I1, A0, A1, M0, M1 = R
        return (I0 | M0, I1 | M1, ((I0 | I1 | M1) << 1) & FULL, (I0 | I1 | M0) >> 1, ((A0 | M0) << 1) & FULL,
                (A1 | M1) >> 1)

    def pop(R):
        return bin(R[0] | R[1] | R[4] | R[5]).count("1")

    for t in range(min([t_start] + list(air)), t_max):
        if not states:
            break
        nxt = {}

        def put(key, R, back):
            o = nxt.get(key)
            if o is None or pop(o[0]) < pop(R):
                nxt[key] = (R, back)

        for (cd, slots, hps, jp), (R, back) in states.items():
            if t + FLIGHT >= best_fin:
                continue
            if kill_by and any(hps[eid] > 0 and t > tk for eid, tk in kill_by.items()):
                continue                    # a soldier that had to be shot by now (its bullets killed Bill) is alive
            ns = tuple(0 if f <= t else f for f in slots)
            njp = 0 if (jp == 0 or jp >= J) else jp + 1
            put((min(cd + 1, CAP), ns, hps, njp), dilate(R) if (cd >= 2 and t >= t_start and jp == 0) else R, back)
            nfree = ns.count(0)
            if J and jp == 0 and t >= t_start and cd >= 2 and (R[0] | R[1]):
                put((min(cd + 1, CAP), ns, hps, 1), (R[0], R[1], 0, 0, 0, 0), (t, 0, R[0], R[1], (), 9, back))
            if jp:
                if cd >= CAP and nfree and t not in no_press:
                    k = min(5, nfree)
                    ya = min(jump_y[jp - 1], 152) - 40
                    for hk, m in outcomes_jump(t + FLIGHT, k, hps, ya).items():
                        aR, aL = R[0] & m, R[1] & m
                        if not (aR or aL):
                            continue
                        h = len(hk)
                        nh = list(hps)
                        for eid, _ in hk:
                            nh[eid] -= 1
                        nh = tuple(nh)
                        nslots = tuple(sorted(ns[k:] + (t + BUSY_HIT,) * h + (t + BUSY_MISS,) * (k - h)))
                        nb = (t, k, aR, aL, hk, 3, back)
                        if all(nh[c] <= 0 for c in cores):
                            best.append((t + FLIGHT, nb))
                            best.sort(key=lambda x: x[0])
                            del best[ntop:]
                            if len(best) >= ntop:
                                best_fin = best[-1][0] + 1
                            continue
                        put((1, nslots, nh, njp), (aR, aL, 0, 0, 0, 0), nb)
                continue
            if t < t_start:
                if cd >= CAP and nfree and t in air and t not in no_press:
                    k = min(5, nfree)
                    hk = outcome_air(t, k, hps)
                    h = len(hk)
                    nh = list(hps)
                    for eid, _ in hk:
                        nh[eid] -= 1
                    nslots = tuple(sorted(ns[k:] + (t + BUSY_HIT,) * h + (t + BUSY_MISS,) * (k - h)))
                    put((1, nslots, tuple(nh), 0), R, (t, k, 0, 0, hk, 2, back))
                continue
            if cd >= CAP and nfree and t not in no_press:
                k = min(5, nfree)
                rest = ns[k:]
                RF, LF = R[0] | R[4], R[1] | R[5]
                bad = 0
                for (d0, d1, dm) in danger:      # places where standing up to shoot at this time was fatal
                    if d0 <= t <= d1:
                        bad |= dm
                for (pose, hk), (mR, mL) in outcomes(t + FLIGHT, k, hps).items():
                    aR, aL = RF & mR, LF & mL
                    if bad and pose == 0:
                        aR &= ~bad
                        aL &= ~bad
                    if not (aR or aL):
                        continue
                    h = len(hk)
                    nh = list(hps)
                    for eid, _ in hk:
                        nh[eid] -= 1
                    nh = tuple(nh)
                    nslots = tuple(sorted(rest + (t + BUSY_HIT,) * h + (t + BUSY_MISS,) * (k - h)))
                    nb = (t, k, aR, aL, hk, pose, back)
                    if all(nh[c] <= 0 for c in cores):
                        best.append((t + FLIGHT, nb))
                        best.sort(key=lambda x: x[0])
                        del best[ntop:]
                        if len(best) >= ntop:
                            best_fin = best[-1][0] + 1
                        continue
                    put((1, nslots, nh, 0), (aR, aL, 0, 0, 0, 0), nb)
        if len(nxt) > beam:
            def score(item):
                (cd, slots, hps, jp), _ = item
                rem = sum(hps[c] for c in cores)
                return (rem, -len(set(slots)), sum(hps) - rem, -cd)
            nxt = dict(sorted(nxt.items(), key=score)[:beam])
        states = nxt
        if verbose and t % 20 == 0:
            print("t", t, "states", len(states), "best", best[0][0] if best else None)
    plans = []
    for fin, back in best:
        pr = []
        b = back
        while b is not None:
            pr.append(b[:6])
            b = b[6]
        pr.reverse()
        plans.append(Plan(pr, fin))
    return plans

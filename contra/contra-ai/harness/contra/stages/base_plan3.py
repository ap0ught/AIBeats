"""Third-pass room planner for the two bases (2026-10-12). Same abstract model as base_plan (slots, flight, boxes),
with the things the first planner left out:

* Bill's position is free during the 50-frame hop (and the stage-start drop): a 2-frame tap of Left/Right makes him
  drift 1 px per frame until he lands (measured, tools/s4t_snip/a3.py), and the x he ENTERS the room with is a choice
  too (it is the x he left the previous room with; base_room3 walks there while the previous room clears).
* He keeps walking while B is pressed and held (measured: x changes on every frame of a walk whatever B does); only a
  crouch shot (Down + B, two frames) needs him to stand still.
* The d-pad rules (a direction is held >= 2 frames, released >= 2, pressed again >= 5 frames after its last press) are
  part of the movement model, so every plan has a legal walk; `walk_rows` returns it frame by frame.
* Several incomparable position sets are kept per (cooldown, slots, HP) state instead of the largest one.
* A plan can be continued from a row (`prefix`, `t_free`, `resume`): what was played before stays as it is and only
  the rest is searched (used after a lost controller read, a miss, ...).

Position convention (measured, tools/s4t_snip/a6.py): a press on row T is fired from the x Bill has BEFORE that row's
move, with the facing the row's d-pad gives him; in the air the facing does not matter (centre = (3x + 640) // 8).

Movement classes (bit masks over px PXMIN..PXMAX, index = class * 2 + facing, facing 0 = right, 1 = left):
  I still | A moved 1 frame | M2 moved 2 | M3 moved 3 | M moved >= 4 | C2 still, 2 more still frames due |
  C1 still, 1 more due | N in the air, not drifting | D in the air, drifting
"""
from __future__ import annotations

from .base_plan import (BOX, BUSY_HIT, BUSY_MISS, CAP, CROUCH_Y, FLIGHT, FULL, NPX, PELLET_DX, PXMAX, PXMIN, STAND_Y,
                        Ent, Plan, centre_x, entities_from_trace, in_box, mask_list, mask_range)

__all__ = ["plan_room", "walk_rows", "entities_from_trace", "Ent", "Plan", "mask_range", "mask_list", "in_box"]

NCLS = 18
I0, I1, A0, A1, M20, M21, M30, M31, MM0, MM1, C20, C21, C10, C11, N0, N1, D0, D1 = range(NCLS)
EMPTY = (0,) * NCLS


def _shr(m):      # one px to the right
    return (m << 1) & FULL


def _shl(m):
    return m >> 1


def step_ground(R, mR=FULL, mL=FULL):
    """One ground frame without a crouch shot. mR / mL: positions (before the move) a press on this frame allows for
    a result facing right / left (FULL when there is no press)."""
    (i0, i1, a0, a1, m20, m21, m30, m31, mm0, mm1, c20, c21, c10, c11, _, _, _, _) = R
    startR = (i0 | i1 | m31 | mm1) & mR
    startL = (i0 | i1 | m30 | mm0) & mL
    return ((i0 | c10) & mR, (i1 | c11) & mL,
            _shr(startR), _shl(startL),
            _shr(a0 & mR), _shl(a1 & mL),
            _shr(m20 & mR), _shl(m21 & mL),
            _shr((m30 | mm0) & mR), _shl((m31 | mm1) & mL),
            m20 & mR, m21 & mL,
            (c20 | m30 | mm0) & mR, (c21 | m31 | mm1) & mL,
            0, 0, 0, 0)


def step_hold(R):
    """A frame on which the game is known not to read the pad (it re-uses the previous frame's buttons): whoever
    walks goes on walking, whoever stands goes on standing; nothing starts, stops or turns."""
    (i0, i1, a0, a1, m20, m21, m30, m31, mm0, mm1, c20, c21, c10, c11, n0, n1, d0, d1) = R
    return (i0 | c10, i1 | c11, 0, 0, _shr(a0), _shl(a1), _shr(m20), _shl(m21), _shr(m30 | mm0), _shl(m31 | mm1),
            0, 0, c20, c21, n0, n1, _shr(d0), _shl(d1))


def step_crouch(R, m):
    """A frame on which a crouch shot is pressed (Down + B, no Left/Right on this frame and the next)."""
    (i0, i1, a0, a1, m20, m21, m30, m31, mm0, mm1, c20, c21, c10, c11, _, _, _, _) = R
    return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            m20 & m, m21 & m,
            (i0 | c10 | c20 | m30 | mm0) & m, (i1 | c11 | c21 | m31 | mm1) & m,
            0, 0, 0, 0)


def step_air(R, m=FULL, start=True):
    """One airborne frame; start = may a drift begin on this row (not on the last two airborne rows: the tap is held
    two frames and must not run into the landing)."""
    n0, n1, d0, d1 = R[N0], R[N1], R[D0], R[D1]
    if not start:
        return (0,) * 14 + (n0 & m, n1 & m, _shr(d0 & m), _shl(d1 & m))
    return (0,) * 14 + (n0 & m, n1 & m, _shr((d0 | n0 | n1) & m), _shl((d1 | n0 | n1) & m))


def land(R):
    """Air classes -> ground classes (applied before the first ground row)."""
    return (R[N0], R[N1], 0, 0, 0, 0, 0, 0, 0, 0, R[D0], R[D1], 0, 0, 0, 0, 0, 0)


def still_only(R):
    """Positions from which a jump may start (standing still), as I masks."""
    return (R[I0] | R[C10] | R[C20], R[I1] | R[C11] | R[C21]) + (0,) * 16


def _union(R):
    u = 0
    for m in R:
        u |= m
    return u


def single(px, cls, f):
    """Mask tuple with exactly one position: cls 0..6 = ground class, 7 = N, 8 = D (the walk's state numbering)."""
    R = [0] * NCLS
    R[(14 if cls == 7 else 16 if cls == 8 else cls * 2) + f] = 1 << (px - PXMIN)
    return tuple(R)


def plan_room(ents, t_start, entry, air_y, hp_over=None, t_max=420, beam=12000, ntop=8, verbose=False, pre=None,
              cd0=CAP, forbid=None, no_press=None, not_before=None, plated=(), jump_y=None, danger=(), kill_by=None,
              keep=3, t0=1, steer=True, prefix=None, t_free=None, resume=None, lost=()):
    """Frame-synchronous beam search over (cooldown, slot free times, entity HP, jump phase) with position masks.

    t_start: first row on which Bill stands on the ground. entry: (mask facing right, mask facing left) of the px he
    may have on row t0 (in the air, not drifting). air_y: {T: arrival Y} for presses on airborne rows T < t_start.
    prefix / t_free / resume: the presses of an earlier plan that are replayed as they are on rows < t_free, and the
    walk state (px, class, facing) Bill really has before row t_free. lost: rows on which the pad is not read.
    Returns up to ntop Plans sorted by finish (T of the last required core hit); Plan.presses entries are
    (T, k, mask right, mask left, hits, pose) with pose 0 stand, 1 crouch, 2 hop/drop, 3 in a jump, 9 jump start."""
    hp_over = hp_over or {}
    forbid = forbid or set()
    no_press = no_press or set()
    not_before = not_before or {}
    plated = set(plated)
    lost = set(lost)
    pfx = {p[0]: p for p in (prefix or ())} if t_free is not None else {}
    cores = [e.eid for e in ents if e.kind == "core"]
    hp0 = tuple(hp_over.get(e.eid, e.hp0 if e.kind in ("core", "turret") else (1 if e.kind == "soldier" else 0))
                for e in ents)
    by_slot = sorted((e for e in ents if e.kind in ("core", "turret", "soldier")), key=lambda e: -e.slot)
    ocache = {}

    def live_at(ta, hps, strict=True):
        return tuple((e.eid, e.track[ta][0], e.track[ta][1],
                      (2 if hps[e.eid] > 8 else 5) if e.eid in plated else e.code) for e in by_slot
                     if hps[e.eid] > 0 and ta in e.track and e.track[ta][2]
                     and (not strict or ((ta, e.eid) not in forbid and ta >= not_before.get(e.eid, 0))))

    def outcomes(ta, k, hps, strict=True):
        live = live_at(ta, hps, strict)
        key = (k, live)
        r = ocache.get(key)
        if r is not None:
            return r
        res = {}
        for pose, ys in ((0, STAND_Y), (1, CROUCH_Y)):
            if pose == 1 and not any(in_box(ex, ys, ex, ey, code) for _, ex, ey, code in live):
                continue        # a crouch shot that can hit nothing is never needed (a standing miss is equivalent)
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

    def outcomes_air(ta, k, hps, ya, strict=True):
        live = live_at(ta, hps, strict)
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
            res[tuple(hits)] = res.get(tuple(hits), 0) | 1 << (px - PXMIN)
        ocache[key] = res
        return res

    J = len(jump_y) if jump_y else 0
    start_slots = tuple(sorted(pre)) if pre else (0,) * 10
    R0 = (0,) * 14 + (entry[0], entry[1], 0, 0)
    if t0 >= t_start:
        R0 = land(R0)
    states = {(cd0, start_slots, hp0, 0): [(R0, None)]}
    best = []
    best_fin = t_max + 100

    for t in range(t0, t_max):
        if not states:
            break
        nxt = {}

        def put(key, R, back):
            u = _union(R)
            if not u:
                return
            lst = nxt.get(key)
            if lst is None:
                nxt[key] = [(R, back, u)]
                return
            for (R2, _, u2) in lst:
                if u & ~u2 == 0 and all(a & ~b == 0 for a, b in zip(R, R2)):
                    return                      # nothing new
            lst[:] = [x for x in lst if not (x[2] & ~u == 0 and all(a & ~b == 0 for a, b in zip(x[0], R)))]
            lst.append((R, back, u))
            if len(lst) > keep:
                lst.sort(key=lambda x: -bin(x[2]).count("1"))
                del lst[keep:]

        ground = t >= t_start
        forced = t_free is not None and t < t_free
        pf = pfx.get(t) if forced else None
        hold = t in lost
        for (cd, slots, hps, jp), lst in states.items():
            if t + FLIGHT >= best_fin:
                continue
            if kill_by and not forced and any(hps[eid] > 0 and t > tk for eid, tk in kill_by.items()):
                continue                    # a soldier that had to be shot by now (its bullets killed Bill) is alive
            ns = tuple(0 if f <= t else f for f in slots)
            njp = 0 if (jp == 0 or jp >= J) else jp + 1
            ncd = min(cd + 1, CAP)
            nfree = ns.count(0)
            can = cd >= CAP and nfree and (pf is not None if forced else (t not in no_press and not hold))
            k = min(5, nfree)
            rest = ns[k:]
            for (R, back, *_u) in lst:
                if t == t_start and ground and (R[N0] | R[N1] | R[D0] | R[D1]):
                    R = land(R)
                if t_free is not None and t == t_free and resume is not None:
                    R = single(*resume)
                # -- no press on this row
                if not (forced and pf is not None):
                    if jp:
                        put((ncd, ns, hps, njp), R, back)
                    elif hold:
                        put((ncd, ns, hps, 0), step_hold(R), back)
                    elif ground:
                        put((ncd, ns, hps, 0), step_ground(R), back)
                    else:
                        put((ncd, ns, hps, 0), step_air(R, FULL, steer and t < t_start - 2), back)
                # -- jump start (the Y-88 core): from standing still, no movement until the landing
                if J and jp == 0 and ground and cd >= 2 and not hold and (pf is not None and pf[5] == 9 if forced else True):
                    Rs = still_only(R)
                    if Rs[0] | Rs[1]:
                        put((ncd, ns, hps, 1), Rs, (t, 0, Rs[0], Rs[1], (), 9, back))
                if not can or (forced and (pf[5] == 9 or pf[1] != k)):
                    continue
                strict = not forced
                if forced:
                    opts = [((pf[5], pf[4]), pf[2], pf[3])]        # exactly what was played
                elif jp:
                    ya = min(jump_y[jp - 1], 152) - 40
                    opts = [((3, hk), m, m) for hk, m in outcomes_air(t + FLIGHT, k, hps, ya, strict).items()]
                elif not ground:
                    if t not in air_y:
                        continue
                    opts = [((2, hk), m, m) for hk, m in outcomes_air(t + FLIGHT, k, hps, air_y[t], strict).items()]
                else:
                    opts = [(key, mR, mL) for key, (mR, mL) in outcomes(t + FLIGHT, k, hps, strict).items()]
                    bad = 0
                    if not forced:
                        for (d0, d1, dm) in danger:      # places where standing up to shoot at this time was fatal
                            if d0 <= t <= d1:
                                bad |= dm
                    if bad:
                        opts = [((pose, hk), (mR & ~bad) if pose == 0 else mR, (mL & ~bad) if pose == 0 else mL)
                                for (pose, hk), mR, mL in opts]
                for (pose, hk), mR, mL in opts:
                    if pose == 3:
                        Rn = (R[I0] & mR, R[I1] & mL) + (0,) * 16
                        aR, aL = Rn[0], Rn[1]
                    elif pose == 2:
                        Rn = step_air(R, mR, steer and t < t_start - 2)
                        aR = aL = mR
                    elif pose == 1:
                        Rn = step_crouch(R, mR)
                        aR, aL = mR, mL
                    else:
                        Rn = step_ground(R, mR, mL)
                        aR, aL = mR, mL
                    if not _union(Rn):
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
                    put((1, nslots, nh, njp), Rn, nb)
        if len(nxt) > beam:
            def score(item):
                (cd, slots, hps, jp), _ = item
                rem = sum(hps[c] for c in cores)
                return (rem, -len(set(slots)), sum(hps) - rem, -cd)
            nxt = dict(sorted(nxt.items(), key=score)[:beam])
        states = nxt
        if verbose and t % 20 == 0:
            print("t", t, "states", len(states), "best", best[0][0] if best else None, flush=True)
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


# ---------------------------------------------------------------------------------------------------------------
# the concrete walk for a plan: one d-pad button (or None) per row, obeying the same movement classes
_G_NEXT = {  # ground class -> [(next class, move)]  (move: 0 stay, 1 with the facing, -1 reverse, 2 start either way)
    0: ((0, 0), (1, 2)),            # I: stay | start
    1: ((2, 1),),                   # A -> M2
    2: ((3, 1), (5, 0)),            # M2 -> M3 | stop -> C2
    3: ((4, 1), (6, 0), (1, -1)),   # M3 -> M | stop -> C1 | reverse -> A
    4: ((4, 1), (6, 0), (1, -1)),   # M -> M | stop -> C1 | reverse -> A
    5: ((6, 0),),                   # C2 -> C1
    6: ((0, 0),),                   # C1 -> I
}
_G_HOLD = {0: (0, 0), 1: (2, 1), 2: (3, 1), 3: (4, 1), 4: (4, 1), 5: (6, 0), 6: (0, 0)}     # pad not read


def walk_rows(presses, t_start, entry, t0=1, avoid=(), jump_len=0, steer=True, prefer=None, force=None, lost=()):
    """Concrete movement for a plan. entry = [(px, facing)] possible states before row t0. Returns
    (dpad, pos, path) or (None, index of the press that cannot be reached, None): dpad[T] in (None, 'Left',
    'Right') for every row T up to the last press, pos[i] = (px before the press row, facing) of press i,
    pos['entry'] = (px, facing), path[T] = (px, class, facing) before row T (class 0..6 ground, 7 = N, 8 = D).
    Fewest walked frames; avoid = [(t0, t1, x0, x1)] where standing up to shoot was fatal; prefer = px the entry
    should be close to (tie-break); force = {T: button} rows that are already decided; lost = rows on which the
    pad is not read (nothing may start, stop or turn there)."""
    by_t = {}
    for n, p in enumerate(presses):
        by_t[p[0]] = (n, p)
    frozen = set()
    for p in presses:
        if p[5] == 9:
            frozen.update(range(p[0], p[0] + jump_len + 1))
    force = force or {}
    lost = set(lost)
    T_end = presses[-1][0]
    cur = {}
    for (px, f) in entry:
        cur[(px, 7 if t0 < t_start else 0, f)] = (abs(px - prefer) * 0.001 if prefer is not None else 0.0, None, None)
    layers = []
    for t in range(t0, T_end + 1):
        if t == t_start:
            cur = {((px, 0 if c == 7 else 5, f) if c >= 7 else (px, c, f)): v for (px, c, f), v in cur.items()}
        ground = t >= t_start
        pr = by_t.get(t)
        nxt = {}
        hold = t in lost
        for (px, c, f), (cost, _, _) in cur.items():
            if t in frozen:
                moves = [((px, 0, f), None, 0)] if c in (0, 5, 6) else []
            elif not ground:
                if c == 7:
                    moves = [((px, c, f), None, 0)]
                    if steer and t < t_start - 2 and not hold:
                        moves += [((px + 1, 8, 0), "Right", 1), ((px - 1, 8, 1), "Left", 1)]
                else:
                    moves = [((px + (1 if f == 0 else -1), 8, f), None, 0)]
            elif hold:
                nc, mv = _G_HOLD[c]
                if mv:
                    moves = [((px + (1 if f == 0 else -1), nc, f), "Right" if f == 0 else "Left", 1)]
                else:
                    moves = [((px, nc, f), None, 0)]
            else:
                moves = []
                for nc, mv in _G_NEXT[c]:
                    if mv == 0:
                        moves.append(((px, nc, f), None, 0))
                    elif mv == 1:
                        moves.append(((px + (1 if f == 0 else -1), nc, f), "Right" if f == 0 else "Left", 1))
                    elif mv == -1:
                        moves.append(((px + (-1 if f == 0 else 1), nc, 1 - f), "Left" if f == 0 else "Right", 1))
                    else:
                        moves.append(((px + 1, nc, 0), "Right", 1))
                        moves.append(((px - 1, nc, 1), "Left", 1))
            for (nst, btn, mc) in moves:
                npx, nc, nf = nst
                if not PXMIN <= npx <= PXMAX:
                    continue
                if t in force and force[t] != btn:
                    continue
                if pr is not None:
                    n, (pT, k, mR, mL, hk, pose) = pr
                    if pose == 1 or pose == 9 or pose == 3:
                        if btn is not None or (ground and nc in (1, 2, 3, 4)):
                            continue                 # crouch shot / jump: no Left/Right on this row
                        m = mR if f == 0 else mL
                        if pose == 1 and nc == 0:
                            nst = (npx, 6, nf)       # Down is held one more frame
                    else:
                        m = mR if nf == 0 else mL
                    if not (m >> (px - PXMIN)) & 1:
                        continue
                    if pose == 0 and any(a0 <= t <= a1 and x0 <= px <= x1 for (a0, a1, x0, x1) in avoid):
                        continue
                o = nxt.get(nst)
                if o is None or cost + mc < o[0]:
                    nxt[nst] = (cost + mc, (px, c, f), btn)
        if not nxt:
            later = [i for i, p in enumerate(presses) if p[0] >= t]
            return None, (later[0] if later else len(presses) - 1), None
        layers.append((t, cur))
        cur = nxt
    end = min(cur.items(), key=lambda kv: (kv[1][0] + (0.5 if kv[0][1] == 1 else 0), kv[0]))[0]
    layers.append((T_end + 1, cur))
    dpad = {}
    pos = {}
    path = {T_end + 1: end}
    st = end
    if end[1] == 1:                     # the last row started a move: the button is held one more frame
        dpad[T_end + 1] = "Right" if end[2] == 0 else "Left"
    for i in range(len(layers) - 1, 0, -1):
        t, lay = layers[i]
        cost, prev, btn = lay[st]
        dpad[t - 1] = btn
        if (t - 1) in by_t:
            n, p = by_t[t - 1]
            # facing of the shot: the facing after the row for a walking shot, the standing facing otherwise
            pos[n] = (prev[0], st[2] if p[5] == 0 else prev[2])
        st = prev
        path[t - 1] = st
    pos["entry"] = (st[0], st[2])
    return dpad, pos, path

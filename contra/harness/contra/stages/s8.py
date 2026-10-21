"""Stage 8 (Alien's Lair) solver: from a savestate one frame before the stage's first frame to the run's END event.

    python -m contra.stages.s8 <state> [--out s8/<name>] [--emus 3] [--prior <inputs.txt>] [--quick] [--nobarrier]

Closed-loop play with savestate lookahead (contra/stages/s3s8_engine.py). No RAM writes. Phases:
    P1   run to the alien guardian: Right held, B at the legal cadence, jumps / aims inserted where the default
         policy dies, stalls or would pick up a weapon (lookahead + repair)
    P1b  hill climbing for "Barrier picked up before the guardian" at the least cost in frames
    P2   guardian: jump-shoot schedule by hill climbing on "frame its HP reaches 0", then over the wall
    P3   run to the heart (same lookahead as P1)
    P4   heart: schedule by hill climbing on "frame BOSS_DEFEATED_FLAG is set"
    P5   stay alive and be on the ground with Down (or Up) held when control is taken away = END
The result is a legal input segment (check_inputs.py defaults) + a json report (events, lag, ignored-pad frames).
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from contra.stages.s3s8_lib import Pad, save_segment, check_rows, read_inputs, LOGS_DIR  # noqa: E402
from contra.stages import s3s8_lib  # noqa: E402
from contra.stages.s3s8_engine import Engine, Ck, gen, new_ov, ov_add, hpos, find_slot, first, TR  # noqa: E402
from contra.stages.s3s8_engine import pellets_born, b_starts  # noqa: E402
from contra.inputs import to_mask  # noqa: E402
from contra.stages.s3s8_fight import FightCfg, beam_fight  # noqa: E402

GUARDIAN, HEART, EGG = 0x10, 0x16, 0x15
# world X (screen*256 + offset + X) of the terrain jumps of the fitted TAS route (logs/s8_ref_trace.txt)
HINTS_P1 = (98, 224, 309, 383, 490)
HINTS_P3 = (799, 1009, 1066, 1138, 1255, 1602, 1678, 1782, 2588)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fail_index(tr, weapon, stall_n=14, stall_ok=None, start=0):
    """First trace index that shows a failure: death, weapon change, or no forward progress for stall_n frames
    on the ground (stall_ok(s) True = a stall is expected there)."""
    best = -1
    since = 0
    lagrun = 0
    for k, s in enumerate(tr):
        if k < start:
            continue
        lagrun = lagrun + 1 if s["lagged"] else 0
        if lagrun >= 12 and s["lroutine"] == 4:
            return k, "death"                       # the game hangs
        if s["death"] & 1 or s["pstate"] == 2:
            return k, "death"
        if s["weapon"] != weapon and s["lroutine"] == 4:
            return k, "weapon"
        p = hpos(s)
        if p > best:
            best, since = p, 0
        else:
            since += 1
            if since >= stall_n and not s["jump"] and not s["edge"] and s["lroutine"] == 4 and s["pstate"] == 1 \
                    and not (stall_ok and stall_ok(s)):
                return k, "stall"
    return None, None


def candidates(D, ov, level, kind):
    out = []
    if kind == "stall":
        ds = list(range(8, 40, 1)) if level == 0 else list(range(0, 90, 2))
        for d in ds:
            out.append(ov_add(ov, jumps=D - d))
        return out
    for a, b in ((D - 60, D + 12), (D - 30, D + 12), (D - 100, D + 12), (D - 16, D + 6)):
        out.append(ov_add(ov, aims=(a, b, "Up")))
        out.append(ov_add(ov, aims=(a, b, "Down")))
        out.append(ov_add(ov, nofire=(a, b)))
    for d in range(1, 76, 3 if level == 0 else 1):
        out.append(ov_add(ov, jumps=D - d))
    # move or drop a jump that is already scheduled shortly before the failure (a hinted terrain jump may be
    # what carries Bill into an enemy)
    for j in [x for x in ov["jumps"] if D - 130 <= x <= D]:
        for dj in ((-3, 3, -6, 6) if level == 0 else (-2, 2, -4, 4, -8, 8, -12, 12, -16, 16)):
            o = {k: list(v) for k, v in ov.items()}
            o["jumps"].remove(j)
            o["jumps"].append(j + dj)
            out.append(o)
            for a_ in ("Up", "Down"):
                o2 = {k: list(v) for k, v in o.items()}
                o2["aims"].append((D - 70, D + 12, a_))
                out.append(o2)
    if level >= 1:
        for d in range(4, 80, 6):
            for k in (3, 6, 12, 24):
                out.append(ov_add(ov, stops=(D - d, D - d + k)))
        for d in range(1, 76, 4):
            for a in ("Up", "Down"):
                out.append(ov_add(ov_add(ov, jumps=D - d), aims=(D - 60, D + 12, a)))
    if level >= 2:
        for d in range(4, 100, 5):
            for d2 in range(-60, 50, 9):
                if abs(d2 + d) > 8:
                    out.append(ov_add(ov_add(ov, jumps=D - d), jumps=D + d2))
        for d in range(4, 60, 6):
            for k in (8, 16, 32):
                out.append(ov_add(ov, lefts=(D - d, D - d + k)))
    return out


def fire_cands(D, ov, level):
    """Rule v2, on-demand firing: the shots that might remove whatever kills Bill at row D. Single presses
    ("taps", one volley of up to 5 pellets) first, then bursts; flat, up-right and down-right."""
    out = []

    def add(a, b, aim, gap=None):
        o = ov_add(ov, fires=(a, b) if gap is None else (a, b, gap))
        if aim:
            o = ov_add(o, aims=(a - 1, b + 1, aim))
        out.append(o)
    taps = (6, 12, 20, 30, 42, 56) if level == 0 else tuple(range(4, 92, 4))
    wins = ((D - 30, D + 12), (D - 60, D + 12)) if level == 0 else \
        ((D - 16, D + 6), (D - 30, D + 12), (D - 60, D + 12), (D - 100, D + 12), (D - 140, D + 12))
    for d in taps:
        for aim in (None, "Up", "Down"):
            add(D - d, D - d + 2, aim)
    for a, b in wins:
        for aim in (None, "Up", "Down"):
            add(a, b, aim)
    if level == 0:
        # what the first run's constant mash did for free: flat fire from far out (thinned afterwards)
        for d in (100, 160, 240):
            add(D - d, D + 12, None)
    if level >= 1:
        for d in (10, 24, 40, 60):                       # two volleys 10 rows apart
            for aim in (None, "Up", "Down"):
                add(D - d - 10, D - d + 2, aim, 10)
    # a shot already scheduled may be the cause (a capsule shot open: weapon pick-up; lag)
    if any(z[0] <= D + 12 and z[1] >= D - 100 for z in ov.get("fires", ())):
        for a, b in ((D - 30, D + 12), (D - 60, D + 12), (D - 100, D + 12)):
            out.append(ov_add(ov, nofire=(a, b)))
    return out


def move_cands(D, ov, level, kind):
    """Rule v2, on-demand firing: the repairs that move Bill instead (jumps, stops, steps back); at the higher
    levels combined with a burst."""
    out = []
    if kind == "stall":
        ds = list(range(8, 40, 1)) if level == 0 else list(range(0, 90, 2))
        for d in ds:
            out.append(ov_add(ov, jumps=D - d))
        return out
    for d in range(1, 76, 3 if level == 0 else 1):
        out.append(ov_add(ov, jumps=D - d))
    for j in [x for x in ov["jumps"] if D - 130 <= x <= D]:
        for dj in ((-3, 3, -6, 6) if level == 0 else (-2, 2, -4, 4, -8, 8, -12, 12, -16, 16)):
            o = {k: list(v) for k, v in ov.items()}
            o["jumps"].remove(j)
            o["jumps"].append(j + dj)
            out.append(o)
            if level >= 1:
                for a_ in (None, "Up", "Down"):
                    o2 = {k: list(v) for k, v in o.items()}
                    o2["fires"].append((D - 70, D + 12))
                    if a_:
                        o2["aims"].append((D - 71, D + 13, a_))
                    out.append(o2)
    if level >= 1:
        for d in range(4, 80, 6):
            for k in (3, 6, 12, 24):
                out.append(ov_add(ov, stops=(D - d, D - d + k)))
        for d in range(1, 76, 4):
            for a in (None, "Up", "Down"):
                o = ov_add(ov_add(ov, jumps=D - d), fires=(D - 60, D + 12))
                if a:
                    o = ov_add(o, aims=(D - 61, D + 13, a))
                out.append(o)
    if level >= 2:
        for d in range(4, 100, 5):
            for d2 in range(-60, 50, 9):
                if abs(d2 + d) > 8:
                    out.append(ov_add(ov_add(ov, jumps=D - d), jumps=D + d2))
        for d in range(4, 60, 6):
            for k in (8, 16, 32):
                out.append(ov_add(ov, lefts=(D - d, D - d + k)))
    return out


def run_phase(eng: Engine, ck: Ck, goal, weapon, ov=None, H=260, name="run", stall_ok=None, maxlevel=2, hints=(),
              base=("Right",), fire=True, cand_fn=None, progress=None, delag=True):
    """Default policy + repairs until goal(s) holds. Returns (ck at the goal frame, ov used).
    hints: world X positions (screen*256 + offset + X) at which a jump is known to be useful (terrain); a jump
    is scheduled on the first row Bill stands at or past each of them.
    fire: True = B at the legal cadence (the first run), False = never, "demand" (rule v2) = nothing is fired
    unless a repair asks for it: a failure in the lookahead is first answered with shots (fire_cands), and only
    when no shot helps with jumps and stops (move_cands). Among the repairs that work the one with the most
    progress wins, then the one with the fewest B presses."""
    ov = ov or new_ov()
    ov.setdefault("fires", [])
    level = 0
    guard = 0
    hints = sorted(hints)
    hi = 0
    demand = fire == "demand" and cand_fn is None
    cand_fn = cand_fn or candidates
    progress = progress or hpos
    lag_seen = set()
    while True:
        guard += 1
        if guard > 400:
            raise RuntimeError(f"{name}: no progress")
        rows, _ = gen(ck.pad, ck.i, H, ov, base=base, fire=fire)
        tr = eng.sim(ck, rows)
        if fire and delag:
            # second pass: a lag frame costs a whole frame. Lag in the running sections comes from our own
            # pellets (10 slots) on top of the enemies: try leaving out the presses just before it.
            fl = next((k for k, s in enumerate(tr[:H - 110]) if s["lagged"] and ck.i + k not in lag_seen), None)
            f0, _k0 = fail_index(tr, weapon, stall_ok=stall_ok)
            if fl is not None and demand and not any(z[0] <= ck.i + fl + 2 and z[1] > ck.i + fl - 60
                                                     for z in ov["fires"]):
                lag_seen.add(ck.i + fl)               # nothing of ours was fired before it: not our pellets
                fl = None
            if fl is not None and (f0 is None or f0 > fl + 40):
                D = ck.i + fl
                lag_seen.add(D)
                n = min(H, fl + 90)
                base_lag = sum(1 for s in tr[:n] if s["lagged"])
                base_prog = progress(tr[n - 1])
                cs = [ov_add(ov, nofire=(D - k, D + 2)) for k in (6, 11, 16, 24, 34, 46, 60)]
                trs = eng.sims(ck, [gen(ck.pad, ck.i, n, c, base=base, fire=fire)[0] for c in cs])
                pick = None
                for c, t in zip(cs, trs):
                    fi, _k = fail_index(t, weapon, stall_ok=stall_ok)
                    if fi is not None:
                        continue
                    lg = sum(1 for s in t if s["lagged"])
                    pg = progress(t[-1])
                    if lg < base_lag and pg > base_prog and (pick is None or (pg, -lg) > pick[0]):
                        pick = ((pg, -lg), c)
                if pick is not None:
                    # the whole horizon must still be clean with the change
                    t2 = eng.sim(ck, gen(ck.pad, ck.i, H, pick[1], base=base, fire=fire)[0])
                    f2, _k2 = fail_index(t2, weapon, stall_ok=stall_ok)
                    if (f2 is None) >= (f0 is None) and progress(t2[-1]) > progress(tr[-1]):
                        log(f"[{name}] lag at row {D}: removed by {pick[1]['nofire'][-1]} "
                            f"(progress {progress(tr[-1])} -> {progress(t2[-1])})")
                        ov = pick[1]
                        continue
        # schedule the next hinted jump inside this horizon, then simulate again
        while hi < len(hints) and hpos(tr[0]) > hints[hi] + 2:
            hi += 1
        if hi < len(hints):
            k = first(tr, lambda s: hpos(s) >= hints[hi])
            if k is not None and k + 1 < H - 60:
                # only from the ground, and only close to the hinted spot (a repair may have changed the path)
                kk = next((q for q in range(k, min(k + 12, len(tr))) if not tr[q]["jump"] and not tr[q]["edge"]
                           and hpos(tr[q]) <= hints[hi] + 10), None)
                if kk is not None and not any(abs(j - (ck.i + kk + 1)) < 12 for j in ov["jumps"]):
                    ov = ov_add(ov, jumps=ck.i + kk + 1)
                hi += 1
                continue
        g = first(tr, goal)
        f, kind = fail_index(tr, weapon, stall_ok=stall_ok)
        if g is not None and (f is None or g <= f):
            ck, _ = eng.commit(ck, rows[:g + 1])
            return ck, ov
        if f is None:
            ck, _ = eng.commit(ck, rows[:H - 110])
            level = 0
            continue
        D = ck.i + f
        if demand:
            # rule v2: shots first; Bill is only moved (a jump costs a frame) when no shot helps
            groups = [move_cands(D, ov, level, kind)] if kind == "stall" else \
                [fire_cands(D, ov, level), move_cands(D, ov, level, kind)]
        else:
            groups = [cand_fn(D, ov, level, kind)]
        n = f + 110
        scored = []
        ncand = 0
        for cands in groups:
            if not cands:
                continue
            ncand += len(cands)
            rl = [gen(ck.pad, ck.i, n, c, base=base, fire=fire)[0] for c in cands]
            trs = eng.sims(ck, rl)
            for c, rows_c, t in zip(cands, rl, trs):
                fi, _k = fail_index(t, weapon, stall_ok=stall_ok)
                gi = first(t, goal)
                if gi is not None and (fi is None or gi <= fi):
                    fi = None
                ok = fi is None
                prog = progress(t[-1]) if ok else progress(t[fi])
                scored.append((ok, (fi if fi is not None else 10 ** 6), prog, c, -b_starts(rows_c)))
            if any(z[0] for z in scored):
                break
            if demand and len(groups) > 1 and cands is groups[0] and max(z[1] for z in scored) > f + 40:
                break           # a shot moves the failure 40+ rows away: take it before a jump (a frame) is tried
        cands = [None] * ncand
        scored.sort(key=lambda z: (z[0], z[2] if z[0] else z[1], z[2], z[4]), reverse=True)
        ok, fi, prog, c, _nb = scored[0]
        if (ok or fi > f + 20) and demand and len(c["fires"]) > len(ov["fires"]):
            # rule v2: a burst that works is thinned: wider gaps between its volleys, half of it, single
            # volleys - whatever still gives the same progress with fewer presses (for a burst that only moves
            # the failure later: whatever moves it at least as far)
            nb0 = -_nb
            for _round in range(4):
                z = c["fires"][-1]
                a_, b_ = z[0], z[1]
                g_ = z[2] if len(z) > 2 else 5
                if b_ - a_ <= 6:
                    break
                alts = [(a_, b_, g2) for g2 in (8, 12, 18, 27, 40, 60) if g2 > g_ and g2 < b_ - a_]
                mid = (a_ + b_) // 2
                alts += [(a_, mid) + tuple(z[2:]), (mid, b_) + tuple(z[2:])]
                alts += [(x, x + 2) for x in sorted({a_ + (b_ - a_) * q // 5 for q in range(5)})]
                cs = []
                for alt in alts:
                    o = {k: list(v) for k, v in c.items()}
                    o["fires"][-1] = alt
                    cs.append(o)
                rl = [gen(ck.pad, ck.i, n, o, base=base, fire=fire)[0] for o in cs]
                trs = eng.sims(ck, rl)
                pick = None
                for o, rows_c, t in zip(cs, rl, trs):
                    fi2, _k = fail_index(t, weapon, stall_ok=stall_ok)
                    gi = first(t, goal)
                    if gi is not None and (fi2 is None or gi <= fi2):
                        fi2 = None
                    if ok and (fi2 is not None or progress(t[-1]) < prog):
                        continue
                    if not ok and fi2 is not None and fi2 < fi:
                        continue
                    nb2 = b_starts(rows_c)
                    if nb2 < nb0 and (pick is None or nb2 < pick[0]):
                        pick = (nb2, o)
                if pick is None:
                    break
                log(f"[{name}] burst {z} thinned to {pick[1]['fires'][-1]}: {nb0} -> {pick[0]} presses in the horizon")
                nb0, c = pick
        fixd = {k: v[len(ov[k]):] for k, v in c.items() if len(v) > len(ov[k])}
        if ok:
            log(f"[{name}] {kind} at row {D} (pos {hpos(tr[f])}): fixed, level {level}, {len(cands)} cands, "
                f"progress {prog}; fix = {fixd}")
            ov = c
            level = 0
        else:
            log(f"[{name}] {kind} at row {D} (pos {hpos(tr[f])}): no clean fix at level {level} ({len(cands)} cands); "
                f"latest failure {fi - f:+d} with {fixd}")
            if fi > f + 20:
                ov = c
                level = 0
            elif level < maxlevel:
                level += 1
            elif fi > f + 6:
                ov = c
                level = 0
            else:
                raise RuntimeError(f"{name}: stuck at row {D}")


def climb(eng, ck, ov, n, cost, mutate, iters, name, base=("Right",), seed=1, patience=150, good_enough=None,
          after_good=40, fire=True, press_w=0.0):
    """Hill climbing on overrides: cost(trace) lower is better. Returns (ov, cost, trace).
    press_w (rule v2): added to the cost per B press, so that of two equal results the one with fewer shots wins."""
    rng = random.Random(seed)
    rows, _ = gen(ck.pad, ck.i, n, ov, base=base, fire=fire)
    tr = eng.sim(ck, rows)
    best = cost(tr) + press_w * b_starts(rows)
    log(f"[{name}] start cost {best}")
    stale = 0
    it = 0
    while it < iters and stale < patience:
        batch = [mutate(ov, rng) for _ in range(len(eng.emus) * 2)]
        rl = [gen(ck.pad, ck.i, n, c, base=base, fire=fire)[0] for c in batch]
        trs = eng.sims(ck, rl)
        it += len(batch)
        improved = False
        for c, t, rws in zip(batch, trs, rl):
            v = cost(t) + press_w * b_starts(rws)
            if v < best:
                best, ov, tr, improved = v, c, t, True
        if improved:
            stale = 0
            log(f"[{name}] it {it}: cost {best}")
        else:
            stale += len(batch)
        if good_enough is not None and best <= good_enough and stale >= after_good:
            break
    return ov, best, tr


def tune_jumps(eng, ck0, ov, goal, weapon, n, name, lo, deltas=(-3, -2, -1, 1, 2, 3), stall_ok=None, base=("Right",),
               sweeps=2, fire=True):
    """Coordinate descent on the rows of the scheduled jumps (those >= lo): each is moved by a few rows and
    kept where the goal frame comes sooner without a failure before it. Returns (ov, goal index from ck0)."""
    def run(o):
        return gen(ck0.pad, ck0.i, n, o, base=base, fire=fire)[0]

    def val(t):
        g = first(t, goal)
        f, _k = fail_index(t, weapon, stall_ok=stall_ok)
        if g is None or (f is not None and f < g):
            return None
        return g
    best = val(eng.sim(ck0, run(ov)))
    if best is None:
        return ov, None
    for _sw in range(sweeps):
        improved = False
        for j in sorted(x for x in ov["jumps"] if x >= lo):
            cands = []
            for d in deltas:
                o = {k: list(v) for k, v in ov.items()}
                o["jumps"].remove(j)
                o["jumps"].append(j + d)
                cands.append(o)
            o = {k: list(v) for k, v in ov.items()}
            o["jumps"].remove(j)
            cands.append(o)                           # no jump at all
            trs = eng.sims(ck0, [run(c) for c in cands])
            for c, t in zip(cands, trs):
                v = val(t)
                if v is not None and v < best:
                    best, ov, improved = v, c, True
        log(f"[{name}] jump tuning sweep: goal at +{best}")
        if not improved:
            break
    return ov, best


def boss_hp(s, typ):
    """HP of the boss slot of type typ in a trace state; None when no such slot exists."""
    k = find_slot(s, typ)
    if k is None:
        return None
    return s[f"h{k}"]


def greedy_fight(eng, ck, weapon, typ, name, r_ref=0.5, first_land_after=None, maxseg=14, heart=False,
                 base=("Right",), hp_fn=None, progs=None, extra_ov=None, first_credit=10, hp_full=103, taps=None,
                 stop_fn=None):
    """Jump-and-shoot fight, one jump at a time. From the checkpoint every candidate (wait, B phase, aim program
    for rise / top / fall) is simulated to its landing; the one with the smallest
        frames used + HP left / r_ref
    is committed. Returns the checkpoint on the frame the boss's HP reached 0 (heart: boss flag set)."""
    PROGS = (("U", "U", "U"), ("F", "F", "F"), ("U", "F", "U"), ("F", "U", "F"), ("U", "U", "F"), ("F", "U", "U"),
             ("F", "F", "U"), ("U", "F", "F"), ("D", "D", "D"), ("F", "D", "F"), ("F", "F", "D"))
    AIM = {"U": "Up", "F": "Flat", "D": "Down"}
    PROGS = progs or PROGS
    hp_fn = hp_fn or (lambda s_: boss_hp(s_, typ))
    seg = 0
    used = new_ov()                 # union of the committed segments' overrides (None once an escape was used)

    def keep_ov(o):
        nonlocal used
        if used is not None and o is not None:
            for k_, v_ in o.items():
                used[k_].extend(v_)
        else:
            used = None
    while seg < maxseg:
        seg += 1
        cands = []
        first_seg = first_land_after is not None and seg == 1
        waits = tuple(range(0, 72, 3)) if first_seg else (0, 1, 2, 3, 5)
        for d in waits:
            for ph in ((0,) if first_seg else (0, 1, 2)):
                for pg in PROGS:
                    for tap in (taps or [None]):
                        j0 = ck.i + d
                        o = new_ov()
                        o["jumps"].append(j0)
                        if ph:
                            o["nofire"].append((ck.i, ck.i + ph))
                        o["aims"].append((ck.i, j0 + 16, AIM[pg[0]]))
                        o["aims"].append((j0 + 16, j0 + 44, AIM[pg[1]]))
                        o["aims"].append((j0 + 44, j0 + 160, AIM[pg[2]]))
                        lab = pg
                        if tap:
                            # a side step in the air: Left tap, then a Right tap to come back
                            o["holds"].append((j0 + 1 + tap[0], j0 + 3 + tap[0], "Left"))
                            o["holds"].append((j0 + 1 + tap[0] + tap[1], j0 + 3 + tap[0] + tap[1], "Right"))
                            lab = pg + (f" side-step {tap}",)
                        cands.append((d, ph, lab, o))
        if not first_seg:
            for pg in ("U", "F"):                          # stand and shoot for 24 frames
                o = new_ov()
                o["aims"].append((ck.i, ck.i + 60, AIM[pg]))
                cands.append((-1, 0, (pg,), o))
        n = 80 + ((80 + first_credit) if first_seg else 0)
        if extra_ov:
            for c in cands:
                for k_, v_ in extra_ov.items():
                    c[3][k_].extend(v_)
        rl = [gen(ck.pad, ck.i, n, c[3], base=base)[0] for c in cands]
        trs = eng.sims(ck, rl)
        best = None
        CREDIT = first_credit if first_seg else 10
        for c, rows, t in zip(cands, rl, trs):
            d = c[0]
            dead_at = None
            end = None
            fail = False
            hp0 = None
            hp_cred = None
            lagrun = 0
            for k, s_ in enumerate(t):
                lagrun = lagrun + 1 if s_["lagged"] else 0
                if s_["death"] & 1 or s_["pstate"] == 2 or s_["weapon"] != weapon or lagrun >= 12:
                    fail = True                     # lagrun: the game hangs (dragon arm freeze)
                    break
                hp = hp_fn(s_)
                if hp0 is None and hp is not None:
                    hp0 = hp
                if (hp is not None and hp == 0) or (heart and s_["bossdef"]):
                    dead_at = k
                    break
                if end is None:
                    if d < 0:
                        if k >= 23:
                            end = k
                    elif k > d + 12 and not s_["jump"] and not s_["edge"]:
                        if not (first_seg and ck.i + k < first_land_after):
                            end = k
                if end is not None:
                    hp_cred = hp
                    if k >= end + CREDIT:
                        break
            if hp0 is None:
                hp0 = hp_full
            else:
                hp0 = max(hp0, hp_full) if first_seg else hp0
            if end is not None and hp_cred is None:
                hp_cred = hp_full
            if fail and (end is None or True):
                # a death inside the credit window still disqualifies: the next segment starts from `end`
                continue
            if dead_at is not None:
                score = (2, -dead_at)
                end = dead_at
                hp_end = 0
            elif end is None or hp_cred is None or hp0 is None:
                if end is None:
                    continue
                score = (0, -end)
                hp_end = hp_cred
            else:
                score = (1, (hp0 - hp_cred) / (end + 1), -end)
                hp_end = hp_cred
            if best is None or score > best[0]:
                best = (score, end, hp_end, c, rows, dead_at)
        if best is None:
            # every jump / stand dies: get out of the way first (a walk or a drifting jump, firing on), 40 rows
            esc = []
            for d in (0, 2, 4, 8, 12, 20):
                for dirb in ("Left", "Right"):
                    for k_ in (6, 10, 16, 24):
                        for jmp in (False, True):
                            o = new_ov()
                            o["aims"].append((ck.i, ck.i + 200, "Up"))
                            o["holds"].append((ck.i + d, ck.i + d + k_, dirb))
                            if jmp:
                                o["jumps"].append(ck.i + d)
                                o["holds"].append((ck.i + d + k_ + 2, ck.i + d + k_ + 4, "Left" if dirb == "Right" else "Right"))
                            esc.append((d, dirb, k_, jmp, o))
            rl2 = [gen(ck.pad, ck.i, 100, c_[4], base=base)[0] for c_ in esc]
            trs2 = eng.sims(ck, rl2)
            pick = None
            for c_, rows_, t_ in zip(esc, rl2, trs2):
                if any(z["death"] & 1 or z["pstate"] == 2 or z["weapon"] != weapon for z in t_):
                    continue
                k_end = next((q for q in range(40, len(t_)) if not t_[q]["jump"] and not t_[q]["edge"]), None)
                if k_end is None:
                    continue
                hp_ = hp_fn(t_[k_end])
                sc_ = (-(hp_ if hp_ is not None else hp_full), -k_end)
                if pick is None or sc_ > pick[0]:
                    pick = (sc_, k_end, rows_, c_)
            if pick is None:
                raise RuntimeError(f"{name}: every candidate of segment {seg} dies")
            _sc, k_end, rows_, c_ = pick
            ck, trc = eng.commit(ck, rows_[:k_end + 1])
            log(f"[{name}] segment {seg}: escape (wait {c_[0]}, {c_[1]} {c_[2]} rows{', jump' if c_[3] else ''}): {k_end + 1} rows")
            ck.dead = False
            keep_ov(c_[4])
            ck.ov_used = used
            if stop_fn is not None and trc and stop_fn(trc[-1], ck.i):
                return ck
            continue
        score, end, hp_end, c, rows, dead_at = best
        ck, trc = eng.commit(ck, rows[:end + 1])
        log(f"[{name}] segment {seg}: wait {c[0]}, B phase {c[1]}, aims {''.join(c[2])}: {end + 1} rows, boss HP {hp_end}"
            + (" DEAD" if dead_at is not None else ""))
        ck.dead = dead_at is not None
        keep_ov(c[3])
        ck.ov_used = used
        if dead_at is not None:
            return ck
        if stop_fn is not None and trc and stop_fn(trc[-1], ck.i):
            return ck
    raise RuntimeError(f"{name}: boss still alive after {maxseg} segments")


# level data (bank2.asm level_8_enemy_screen_xx): scroll position at which the boss slot appears, its X and Y then,
# the scroll position at which the screen stops; bullet boxes from collision_box_codes_04 (codes 8 and 7), shifted
# by the +1 the carry adds (measured: guardian hit from X 149 / Y 114, heart from X 166 / Y 85..140)
BOSS = {"guardian": dict(typ=GUARDIAN, box=(-27, 28, -17, 18), virt=(432, 240, 96, 496)),
        "heart": dict(typ=HEART, box=(-27, 28, -27, 28), virt=(2512, 240, 112, 2560))}


def beam_boss(eng, ck0, weapon, kind, anchor, quick=False, runs=None):
    """Second pass: the boss fight by beam search over press rows / aims / jumps (s3s8_fight.py). ck0 = the
    checkpoint 80 rows before `anchor` (guardian: its spawn row; heart: the row the boss scroll starts).
    Returns the checkpoint on the frame the boss's HP reached 0, or None when every beam failed.
    runs: the beams to try, each (W, free offsets[, dict of FightCfg overrides / "strat": rows after the anchor
    up to which the beam is stratified by the first jump]); default: the lists below."""
    b = BOSS[kind]
    alive = None
    runs_in = runs
    if kind == "guardian":
        def mode(s, js):
            return "free" if (not js and hpos(s) < 560) else "asap"
        strat = anchor + 75
        # rule v2 pass: the kill row moves by +-5 with the phase the search starts on (measured 749..761 from
        # the same state), so four beams instead of two; 60-110 s each
        # 2026-10-16: W24 beams added (from the c1 state's fight start: W24 off0 737, off2 738, off1 751 against
        # W16 off0 751, off2 759, W8 770, W12 off1 757); W8 and W16 off2 never won and were dropped
        runs = ((8, (0,)),) if quick else ((24, (0,)), (24, (2,)), (16, (0,)), (12, (1,)))
        # An up-right volley from the platform can open the M capsule that flies along the top of the screen;
        # its item then lies on the floor behind the wall and would change the weapon 150 rows after the kill.
        # Forbidding that (alive_fn: no weapon item during the fight) cost 8-10 rows (kill 759 against 751);
        # jumping the item costs one. So it is allowed, charged one row below, and the wall search jumps it.
    else:
        def mode(s, js):
            return "asap" if (js or s["autodone"]) else "free"
        strat = anchor + 130
        runs = ((8, (0,)),) if quick else ((24, (0,)), (16, (2,)))
    best = None
    allinfo = []
    for run in (runs_in or runs):
        W, offs = run[0], run[1]
        extra = dict(run[2]) if len(run) > 2 else {}
        st_ = anchor + extra.pop("strat") if "strat" in extra else strat
        tagx = "".join(f" {k}={v}" for k, v in (run[2].items() if len(run) > 2 else ()))
        cfg = FightCfg(typ=b["typ"], box=b["box"], virt=b["virt"], W=W,
                       name=f"{kind} W{W} off{','.join(str(o) for o in offs)}{tagx}", log=log,
                       weapon=weapon, jump_mode=mode, strat_until=st_, free_offsets=offs, alive_fn=alive)
        for k_, v_ in extra.items():
            setattr(cfg, k_, v_)
        try:
            rows, info = beam_fight(eng, ck0, cfg)
        except RuntimeError as ex:
            log(f"[{kind}] beam failed: {ex}")
            continue
        last = eng.sim(ck0, rows)[-1]
        info["item_left"] = any(last[f"r{k}"] and last[f"t{k}"] == 0 for k in range(16))
        info["cost"] = info["kill_row"] + (1 if info["item_left"] else 0)
        if info["item_left"]:
            log(f"[{kind}] this fight leaves a weapon item on the screen (one more jump: charged 1 row)")
        info["beam"] = cfg.name
        allinfo.append(dict(info))
        if best is None or info["cost"] < best[1]["cost"]:
            best = (rows, info)
    if best is None:
        return None
    ck, _ = eng.commit(ck0, best[0])
    ck.dead = True
    ck.info = dict(best[1])
    ck.info["all_beams"] = allinfo
    return ck


def mutator(lo, hi, aims=("Up", "Up", "Down", "Flat"), p_left=0.06, demand=False):
    def mut_demand(o, rng):
        """Rule v2 (on-demand firing): a mutation is a burst or a single volley with an aim, not an aim window
        under a constant mash."""
        o = {k: list(v) for k, v in o.items()}
        o.setdefault("fires", [])
        r = rng.random()
        js = [j for j in o["jumps"] if lo <= j < hi]
        if r < 0.22 and js:
            j = rng.choice(js)
            o["jumps"].remove(j)
            o["jumps"].append(j + rng.choice((-8, -5, -3, -2, -1, 1, 2, 3, 5, 8)))
        elif r < 0.28:
            o["jumps"].append(rng.randrange(lo, hi))
        elif r < 0.32 and js:
            o["jumps"].remove(rng.choice(js))
        elif r < 0.62:
            a = rng.randrange(lo, hi)
            b = a + rng.choice((2, 2, 7, 12, 20, 30, 50))
            o["fires"].append((a, b))
            am = rng.choice(aims)
            if am != "Flat":
                o["aims"].append((a - 1, b + 1, am))
        elif r < 0.70:
            a = rng.randrange(lo, hi)
            o["aims"].append((a, a + rng.choice((3, 5, 8, 12, 20, 30, 50)), rng.choice(aims)))
        elif r < 0.76:
            a = rng.randrange(lo, hi)
            o["stops"].append((a, a + rng.choice((2, 4, 8, 16, 30, 60))))
        elif r < 0.76 + p_left:
            a = rng.randrange(lo, hi)
            o["lefts"].append((a, a + rng.choice((2, 4, 8, 16))))
        else:
            k = rng.choice(("fires", "fires", "aims", "stops", "lefts"))
            am = [z for z in o[k] if z[0] >= lo]
            if am:
                z = rng.choice(am)
                o[k].remove(z)
                if k == "fires" and z[1] - z[0] > 6 and rng.random() < 0.6:      # shorten a burst instead
                    h = (z[0] + z[1]) // 2
                    o[k].append((z[0], h) if rng.random() < 0.5 else (h, z[1]))
        return o

    def mut(o, rng):
        o = {k: list(v) for k, v in o.items()}
        r = rng.random()
        js = [j for j in o["jumps"] if lo <= j < hi]
        if r < 0.30 and js:
            j = rng.choice(js)
            o["jumps"].remove(j)
            o["jumps"].append(j + rng.choice((-8, -5, -3, -2, -1, 1, 2, 3, 5, 8)))
        elif r < 0.38:
            o["jumps"].append(rng.randrange(lo, hi))
        elif r < 0.44 and js:
            o["jumps"].remove(rng.choice(js))
        elif r < 0.68:
            a = rng.randrange(lo, hi)
            o["aims"].append((a, a + rng.choice((3, 5, 8, 12, 20, 30, 50)), rng.choice(aims)))
        elif r < 0.78:
            a = rng.randrange(lo, hi)
            o["nofire"].append((a, a + rng.choice((1, 2, 3, 4))))
        elif r < 0.86:
            a = rng.randrange(lo, hi)
            o["stops"].append((a, a + rng.choice((2, 4, 8, 16, 30, 60))))
        elif r < 0.86 + p_left:
            a = rng.randrange(lo, hi)
            o["lefts"].append((a, a + rng.choice((2, 4, 8, 16))))
        else:
            k = rng.choice(("aims", "nofire", "stops", "lefts"))
            am = [z for z in o[k] if z[0] >= lo]
            if am:
                o[k].remove(rng.choice(am))
        return o
    return mut_demand if demand else mut


def press_report(rows, tr, ev, prior=()):
    """Rule v2 bookkeeping for a finished segment: B presses per section, what every press fired (pellets
    created; 0 = wasted, no bullet slot was free), and the fullest 600 / 1,800-row windows (the prior history
    counted). tr = the open-loop replay's trace of rows."""
    n = len(rows)
    bs = [i for i, r in enumerate(rows) if "B" in r and (i == 0 or "B" not in rows[i - 1])]
    born = [0] + [pellets_born(tr[k - 1], tr[k]) for k in range(1, min(len(tr), n))]
    used = set()
    per = []
    for i in bs:
        k = next((q for q in (i, i + 1, i + 2) if q < len(born) and born[q] and q not in used), None)
        if k is not None:
            used.add(k)
        per.append((i, 0 if k is None else born[k]))
    sp, gd, tg, hd = ev.get("guardian_spawn"), ev.get("guardian_dead"), ev.get("boss_scroll"), ev.get("heart_dead_flag")
    out = {"B_presses": len(bs), "sections": {}}
    if None not in (sp, gd, tg, hd):
        secs = (("P1 run", 0, sp - 80), ("guardian fight", sp - 80, gd + 1), ("P3 run", gd + 1, tg - 80),
                ("heart fight", tg - 80, hd + 1), ("ending", hd + 1, n))
        for name, a, b in secs:
            ps = [nb for i, nb in per if a <= i < b]
            out["sections"][name] = {"rows": [a, b], "presses": len(ps), "pellets": sum(ps),
                                     "presses_that_fired_nothing": sum(1 for q in ps if q == 0),
                                     "lag": sum(1 for s in tr[a:b] if s["lagged"])}
    pri = list(prior)
    allr = pri + list(rows)
    st = [i for i, r in enumerate(allr) if "B" in r and (i == 0 or "B" not in allr[i - 1])]
    for w in (60, 600, 1800):
        j, best, at = 0, 0, None
        for i in range(len(st)):
            while st[i] - st[j] >= w:
                j += 1
            if st[i] >= len(pri) and i - j + 1 > best:
                best, at = i - j + 1, st[i] - len(pri)
        out[f"B_max_in_{w}"] = best
        out[f"B_max_in_{w}_ends_at_row"] = at
    return out


def trim(ov, i):
    """Drop overrides that end before row i."""
    return {k: [z for z in v if (z if isinstance(z, int) else z[1]) >= i - 2] for k, v in ov.items()}


def end_index(t):
    """(A index, P index) in a trace: A = first frame with level routine 9, P = first later frame standing."""
    a = first(t, lambda s: s["lroutine"] == 9)
    if a is None:
        return None, None
    p = next((k for k in range(a + 1, len(t)) if t[k]["pseq"] == 0 and not (t[k]["jump"] & 15)
              and t[k]["aim"] in (2, 7)), None)
    return a, p


# Rule v2: what the two fights are planned to need (measured: the beam fights of the first complete run used 46
# and 33 B presses, none of them without a pellet), over which rows relative to their anchor, and how far the heart's
# scroll trigger lies behind the guardian's death (2,061-2,065 rows in every run so far).
RES_GUARDIAN = (-80, 245, 60)       # rows relative to the guardian's spawn row, presses kept back
RES_HEART = (-80, 215, 48)          # rows relative to the boss scroll's first row
SPAWN_EST, TRIG_AFTER_KILL = 517, 2062


def solve(state: str, out: str = "s8/run", emus: int = 3, prior_rows=(), quick: bool = False, eng: Engine | None = None,
          barrier: bool = True, beam: bool = True, fire="demand"):
    """fire: "demand" (rule v2: the running sections fire only where a lookahead repair asks for a shot) or True
    (the first run's metronome, B at the legal cadence; the press budget then throttles it)."""
    own = eng is None
    eng = eng or Engine(emus, tag="s8")
    t0 = time.time()
    rep = {"state": state, "events": {}, "fire_mode": str(fire), "windows": [list(w) for w in s3s8_lib.WINDOWS]}
    tagn = out.replace("/", "_")
    FM = fire
    try:
        root = eng.root(state, prior_rows)
        off = root.pad.t                    # Pad row of the segment's row 0 (the history comes before it)

        def plan(*fights):
            """reserve entries for fights given as (anchor row of the segment, (from, to, presses))."""
            return tuple((off + a + r[0], off + a + r[1], r[2], "B") for a, r in fights)
        root.pad.reserve = plan((SPAWN_EST, RES_GUARDIAN), (SPAWN_EST + 232 + TRIG_AFTER_KILL, RES_HEART))
        rep["prior_rows"] = len(prior_rows)
        rep["B_room_at_start"] = list(root.pad.room("B"))
        log(f"press budget {s3s8_lib.WINDOWS}; history {len(prior_rows)} rows; B presses that still fit each "
            f"window at the stage's first row: {rep['B_room_at_start']}; fire mode {fire}")
        ck = root
        tr0 = eng.sim(ck, [()] * 3)
        L = next(s["frame"] for s in tr0 if s["lroutine"] == 4)
        weapon = tr0[-1]["weapon"]
        rep["L"] = L
        rep["weapon_in"] = weapon
        rep["fc_at_L"] = next(s["fc"] for s in tr0 if s["lroutine"] == 4)
        rep["rng_at_L"] = next(s["rng"] for s in tr0 if s["lroutine"] == 4)
        log(f"stage 8 from {state}: L = frame {L}, weapon ${weapon:02x}, fc {rep['fc_at_L']}")

        def gexists(s):
            return find_slot(s, GUARDIAN) is not None

        # ---- P1: to the guardian's spawn (terrain jumps hinted from the reference route, then repaired)
        ck, ov = run_phase(eng, ck, gexists, weapon, name="P1", hints=HINTS_P1, fire=FM)
        ov1, g1 = tune_jumps(eng, root, ov, gexists, weapon, ck.i + 40, "P1", 0, fire=FM)
        if g1 is not None and g1 + 1 < ck.i:
            log(f"P1: jump tuning moved the guardian's spawn from row {ck.i} to row {g1 + 1}")
            ck, _ = eng.commit(root, gen(root.pad, 0, g1 + 1, ov1, fire=FM)[0])
            ov = ov1
        spawn = ck.i
        bar = eng.sim(ck, [("Right",)] * 70)[-1]["barrier"]
        if barrier and not bar:
            # ---- P1b: the Barrier capsule flies along the bottom of screens 0-1: shoot it (down-right from the
            # platform) and take the item in stride. Hill climbing on aims / jump shifts over the last 260 rows.
            ckb, _ = eng.commit(root, ck.rows[:max(0, spawn - 260)])
            nb = spawn - ckb.i + 80

            def bcost(t):
                fi, _k = fail_index(t, weapon, stall_ok=gexists)
                if fi is not None:
                    return 10 ** 6 - fi
                g = first(t, gexists)
                if g is None:
                    return 10 ** 5
                # rule v2: the item has to be in hand before the guardian fight's search takes over (80 rows
                # before the spawn); a pick-up after that row is thrown away with the rows it replaces
                return g + (0 if (t[min(len(t) - 1, g + 60)]["barrier"] and g >= 84 and t[g - 84]["barrier"]) else 2000)

            dem = FM == "demand"
            ov_seed, n_it = ov, (120 if quick else 420)
            if dem:
                # nothing is fired by default now, so the capsule has to be aimed at: scan one volley / a short
                # burst down-right over the rows in which it passes under the platform, then let the climb trim it
                seeds = []
                for a_ in range(max(ckb.i + 2, spawn - 235), spawn - 88, 4):
                    for ln in (2, 12):
                        seeds.append(ov_add(ov_add(ov, fires=(a_, a_ + ln)), aims=(a_ - 1, a_ + ln + 1, "Down")))
                rl_s = [gen(ckb.pad, ckb.i, nb, o, fire=FM)[0] for o in seeds]
                trs_s = eng.sims(ckb, rl_s)
                sc_s = sorted(((bcost(t_) + 0.01 * b_starts(r_), k_) for k_, (r_, t_) in enumerate(zip(rl_s, trs_s))))
                if sc_s and sc_s[0][0] < 2000:
                    ov_seed = seeds[sc_s[0][1]]
                    n_it = 60 if quick else 150
                    log(f"[P1b] seed scan: {sum(1 for z in sc_s if z[0] < 2000)} of {len(seeds)} volleys bring the "
                        f"Barrier; best cost {sc_s[0][0]:.2f} with {ov_seed['fires'][-1]}")
                else:
                    log(f"[P1b] seed scan: none of {len(seeds)} volleys brings the Barrier")
            ovb2, bc, t = climb(eng, ckb, ov_seed, nb, bcost,
                                mutator(ckb.i, spawn, aims=("Down", "Down", "Up"), demand=dem),
                                n_it, "P1b", patience=420, good_enough=1999.99, after_good=40,
                                fire=FM, press_w=0.01 if dem else 0.0)
            bc = int(bc)                    # the cost carries 0.01 per B press behind the point (rule v2)
            if bc < 2000 and ckb.i + bc <= spawn + 6:
                log(f"P1b: Barrier taken; guardian spawn at row {ckb.i + bc} (was {spawn})")
                spawn = ckb.i + bc
                ck, _ = eng.commit(ckb, gen(ckb.pad, ckb.i, bc + 1, ovb2, fire=FM)[0])
                ov = ovb2
                bar = 1
            else:
                log(f"P1b: no cheap Barrier (best cost {bc}); going on without it")
        rep["events"]["guardian_spawn"] = spawn
        rep["barrier_taken"] = bool(bar)
        log(f"P1 done: guardian spawns at row {spawn}; Barrier {'taken' if bar else 'NOT taken'} ({time.time() - t0:.0f}s)")
        ck, _ = eng.commit(root, ck.rows, keep=f"s8/{tagn}_p1")

        # ---- P2: the guardian, one jump at a time from 80 rows before its spawn
        cke, _ = eng.commit(root, ck.rows[:spawn - 80])
        cke.pad.reserve = plan((spawn + 232 + TRIG_AFTER_KILL, RES_HEART))      # this fight's own reserve is released
        rep["B_room_at_guardian_fight"] = list(cke.pad.room("B"))
        log(f"P2: B presses that fit each window at the fight's first row ({cke.i}): {rep['B_room_at_guardian_fight']}")
        ck = beam_boss(eng, cke, weapon, "guardian", spawn, quick) if beam else None
        if ck is None:
            ck = greedy_fight(eng, cke, weapon, GUARDIAN, "P2", first_land_after=spawn - 6, first_credit=45)
        kill = ck.i - 1
        rep["events"]["guardian_dead"] = kill
        rep["guardian_beam"] = getattr(ck, "info", None)
        log(f"P2: guardian HP 0 at row {kill} ({kill - spawn} after its spawn) ({time.time() - t0:.0f}s)")
        ck, _ = eng.commit(root, ck.rows, keep=f"s8/{tagn}_p2")
        ck.pad.reserve = plan((kill + TRIG_AFTER_KILL, RES_HEART))
        ov = new_ov()

        # the wall opens about 70 frames later: pick the jump that gets through first
        # (rule v2 pass: every row is tried and the horizon ends before the next terrain jump at world X 799. A
        # jump that is near its top when the wall goes lets Bill start 2 rows sooner than from the floor; with
        # the old 260-row horizon exactly those candidates reached the pit beyond and were thrown out.)
        cands = [ov] + [ov_add(ov, jumps=ck.i + d) for d in range(0, 104, 1)]

        def wall_eval(cs, n_=190):
            trs_ = eng.sims(ck, [gen(ck.pad, ck.i, n_, c, fire=FM)[0] for c in cs])
            out_ = []
            for c, t in zip(cs, trs_):
                fi, _k = fail_index(t, weapon, stall_ok=gexists)
                out_.append((fi is None and not t[-1]["jump"] and not t[-1]["edge"],
                             hpos(t[-1]) if fi is None else 0, c, fi, hpos(t[min(len(t) - 1, 130)])))
            return out_
        sc = wall_eval(cands)
        if not any(z[0] for z in sc):
            # something behind the wall stops every line (the M capsule's item, opened during the fight): a
            # second jump just before each line's failure
            top = sorted((z for z in sc if z[3] is not None and z[3] > 20), key=lambda z: -z[4])[:24]
            c2 = [ov_add(c, jumps=ck.i + fi - q) for _ok, _p, c, fi, _p130 in top for q in (2, 4, 7, 11)]
            log(f"[P2] wall: every single jump fails within 190 rows; trying {len(c2)} lines with a second jump")
            sc += wall_eval(c2, 215)
        sc.sort(key=lambda z: (z[0], z[1]), reverse=True)
        log(f"[P2] wall: best progress {sc[0][1]} with jumps {sc[0][2]['jumps']}; no jump {[z[1] for z in sc if z[2] is ov]}")
        if sc[0][0]:
            ov = sc[0][2]

        # ---- P3: to the heart's auto-scroll
        ck, ov = run_phase(eng, ck, lambda s: s["auto0"] > 0, weapon, ov=ov, name="P3", stall_ok=gexists,
                           hints=HINTS_P3, fire=FM)
        trig = ck.i
        rep["events"]["boss_scroll"] = trig
        ck, _ = eng.commit(root, ck.rows, keep=f"s8/{tagn}_p3")
        log(f"P3 done: boss auto-scroll starts at row {trig} ({time.time() - t0:.0f}s)")

        # ---- P4: the heart (created 48 frames into the scroll), one jump at a time from 80 rows before the scroll
        ckh, _ = eng.commit(root, ck.rows[:trig - 80])
        ckh.pad.reserve = ()
        rep["B_room_at_heart_fight"] = list(ckh.pad.room("B"))
        log(f"P4: B presses that fit each window at the fight's first row ({ckh.i}): {rep['B_room_at_heart_fight']}")
        ck = beam_boss(eng, ckh, weapon, "heart", trig, quick) if beam else None
        if ck is None:
            ck = greedy_fight(eng, ckh, weapon, HEART, "P4", first_land_after=trig + 30, heart=True, first_credit=45)
        dead = ck.i - 1
        rep["events"]["heart_dead_flag"] = dead
        rep["heart_beam"] = getattr(ck, "info", None)
        log(f"P4: boss flag at row {dead} ({dead - trig} after the scroll trigger) ({time.time() - t0:.0f}s)")
        ck, _ = eng.commit(root, ck.rows, keep=f"s8/{tagn}_p4")
        ovh = new_ov()

        # ---- P5: stay alive (the spiders live about 100 more frames), no firing (every bullet during the
        # explosions makes lag), on the ground with Down held when control is taken away
        from contra.stages.s3_boss import survive_cands
        best = None
        for hold_from in (110, 140, 60):
            try:
                ov5 = new_ov()
                ov5["holds"].append((ck.i + hold_from, ck.i + 600, "Down"))
                ck5, _o = run_phase(eng, ck, lambda s: s["lroutine"] == 9, weapon, ov=ov5, name="P5",
                                    stall_ok=lambda s: True, base=(), fire=False, cand_fn=survive_cands,
                                    progress=lambda s: 0, H=320)
            except RuntimeError as ex:
                log(f"P5: Down from +{hold_from}: {ex}")
                continue
            rows5 = ck5.rows[ck.i:] + [("Down",)] * 3
            t = eng.sim(ck, rows5)
            a, pidx = end_index(t)
            if a is None or pidx is None or any(z["death"] & 1 for z in t[:pidx + 1]):
                continue
            sc = (pidx, 0 if t[a]["pad"] & 0x0C else 1)
            if best is None or sc < best[0]:
                best = (sc, "Down", hold_from, (), rows5, t, a, pidx)
            if t[a]["pad"] & 0x0C and pidx == a + 1:
                break
        if best is None:
            raise RuntimeError("no safe ending found")
        sc, hold, d0, extra, rows, t, a, pidx = best
        log(f"P5: {hold} held from +{d0}: control lost at +{a}, standing pose at +{pidx}, "
            f"Up/Down held at A: {bool(t[a]['pad'] & 12)}; lag in the ending {sum(1 for z in t[:pidx] if z['lagged'])}")
        allrows = ck.rows + rows[:pidx + 1]
        P = t[pidx]["frame"]
        rep["events"]["control_lost_A"] = ck.i + a
        rep["events"]["END_P"] = ck.i + pidx
        rep["END_frame"] = P
        rep["frames_L_to_END"] = P - L
        rep["rows"] = len(allrows)
        rep["up_or_down_held_at_A"] = bool(t[a]["pad"] & 12)
        rep["weapon_out"] = t[pidx]["weapon"]
        rep["wall_seconds"] = round(time.time() - t0)
        return allrows, rep
    finally:
        if own:
            eng.close()


def verify(state, rows, eng=None, trace_out=None):
    """Replay rows open-loop from the state on one emulator: END frame, lag frames, ignored-pad frames, deaths.
    trace_out: a list that receives the replay's per-row trace (for press_report)."""
    own = eng is None
    eng = eng or Engine(1, tag="s8")
    try:
        ck = eng.root(state)
        t = eng.sim(ck, list(rows) + [()] * 3)
        if trace_out is not None:
            trace_out.extend(t)
        L = next(s["frame"] for s in t if s["lroutine"] == 4)
        a, pidx = end_index(t)
        lag = [k for k, s in enumerate(t[:len(rows)]) if s["lagged"]]
        ign = [k for k, s in enumerate(t[:len(rows)]) if not s["lagged"] and s["lroutine"] in (4, 8)
               and s["pad"] != to_mask(rows[k])]
        deaths = sum(1 for k in range(1, len(t)) if t[k]["death"] & 1 and not t[k - 1]["death"] & 1)
        return {"L": L, "A_frame": None if a is None else t[a]["frame"],
                "END_frame": None if pidx is None else t[pidx]["frame"],
                "frames_L_to_END": None if pidx is None else t[pidx]["frame"] - L, "lag_frames": lag,
                "ignored_pad_frames": ign, "deaths": deaths, "held_at_A": None if a is None else t[a]["pad"],
                "bossdef_row": first(t, lambda s: s["bossdef"] == 1), "weapon_out": t[-1]["weapon"]}
    finally:
        if own:
            eng.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return type(default)(v)
        return default
    out = opt("--out", "s8/run")
    emus = opt("--emus", 3)
    prior = opt("--prior", "")
    quick = "--quick" in args
    if quick:
        args.remove("--quick")
    nobar = "--nobarrier" in args
    if nobar:
        args.remove("--nobarrier")
    nobeam = "--nobeam" in args
    if nobeam:
        args.remove("--nobeam")
    metro = "--metronome" in args           # the first run's firing (B at the legal cadence), under the budget
    if metro:
        args.remove("--metronome")
    # rule v2: the sustained limits (a parameter; the default is the rule's) and the REAL press history: every
    # press of the last 1,800 rows before the stage counts
    windows = s3s8_lib.set_windows(s3s8_lib.parse_windows(opt("--windows", "600:109,1800:246")))
    state = args[0] if args else "dbg/s8_pre"
    pr = s3s8_lib.history_tail(read_inputs(prior)) if prior else []
    rows, rep = solve(state, out, emus, pr, quick=quick, barrier=not nobar, beam=not nobeam,
                      fire=True if metro else "demand")
    bad = check_rows(rows, pr)
    rep["input_rule_violations"] = len(bad)
    vt = []
    v = verify(state, rows, trace_out=vt)
    rep["verify"] = v
    rep["presses"] = press_report(rows, vt, rep["events"], pr)
    save_segment(out, rows, {"state": state, "stage": 8, "frames_L_to_END": rep["frames_L_to_END"]})
    # the project's own checker on history + segment, with the sustained limits
    import check_inputs as CI
    from contra.inputs import write_inputs
    both = LOGS_DIR / f"{out}.withprior.inputs.txt"
    write_inputs(both, list(pr) + list(rows), f"history_tail={len(pr)} segment={len(rows)}")
    cr = CI.check(list(pr) + list(rows), windows=windows)
    rep["check_inputs_v2"] = {"file": str(both.relative_to(LOGS_DIR.parent)), "pass": cr["pass"],
                              "violations": {k: r["violations"] for k, r in cr["rules"].items()},
                              "B": cr["stats"]["B"]}
    (LOGS_DIR / f"{out}.report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    pz = rep["presses"]
    log(f"DONE: {len(rows)} rows, L to END {rep['frames_L_to_END']} frames (record 3273); replay check: "
        f"{v['frames_L_to_END']} frames, lag {len(v['lag_frames'])}, ignored pad {len(v['ignored_pad_frames'])}, "
        f"deaths {v['deaths']}; rule violations {len(bad)}")
    log(f"rule v2: B presses {pz['B_presses']}, most in any 600 rows {pz['B_max_in_600']}, in any 1800 "
        f"{pz['B_max_in_1800']} (history counted); sections {json.dumps(pz['sections'])}; check_inputs.py with "
        f"windows {windows} on history tail + segment: {'PASS' if cr['pass'] else 'FAIL'}")

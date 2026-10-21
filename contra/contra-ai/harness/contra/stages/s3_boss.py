"""Stage 3 after the climb: the jump that starts the boss scroll, the dragon, the exit, to stage 4's first frame.

Uses the open-loop engine (s3s8_engine.py) and the lookahead / jump-by-jump fight helpers of s8.py.

Plan (all of it found by simulation, nothing assumed about timing):
    T   the jump from the top floor that starts the boss scroll soonest
    A   both arms: the right hand is shot from below while it is still extending (it appears 131 frames after the
        scroll ends, HP 16), then the left hand while it swings. With both arms gone nothing rains on the floor
        and the mouth's closed gap drops from 222 to 62 frames. (The freeze of docs/Bugs.md #4 would show up as
        an endless lag streak; such candidates are thrown away.)
    W   wait for the mouth (first opening is a fixed count after the scroll and the palette fade)
    M   the mouth: 32 HP, open 112 frames; shot from jumps right under it (X 123), stepping aside for the
        fireball it drops straight down 6 frames after opening
    X   the exit: stand in the middle; the next stage's first frame decides
"""
from __future__ import annotations

import time

from .s3s8_lib import Pad
from .s3s8_engine import Engine, Ck, gen, new_ov, ov_add, find_slot, first
from .s8 import run_phase, greedy_fight, fail_index, log, trim

MOUTH, ARM, SOLDIER = 0x14, 0x15, 0x05
SLOTV = float(__import__("os").environ.get("S3_SLOTV", "0.01"))    # beam ranking: hits a bullet slot is worth per frame
X_MOUTH = 123        # facing right the muzzle is at X + 5 = the mouth's X
X_SAFE = 116         # nearest spot the mouth's centre fireball (straight down at X 128) misses
X_RIGHT_HAND = 181   # under the right hand while it extends from (184, 85)
X_LEFT_HAND = 50


def mouth_hp(s):
    """32 while the mouth is closed (its real HP is parked elsewhere), the HP byte while it is open."""
    k = find_slot(s, MOUTH)
    if k is None:
        return None
    h = s[f"h{k}"]
    if h >= 0xF0 or s[f"es{k}"] & 0x80:
        return 32
    return h


def mouth_open(s):
    k = find_slot(s, MOUTH)
    return k is not None and s[f"h{k}"] < 0xF0 and not (s[f"es{k}"] & 0x80)


def hands(s):
    """{"R"/"L": (slot, x, y, hp)} for the hittable hands (the outermost orb of each arm)."""
    out = {}
    for k in range(16):
        if s[f"r{k}"] and s[f"t{k}"] == ARM and 0 < s[f"h{k}"] < 0xF0:
            out["R" if s[f"ex{k}"] >= 128 else "L"] = (k, s[f"ex{k}"], s[f"ey{k}"], s[f"h{k}"])
    return out


def hand_hp(side, need_dead):
    """HP of one hand for the fight helper: None before the hands exist, 0 once `need_dead` arms are gone."""
    def f(s):
        if s["nbossdead"] >= need_dead:
            return 0
        h = hands(s).get(side)
        if h is None:
            return None
        return h[3]
    return f


def survive_cands(D, ov, level, kind):
    """Repairs for "stand still and wait": a jump, a short walk, a single shot, in the frames before a death."""
    out = []
    for d in range(2, 44, 3):
        out.append(ov_add(ov, jumps=D - d))
    for d in (6, 12, 20, 30, 45, 60):
        for k in (6, 12, 24, 48):
            out.append(ov_add(ov, holds=(D - d, D - d + k, "Left")))
            out.append(ov_add(ov, holds=(D - d, D - d + k, "Right")))
    for d in range(6, 70, 6):
        for dirb in ("Left", "Right"):
            o = ov_add(ov, holds=(D - d, D - d + 2, dirb))
            out.append(ov_add(o, holds=(D - d, D - d + 2, "B")))
    if level >= 1:
        for d in range(2, 60, 4):
            for d2 in (8, 16, 24):
                for dirb in ("Left", "Right"):
                    out.append(ov_add(ov_add(ov, jumps=D - d), holds=(D - d, D - d + d2, dirb)))
        for d in range(10, 100, 10):
            for dirb in ("Left", "Right"):
                o = ov
                for rep in range(3):
                    o = ov_add(o, holds=(D - d + 8 * rep, D - d + 8 * rep + 2, "B"))
                out.append(ov_add(o, holds=(D - d, D - d + 2, dirb)))
    if level >= 2:
        for d in range(2, 80, 5):
            for d2 in range(-50, 40, 10):
                out.append(ov_add(ov_add(ov, jumps=D - d), jumps=D + d2))
    return out


def trigger_jump(eng: Engine, ck: Ck, weapon):
    """From the top floor: the jump that starts the boss scroll soonest. Returns (ck on the trigger frame, info)."""
    cands = []
    for d in (0, 1, 2):
        for base in ((), ("Right",), ("Left",)):
            o = new_ov()
            o["jumps"].append(ck.i + d)
            cands.append((d, base, gen(ck.pad, ck.i, 70, o, base=base, fire=False)[0]))
    trs = eng.sims(ck, [c[2] for c in cands])
    best = None
    for (d, base, rows), t in zip(cands, trs):
        k = first(t, lambda s: s["auto0"] > 0)
        if k is None or any(s["death"] & 1 for s in t[:k + 1]):
            continue
        if best is None or k < best[0]:
            best = (k, d, base, rows)
    if best is None:
        raise RuntimeError("no jump starts the boss scroll")
    k, d, base, rows = best
    ck2, _ = eng.commit(ck, rows[:k + 1])
    return ck2, {"wait": d, "held": "+".join(base), "rows": k + 1}


def walk_to(eng: Engine, ck: Ck, weapon, xt: int, goal, name: str, face: str | None = None, H: int = 300):
    """Stand still / walk to screen X = xt (as soon as Bill is on the ground), repairing deaths, until goal(s).
    Returns (ck at the goal frame, ov)."""
    t = eng.sim(ck, [()] * 90)
    k = first(t, lambda s: not s["jump"] and not s["edge"] and s["pstate"] == 1)
    k = 0 if k is None else k
    x = t[k]["x"]
    ov = new_ov()
    dx = xt - x
    a = ck.i + k + 1
    turn = bool(face) and dx != 0 and ((face == "Right") != (dx > 0))
    if turn:
        dx += -2 if face == "Right" else 2        # overshoot by 2 and come back: Bill ends up facing `face`
    if dx:
        ov["holds"].append((a, a + abs(dx), "Right" if dx > 0 else "Left"))
    if turn:
        ov["holds"].append((a + abs(dx) + 2, a + abs(dx) + 4, face))
    return run_phase(eng, ck, goal, weapon, ov=ov, name=name, stall_ok=lambda s: True, base=(), fire=False,
                     cand_fn=survive_cands, progress=lambda s: 0, H=H)


def kill_arms(eng: Engine, ck: Ck, weapon, rep, start_ck: Ck):
    """Both hands. Returns (ck, number of arms gone)."""
    sck = Ck(start_ck.name, start_ck.i, start_ck.rows, start_ck.pad)
    # right hand: be under it before it can be hit, then jump-shoot from 70 rows before it appears
    ck, _ov = walk_to(eng, ck, weapon, X_RIGHT_HAND, lambda s: "R" in hands(s), "A-right", face="Right")
    appear = ck.i - 1
    rep["events"]["hands_appear"] = appear
    fallback = ck
    back, _ = eng.commit(sck, ck.rows[start_ck.i:appear - 70])
    try:
        ck = greedy_fight(eng, back, weapon, ARM, "A-right", base=(), hp_fn=hand_hp("R", 1), progs=(("U", "U", "U"),),
                          first_land_after=appear + 2, first_credit=30, hp_full=16, maxseg=8)
        rep["events"]["right_arm_dead"] = ck.i - 1
        log(f"A: right arm gone at row {ck.i - 1} ({ck.i - 1 - appear} after the hands appeared)")
    except RuntimeError as ex:
        log(f"A: right arm not killed ({ex}); going on with the arms alive")
        return fallback, 0
    # left hand
    try:
        ck2, _ov = walk_to(eng, ck, weapon, X_LEFT_HAND,
                           lambda s: not s["jump"] and not s["edge"] and abs(s["x"] - X_LEFT_HAND) <= 1, "A-walk",
                           face="Right")
        ck3 = greedy_fight(eng, ck2, weapon, ARM, "A-left", base=(), hp_fn=hand_hp("L", 2), progs=(("U", "U", "U"),),
                           hp_full=16, maxseg=16)
        rep["events"]["left_arm_dead"] = ck3.i - 1
        log(f"A: left arm gone at row {ck3.i - 1}")
        return ck3, 2
    except RuntimeError as ex:
        log(f"A: left arm not killed ({ex}); going on with one arm")
        return ck, 1


def beam_mouth(eng: Engine, ck0: Ck, weapon, M: int, quick: bool = False):
    """Second pass: the mouth by beam search (s3s8_fight.py) from 70 rows before it opens (row M). Choices per
    5-row layer: no press / a press on a legal row (aim Up), a step left or right between presses, the first
    jump's row (later jumps on landing). Bullet box of the mouth: collision code 3, X -16..+17, Y -16..+17 around
    (128, 63). Returns the checkpoint on the frame the boss flag / HP 0 shows, or None."""
    from .s3s8_fight import FightCfg, beam_fight

    def t_exist(s, row):
        return 0 if mouth_open(s) else max(1, M - row)

    def kill(s):
        return bool(s["bossdef"]) or (mouth_open(s) and mouth_hp(s) == 0)

    best = None
    z0 = eng.sim(ck0, [()])[0]
    x0, f0 = z0["x"], z0["frame"] - 1
    for xs in ((X_SAFE,) if quick else (X_SAFE, X_SAFE + 5, X_SAFE + 10)):
        # stand a little closer to the mouth's centre line (more pellets inside its box); the fireball it drops
        # straight down then has to be dodged to the left, which the beam may do from 25 rows after the opening
        pre = [("Right",) if k < xs - x0 else (("Left",) if k < x0 - xs else ()) for k in range(abs(xs - x0) + 1)]
        pp, prow = ck0.pad.copy(), []
        for r in pre:
            prow.append(pp.fix(r))
            pp.push(prow[-1])
        ckx, trp = eng.commit(ck0, prow) if xs != x0 else (ck0, [])
        if any(z["death"] & 1 for z in trp):
            continue
        cfg = FightCfg(typ=MOUTH, box=(-16, 17, -16, 17), hp_full=32, aims=("U",), base=(), W=8 if quick else 12,
                       weapon=weapon, name=f"mouth X{xs}", log=log, hp_fn=mouth_hp, kill_fn=kill, t_exist_fn=t_exist,
                       moves=lambda row: (None, "Left") if (row >= M + 25 and xs != X_SAFE) else (None,),
                       panic_moves=(None, "Left", "Right"), slot_value=SLOTV, strat_until=M + 20,
                       max_layers=60, jump_mode=lambda s, js: "asap" if js else ("free" if ck0.i + s["frame"] - f0 >= M - 45 else "none"))
        try:
            rows, info = beam_fight(eng, ckx, cfg, aim0="U")
        except RuntimeError as ex:
            log(f"[mouth] beam from X {xs} failed: {ex}")
            continue
        if best is None or info["kill_row"] < best[1]["kill_row"]:
            best = (ckx.rows[ck0.i:] + rows, info)
    if best is None:
        return None
    ck, _ = eng.commit(ck0, best[0])
    ck.dead = True
    return ck


def polish_mouth(eng: Engine, ck0: Ck, ck: Ck, weapon, iters: int = 300):
    """Second pass: hill climbing on the finished fight (the greedy's own overrides as the seed): single presses
    left out (fewer pellets = fewer lag frames, and a slot that is not wasted on a miss), jumps moved by a few
    rows, short steps. Cost = the row the boss flag / HP 0 shows; a death is disqualified. Returns the better
    checkpoint (or ck itself)."""
    from .s8 import climb
    ov = getattr(ck, "ov_used", None)
    if ov is None:
        return ck
    n = ck.i - ck0.i + 4
    kill0 = ck.i - 1 - ck0.i

    def cost(t):
        # the kill row; ties are broken by the HP summed over the rows (damage dealt sooner), which gives the
        # climb a slope to follow between two kill rows
        area = 0
        for k, z in enumerate(t):
            if z["death"] & 1 or z["pstate"] == 2 or z["weapon"] != weapon:
                return 10 ** 6
            if z["bossdef"] or (mouth_open(z) and mouth_hp(z) == 0):
                return k + area / 100000.0
            area += mouth_hp(z) or 32
        return 10 ** 5
    t = eng.sim(ck0, gen(ck0.pad, ck0.i, n, ov, base=())[0])
    if int(cost(t)) != kill0:
        log(f"[polish] the seed does not regenerate ({cost(t)} vs {kill0}); skipped")
        return ck
    lo, hi = ck0.i + 30, ck.i

    def mutate(o, rng):
        o = {k: list(v) for k, v in o.items()}
        r = rng.random()
        if r < 0.45:
            a = rng.randrange(lo, hi)
            o["nofire"].append((a, a + rng.choice((1, 2, 3, 4, 5, 6))))
        elif r < 0.65 and o["jumps"]:
            j = rng.choice(o["jumps"])
            o["jumps"].remove(j)
            o["jumps"].append(j + rng.choice((-4, -3, -2, -1, 1, 2, 3, 4)))
        elif r < 0.77:
            am = [z for z in o["nofire"] if z[0] >= lo]
            if am:
                o["nofire"].remove(rng.choice(am))
        elif r < 0.90:
            a = rng.randrange(lo, hi)
            o["holds"].append((a, a + rng.choice((2, 3, 4, 6)), rng.choice(("Left", "Right"))))
        else:
            am = [z for z in o["holds"] if z[0] >= lo and z[2] in ("Left", "Right")]
            if am:
                o["holds"].remove(rng.choice(am))
            else:
                a = rng.randrange(lo, hi)
                o["nofire"].append((a, a + 5))
        return o
    ov2, best, _t = climb(eng, ck0, ov, n, cost, mutate, iters, "polish", base=(), patience=iters)
    best = int(best)
    if best < kill0:
        ck2, _ = eng.commit(ck0, gen(ck0.pad, ck0.i, best + 1, ov2, base=())[0])
        ck2.dead = True
        log(f"[polish] dragon dead {kill0 - best} rows sooner (row {ck2.i - 1})")
        return ck2
    return ck


def solve_boss(eng: Engine, ck: Ck, weapon, tagn: str, quick: bool = False, arms: bool = False, beam: bool = False,
               polish: bool = True):
    """ck = standing on the top floor (row -108). Returns (rows of the whole segment, report dict)."""
    rep = {"events": {}}
    t0 = time.time()
    start_ck = ck
    ck, info = trigger_jump(eng, ck, weapon)
    rep["events"]["boss_scroll"] = ck.i - 1
    rep["trigger"] = info
    log(f"T: boss scroll starts at row {ck.i - 1} ({info})")
    sck = Ck(start_ck.name, start_ck.i, start_ck.rows, start_ck.pad)

    narms = 0
    if arms:
        ck, narms = kill_arms(eng, ck, weapon, rep, start_ck)
    rep["arms_killed"] = narms
    xm = X_MOUTH if narms == 2 else X_SAFE

    # ---- wait for the mouth, standing where the fight will be
    ck, ov = walk_to(eng, ck, weapon, xm, mouth_open, "W", face="Right")
    m_open = ck.i - 1
    rep["events"]["mouth_open"] = m_open
    log(f"W: mouth first open at row {m_open} ({m_open - rep['events']['boss_scroll']} after the scroll start) "
        f"({time.time() - t0:.0f}s)")

    # ---- the mouth, window by window: jump-by-jump greedy from 70 rows before each opening; while it is closed
    # nothing is fired (every bullet on this screen makes lag) and Bill only stays alive
    taps = [None, (0, 11), (0, 14), (2, 12), (4, 12), (8, 12)] if xm == X_MOUTH else [None]
    rows_now = ck.rows
    M = m_open
    rep["windows"] = []
    for win in range(1, 6):
        ck0, _ = eng.commit(sck, rows_now[start_ck.i:M - 70], keep=f"s3/{tagn}_m70" if win == 1 else None)

        def closed_again(z, i, M=M):
            return i > M + 40 and not mouth_open(z)
        ckb = beam_mouth(eng, ck0, weapon, M, quick) if (beam and win == 1) else None
        if ckb is not None:
            ck = ckb
            rep["windows"].append((win, M, ck.i - 1))
            break
        ck = greedy_fight(eng, ck0, weapon, MOUTH, f"M{win}", base=(), hp_fn=mouth_hp, heart=True,
                          progs=(("U", "U", "U"),), first_land_after=M + 4, first_credit=20, hp_full=32, maxseg=12,
                          taps=taps, stop_fn=closed_again)
        if getattr(ck, "dead", False):
            if polish:
                ck = polish_mouth(eng, ck0, ck, weapon, 120 if quick else 480)
            rep["windows"].append((win, M, ck.i - 1))
            break
        hp_left = eng.ram(ck)[0x5B8 + (find_slot(eng.sim(ck, [()])[0], MOUTH) or 0)]
        log(f"M: window {win} (opened at row {M}) ended at row {ck.i} with the mouth alive (parked HP {hp_left})")
        rep["windows"].append((win, M, None))
        ck, ov = run_phase(eng, ck, mouth_open, weapon, name=f"W{win + 1}", stall_ok=lambda z: True, base=(), fire=False,
                           cand_fn=survive_cands, progress=lambda z: 0, H=300)
        M = ck.i - 1
        rows_now = ck.rows
    else:
        raise RuntimeError("dragon: still alive after 5 windows")
    dead = ck.i - 1
    rep["events"]["boss_flag"] = dead
    log(f"M: dragon dead (flag) at row {dead}, {dead - m_open} after the mouth first opened ({time.time() - t0:.0f}s)")

    # ---- the exit: stand somewhere, wait for the scripted walk; the next stage's first frame decides
    # second pass: if Bill is in the air when the dragon dies, a direction held now would stay latched until he
    # lands; walk to the exit spot from the landing row instead
    t_idle = eng.sim(ck, [()] * 80)
    kl = next((k for k, z in enumerate(t_idle) if not z["jump"] and not z["edge"]), 0)
    xd = t_idle[kl]["x"]
    cands = []
    for xt in (xd, 104, 120, 128, 136, 152):
        dx = xt - xd
        o = new_ov()
        if dx:
            o["holds"].append((ck.i + kl + 1, ck.i + kl + 1 + abs(dx), "Right" if dx > 0 else "Left"))
        cands.append((xt, gen(ck.pad, ck.i, 1100, o, base=(), fire=False)[0]))
    trs = eng.sims(ck, [c[1] for c in cands])
    bestx = None
    for (xt, rows), t in zip(cands, trs):
        k = first(t, lambda z: z["level"] == 3 and z["lroutine"] == 4)
        a_ = first(t, lambda z: z["lroutine"] == 9)
        died = any(z["death"] & 1 for z in t[:(a_ or len(t))])
        rep.setdefault("exit_tests", []).append((xt, k, a_, died))
        if k is None or died:
            continue
        if bestx is None or k < bestx[0]:
            bestx = (k, xt, rows, a_, t)
    log(f"X: exit tests (stand X, rows to the next stage's first frame, rows to control lost, died): {rep['exit_tests']}")
    if bestx is None:
        raise RuntimeError("no exit reached the next stage")
    k, xt, rows, a_, t = bestx
    allrows = ck.rows + rows[:k]              # the row that produces the next stage's first frame is not ours
    rep["events"]["control_lost"] = ck.i + a_
    rep["events"]["next_stage_first_frame_row"] = ck.i + k
    rep["exit_x"] = xt
    rep["weapon_out"] = t[k]["weapon"]
    rep["lives_out"] = t[k]["lives"]
    return allrows, rep

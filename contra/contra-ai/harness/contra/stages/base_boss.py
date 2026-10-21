"""Beam search in the emulator for the two base bosses (boss screens use the outdoor bullet rules).

A beam member is an emulator snapshot; every `hold` frames each member tries every d-pad / jump choice while B is
pressed at the capped rhythm; members are ranked by a score built from the targets' HP minus the bullets already
on their way (straight-line prediction).
"""
from __future__ import annotations

import time

from . import base_plan as bp
from .base_common import Sess, bullets

DIRS = [(), ("Left",), ("Right",), ("Up", "Left"), ("Up", "Right")]
ACTIONS = [(d, j) for d in DIRS for j in (0, 1)]
PLATE = 0x0A


def run_action(S: Sess, act, hold, fire=True):
    """Hold the d-pad choice for `hold` frames (A on the first two when jumping), B at the capped rhythm.
    Returns (state, dead)."""
    d, j = act
    s = S.s
    for i in range(hold):
        row = list(d)
        if j and i < 2:
            row.append("A")
        if fire and (S.pad.len["B"] == 1 or (S.pad.len["B"] == 0 and S.pad.can_press("B"))):
            row.append("B")
        s = S.step(S.pad.fix(tuple(row)))
        if s["death"] & 1:
            return s, True
    return s, False


def beam(S: Sess, snap, score, done, max_layers=80, width=16, hold=4, actions=ACTIONS, sig=None, verbose=False,
         fire=True):
    """score(state) -> sortable (smaller is better); done(state) -> True when the goal is reached.
    Returns (snapshot at the goal, layers used) or (best snapshot, None)."""
    members = [(None, snap)]
    for layer in range(max_layers):
        cand = {}
        for _, sn in members:
            for act in actions:
                S.restore(sn)
                if act[1] and S.s["jump"]:
                    continue                    # already in the air: a jump choice changes nothing
                s, dead = run_action(S, act, hold, fire)
                if dead:
                    continue
                if done(s):
                    return S.snapshot(), layer + 1
                k = sig(s) if sig else (s["x"], s["y"], s["jump"])
                sc = score(s)
                if k not in cand or sc < cand[k][0]:
                    if k in cand:
                        S.free(cand[k][1])
                    cand[k] = (sc, S.snapshot())
        ranked = sorted(cand.values(), key=lambda v: v[0])
        for _, sn in ranked[width:]:
            S.free(sn)
        for _, sn in members:
            if sn is not snap:
                S.free(sn)
        members = ranked[:width]
        if verbose:
            print("  layer", layer, "best", members[0][0] if members else None, flush=True)
        if not members:
            return None, None
    return members[0][1], None


def _vel(s, i):
    vx = s[f"bvx{i}"] - (256 if s[f"bvx{i}"] >= 128 else 0) + s[f"bfx{i}"] / 256.0
    vy = s[f"bvy{i}"] - (256 if s[f"bvy{i}"] >= 128 else 0) + s[f"bfy{i}"] / 256.0
    return vx, vy


def incoming(s, targets, frames=18):
    """How many live bullets will enter each target's box in the next frames (straight-line prediction).
    targets: [(key, x, y, code, capacity, vx, t_open)] (vx = target's X speed, bouncing between 80 and 176;
    t_open = frames until it can be hit, bullets pass through before that) -> {key: n}."""
    cnt = {t[0]: 0 for t in targets}
    bl = []
    for i, sl, tm, rt, x, y in bullets(s):
        if rt == 1:
            vx, vy = _vel(s, i)
            bl.append([float(x), float(y), vx, vy, True])
    tg = [[key, float(ex), ey, code, cap, vx, op] for key, ex, ey, code, cap, vx, op in targets]
    for f in range(frames):
        for t in tg:
            if cnt[t[0]] >= t[4] or f < t[6]:
                continue
            for b in bl:                      # one bullet per target per frame
                if b[4] and bp.in_box(int(b[0]), int(b[1]), int(t[1]), t[2], t[3]):
                    b[4] = False
                    cnt[t[0]] += 1
                    break
        for b in bl:
            b[0] += b[2]
            b[1] += b[3]
        for t in tg:
            if t[5]:
                t[1] += t[5]
                if t[1] >= 176 or t[1] <= 80:
                    t[5] = -t[5]
    return cnt


def plates(s):
    return [(i, s[f"ex{i}"], s[f"ey{i}"], 10 if s[f"eh{i}"] >= 0xF0 else s[f"eh{i}"]) for i in range(16)
            if s[f"er{i}"] and s[f"et{i}"] == PLATE and s[f"eh{i}"] > 0]


def make_score(final_type, hp_field, hp_full, moving, ground_y=201):
    """Score for 'platings first, then the part of type final_type whose real HP is in ENEMY_VAR hp_field'."""

    def finals(s):
        return [i for i in range(16) if s[f"er{i}"] and s[f"et{i}"] == final_type]

    def score(s):
        ps = plates(s)
        if ps:
            inc = incoming(s, [(i, x, y, 2, hp, 0, 0) for i, x, y, hp in ps])
            eff = sum(max(0, hp - inc[i]) for i, x, y, hp in ps)
            raw = sum(hp for i, x, y, hp in ps)
            dist = min(abs(s["x"] - x) for i, x, y, hp in ps)
            return (0, eff, raw, dist)
        fs = finals(s)
        if not fs:
            return (1, 0, 0, 0)
        tg, wait = [], 0
        for i in fs:
            hp = s[f"{hp_field}{i}"] or hp_full
            if s[f"es{i}"] & 0x80:
                if s[f"er{i}"] == 2 and 0 < s[f"ed{i}"] <= 40:
                    # first appearance: becomes vulnerable when its delay runs out; bullets may be sent ahead
                    tg.append((i, s[f"ex{i}"], s[f"ey{i}"], 2, hp, 0, s[f"ed{i}"]))
                else:
                    wait += hp
            else:
                vx = (s[f"evx{i}"] - (256 if s[f"evx{i}"] >= 128 else 0) + s[f"efx{i}"] / 256.0) if moving else 0
                tg.append((i, s[f"ex{i}"], s[f"ey{i}"], s[f"ec{i}"] & 15, hp, vx, 0))
        if not tg:                               # nothing vulnerable soon: wait below a target
            xs = [s[f"ex{i}"] for i in fs]
            return (1, wait, wait, min(abs(s["x"] - x) for x in xs) + abs(s["y"] - ground_y))
        inc = incoming(s, tg, frames=40)
        eff = sum(max(0, t[4] - inc[t[0]]) for t in tg) + wait
        raw = sum(t[4] for t in tg) + wait
        dist = min(abs(s["x"] - (t[1] + t[5] * 12)) for t in tg)
        return (1, eff, raw, dist)

    return score


def solve_boss(S: Sess, final_type, hp_field, hp_full, moving, width=12, hold=4, max_layers=160, verbose=False):
    """From the boss room's first frame to the frame BOSS_DEFEATED_FLAG is set."""
    t0 = time.time()
    n0 = len(S.rows)
    while not (S.s["jump"] == 0 and S.s["y"] > 190) and len(S.rows) - n0 < 140:
        S.step(S.pad.fix(()))
    land = len(S.rows) - n0
    snapL = S.snapshot()
    score = make_score(final_type, hp_field, hp_full, moving, ground_y=S.s["y"])
    goal, layers = beam(S, snapL, score, lambda s: s["bossdef"] != 0, max_layers=max_layers, width=width, hold=hold,
                        verbose=verbose)
    if goal:
        S.restore(goal)
    return {"ok": layers is not None, "land": land, "frames": len(S.rows) - n0, "secs": round(time.time() - t0)}


def solve_exit(S: Sess):
    """After the boss: hold Left (the lift is on the left) until the next stage's first frame ($2C == 4)."""
    lvl = S.s["level"]
    n0 = len(S.rows)
    while not (S.s["level"] != lvl and S.s["lroutine"] == 4) and len(S.rows) - n0 < 1500:
        row = ("Left",) if S.s["level"] == lvl and S.s["lroutine"] in (4, 8) else ()
        S.step(S.pad.fix(row))
        if S.s["death"] & 1:
            return {"ok": False}
    return {"ok": S.s["level"] != lvl, "frames": len(S.rows) - n0}

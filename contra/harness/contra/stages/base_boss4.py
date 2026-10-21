"""Stage 4 boss: platings by beam search (base_boss), then the two helmets by a scripted attack whose few
parameters are searched in the emulator.

Helmet facts watched in the emulator (see knowledge/s4_notes.md): both become vulnerable 64 frames after the third
plating dies, for 32 frames; a helmet that is not being hit then splits and is invulnerable for about 223 frames
before a 48-frame window. Real HP 10 each in ENEMY_VAR_4. Standing under a helmet and jumping puts a tight
stream on it; a hit registered on the frame its timer runs out leaves it vulnerable while split (the known bug).
The search looks for attacks on the first helmet that also leave the second one in that state, and then tries
to finish the second one while it is split; it keeps whichever complete fight is shortest.
"""
from __future__ import annotations

import time

from . import base_boss as bb
from .base_common import Sess

HELMET = 0x1C


def helmets(s):
    """{slot: (x, hp, vulnerable, timer, routine)} for live helmets."""
    return {i: (s[f"ex{i}"], s[f"e4{i}"], (s[f"es{i}"] & 0x80) == 0, s[f"ed{i}"], s[f"er{i}"])
            for i in range(16) if s[f"er{i}"] and s[f"et{i}"] == HELMET}


def gone(h):
    return h is None or (h[4] >= 5 and h[1] == 0)


def attack(S: Sess, slot, x_target, W, tj, phase, limit, rejump=True, g=None):
    """Walk under x_target, jump at row W + tj, B every 5 frames with the given phase, jump again while the helmet
    can still be hit. Stops when the helmet in `slot` is gone, on death, or at row `limit`.
    Returns (row count at the kill | None, hp left)."""
    jumped = False
    while len(S.rows) < limit:
        s = S.s
        n = len(S.rows)
        h = helmets(s).get(slot)
        if gone(h):
            return n, 0
        row = []
        if not s["jump"]:
            if s["x"] < x_target - 1:
                row.append("Right")
            elif s["x"] > x_target + 1:
                row.append("Left")
        if S.pad.len["A"] == 1:
            row.append("A")
        elif (n >= W + tj and not s["jump"] and (not jumped or (rejump and h[2])) and abs(s["x"] - x_target) <= 3
              and S.pad.can_press("A")):
            row.append("A")
            jumped = True
        if g is not None and W + g - 55 <= n <= W + g:
            # hold fire so that five slots are free, then one full spray from the ground at exactly W + g: its
            # outer pellet is meant to reach the OTHER helmet on the frame that helmet's timer runs out
            if S.pad.len["B"] == 1 or (n == W + g and S.pad.can_press("B")):
                row.append("B")
        elif S.pad.len["B"] == 1 or (S.pad.len["B"] == 0 and S.pad.can_press("B") and (n - phase) % 5 == 0):
            row.append("B")
        s = S.step(S.pad.fix(tuple(row)))
        if s["death"] & 1:
            return None, 99
    h = helmets(S.s).get(slot)
    return None, (h[1] if h else 0)


def search_helmet(S: Sess, slot, other=None, xs=None, tjs=None, limit_after=150):
    """Try (x, jump time, B phase) for the helmet in `slot` from the current state.
    Returns (W row, [(kill row | None, hp left, other helmet left vulnerable?, (x, tj, phase))] sorted best first,
    snapshot the tries start from)."""
    snap = S.snapshot()
    n0 = len(S.rows)
    W = None
    while len(S.rows) < n0 + 420:                # when does it become vulnerable? (no fire, no movement)
        h = helmets(S.s).get(slot)
        if h is None:
            break
        if h[2]:
            W = len(S.rows)
            break
        if S.step(S.pad.fix(()))["death"] & 1:
            break
    S.restore(snap)
    if W is None:
        return None, [], snap
    hx = helmets(S.s)[slot][0]
    waiting = W > n0
    while len(S.rows) < W - 50:                   # common prefix: walk under it without firing
        s = S.s
        row = ("Right",) if s["x"] < hx - 1 else (("Left",) if s["x"] > hx + 1 else ())
        if S.step(S.pad.fix(row))["death"] & 1:
            S.restore(snap)
            break
    snap = S.snapshot()
    if xs is None:
        xs = [hx, hx - 4, hx + 4] if waiting else list(range(88, 177, 8))
    if tjs is None:
        tjs = list(range(-44, -3, 5)) if waiting else list(range(0, 41, 8))
    out = []
    for x in xs:
        for tj in tjs:
            for phase in range(5):
                S.restore(snap)
                kill, hp = attack(S, slot, x, W, tj, phase, W + limit_after)
                oth = False
                if kill is not None and other is not None:
                    while len(S.rows) < W + 37:           # past the end of the 32-frame window
                        if S.step(S.pad.fix(()))["death"] & 1:
                            break
                    ho = helmets(S.s).get(other)
                    oth = bool(ho and ho[2] and ho[1] > 0)
                out.append((kill, hp, oth, (x, tj, phase)))
    if other is not None and waiting and not any(r[2] for r in out):
        # no ordinary attack left the other helmet open: try the dedicated full spray from the ground
        for x in (hx, hx - 4, hx + 4):
            for g in range(-16, -1):
                for tj in (g + 2, g + 8):
                    for phase in range(5):
                        S.restore(snap)
                        kill, hp = attack(S, slot, x, W, tj, phase, W + limit_after, g=g)
                        oth = False
                        if kill is not None:
                            while len(S.rows) < W + 37:
                                if S.step(S.pad.fix(()))["death"] & 1:
                                    break
                            ho = helmets(S.s).get(other)
                            oth = bool(ho and ho[2] and ho[1] > 0)
                        if oth:
                            out.append((kill, hp, oth, (x, tj, phase, g)))
    out.sort(key=lambda r: (r[0] if r[0] is not None else 10 ** 6 + r[1] * 1000))
    return W, out, snap


def finish(S: Sess, n0, info):
    """Kill whatever helmets are left, one window at a time (right one first: the lift is on the left)."""
    for _ in range(4):
        hs = helmets(S.s)
        alive = [i for i, h in hs.items() if h[1] > 0 and h[4] < 5]
        if not alive or S.s["bossdef"]:
            break
        slot = max(alive, key=lambda i: hs[i][0])
        W, res, snap = search_helmet(S, slot)
        if W is None or not res:
            return False
        kill, hp, _, par = res[0]
        S.restore(snap)
        attack(S, slot, par[0], W, par[1], par[2], W + 150)
        info["helmets"].append({"slot": slot, "W": W - n0, "kill": (kill - n0) if kill else None, "hp_left": hp,
                                "params": par})
    for _ in range(12):
        if S.s["bossdef"]:
            break
        S.step(S.pad.fix(()))
    return bool(S.s["bossdef"])


def solve_boss(S: Sess, width=12, hold=4, verbose=False, try_glitch=2, **_):
    t0 = time.time()
    n0 = len(S.rows)
    while not (S.s["jump"] == 0 and S.s["y"] > 190) and len(S.rows) - n0 < 140:
        S.step(S.pad.fix(()))
    land = len(S.rows) - n0
    snapL = S.snapshot()
    score = bb.make_score(HELMET, "e4", 10, False, ground_y=S.s["y"])
    goal, layers = bb.beam(S, snapL, score, lambda s: s["plates"] >= 3, max_layers=int(360 / hold), width=width, hold=hold)
    if layers is None:
        return {"ok": False, "land": land, "why": "platings", "frames": len(S.rows) - n0}
    S.restore(goal)
    info = {"land": land, "plates_done": len(S.rows) - n0, "helmets": []}
    hs = helmets(S.s)
    first = max(hs, key=lambda i: hs[i][0])
    second = min(hs, key=lambda i: hs[i][0])
    W, res, snap = search_helmet(S, first, other=second)
    if W is None or not res:
        return {"ok": False, "land": land, "why": "first helmet", "frames": len(S.rows) - n0}
    results = []                                   # (total rows, final snapshot, info)
    cands = [res[0]] + [r for r in res if r[2] and r[0] is not None][:try_glitch]
    for kill, hp, oth, par in cands:
        S.restore(snap)
        attack(S, first, par[0], W, par[1], par[2], W + 150, g=par[3] if len(par) > 3 else None)
        inf = {"land": land, "plates_done": info["plates_done"],
               "helmets": [{"slot": first, "W": W - n0, "kill": (kill - n0) if kill else None, "hp_left": hp,
                            "params": par, "other_left_open": oth}]}
        if oth and kill is not None:
            # the second helmet is split but still vulnerable: try to finish it before it closes
            W2, res2, snap2 = search_helmet(S, second, limit_after=140)
            if W2 is not None and res2 and res2[0][0] is not None:
                S.restore(snap2)
                attack(S, second, res2[0][3][0], W2, res2[0][3][1], res2[0][3][2], W2 + 150)
                inf["helmets"].append({"slot": second, "W": W2 - n0, "kill": res2[0][0] - n0, "params": res2[0][3],
                                       "while_split": True})
            else:
                S.restore(snap2)
        if finish(S, n0, inf):
            results.append((len(S.rows), S.snapshot(), inf))
    if not results:
        return {"ok": False, "land": land, "why": "helmets", "frames": len(S.rows) - n0}
    results.sort(key=lambda r: r[0])
    S.restore(results[0][1])
    info = results[0][2]
    info["tried"] = [(r[0] - n0, [h.get("while_split", False) for h in r[2]["helmets"]]) for r in results]
    info.update(ok=True, frames=len(S.rows) - n0, secs=round(time.time() - t0))
    return info

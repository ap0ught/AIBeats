"""Closed-loop execution of a planned Waterfall climb (contra/stages/s3_plan.py nodes) in the emulator.

One node = walk frames + the A frame + airborne frames, as predicted by the model. The executor sends the rows a
frame at a time, repeats a row when the frame was a lag frame (the game did not run its logic), and compares the
landing state (X, Y, $94, A) with the model's. Firing is laid over the movement rows per node:
    mode = (fire, hold, vert)   fire: B at the legal cadence; hold: keep the direction button down through each
                                run (aim follows the movement) instead of 2 frames; vert: None / "Up" / "Down"
None of this changes the movement the model predicts (Up/Down do not move Bill; a held direction equals the latch).
"""
from __future__ import annotations

from .s3s8_lib import Game, R
from .s3_plan import Node, ds_dir

MODES = [(False, False, None), (True, False, "Up"), (True, True, "Up"), (True, True, None), (True, False, None),
         (True, True, "Down"), (True, False, "Down")]


def A_of(r: R) -> int:
    return r.screen * 240 + r.scroll


def node_rows(n: Node, hold: bool = False):
    """Movement rows for parent -> n. hold=False: each run's button is down on its first two frames only.
    hold=True: down for the whole run, but released 3 frames before the predicted landing."""
    rows = []
    wd = "Right" if n.walk > 0 else "Left"
    for _ in range(abs(n.walk)):
        rows.append((wd,))
    if n.ds0 == 0:
        rows.append(("A",))
        prev, run = 0, 0
    else:
        d0 = ds_dir(n.ds0)
        rows.append((("Right" if d0 > 0 else "Left"), "A"))
        prev, run = d0, 0                      # the latch is only set in the air: hold 2 more frames
    nd = len(n.dirs)
    for i, d in enumerate(n.dirs):
        if d == 0:
            rows.append(())
            continue
        if d != prev:
            prev, run = d, 0
        run += 1
        b = ("Right",) if d > 0 else ("Left",)
        if run <= 2 or (hold and i < nd - 3):
            rows.append(b)
        else:
            rows.append(())
    return rows


def play_node(g: Game, n: Node, mode=(False, False, None), check: bool = True, weapon: int | None = None,
              poke_inv: bool = False):
    """Play one node from the current emulator state (standing where n.parent says). Returns (status, r):
    status: "ok", "dead", "mismatch" (landing differs from the model), "weapon", "nojump"."""
    fire, hold, vert = mode
    rows = node_rows(n, hold)
    r = g.r
    i = 0
    guard = 0
    airborne_seen = False
    while i < len(rows):
        guard += 1
        if guard > len(rows) + 40:
            return "mismatch", r
        base = rows[i]
        want = set(base)
        if vert:
            if not (vert == "Down" and "A" in base and not ("Left" in base or "Right" in base)):
                want.add(vert)
        if fire:
            p = g.pad
            if p.down["B"]:
                if p.t - p.start["B"] < 2:
                    want.add("B")
            elif p.can_press("B"):
                want.add("B")
        if poke_inv:
            g.e.poke(0xAE, 100)
        pj = r.jump
        r = g.step(want)
        if r.dead or r.pstate != 1:
            return "dead", r
        if weapon is not None and r.weapon != weapon:
            return "weapon", r
        if r.lagged:
            continue                                   # the game did not see this row: send it again
        if "A" in base and not (r.jump & 15):
            # the press was not seen (ignored-controller frame): the A row is sent again
            if guard > len(rows) + 30:
                return "nojump", r
            continue
        i += 1
    if check:
        if r.airborne:
            # a late landing: give it a few frames
            for _ in range(3):
                r = g.step(())
                if not r.airborne:
                    break
        if (r.x, r.y, r.sub, A_of(r)) != (n.X, n.Y, n.sub, n.A) or r.airborne:
            return "mismatch", r
    return "ok", r


def wait_frames(g: Game, n: int, mode=(False, False, None), weapon=None, poke_inv=False):
    """Stand still for n frames (firing per mode). Returns (status, r)."""
    fire, hold, vert = mode
    r = g.r
    k = 0
    while k < n:
        want = set()
        if vert == "Up":
            want.add("Up")
        if fire:
            p = g.pad
            if p.down["B"]:
                if p.t - p.start["B"] < 2:
                    want.add("B")
            elif p.can_press("B"):
                want.add("B")
        if poke_inv:
            g.e.poke(0xAE, 100)
        r = g.step(want)
        if r.dead or r.pstate != 1:
            return "dead", r
        if weapon is not None and r.weapon != weapon:
            return "weapon", r
        if not r.lagged:
            k += 1
    return "ok", r


def climb(g: Game, nodes, weapon=0x13, modes=None, delays=(0, 1, 2, 3, 5, 8, 13, 21), log=print, poke_inv=False,
          back=3, budget=4000):
    """Play nodes[1:] (nodes[0] = where Bill stands now). For each node try (delay, mode) options until the
    landing matches the model; when a node cannot be passed, go back up to `back` nodes and take the next option
    there. Returns (index of the last node reached, list of (delay, mode index) used per node)."""
    modes = modes or list(range(len(MODES)))
    opts = [(d, m) for d in delays[:1] for m in modes] + [(d, m) for d in delays[1:] for m in modes[:3]]
    snaps = {0: g.snap()}
    choice = {}
    k = 1
    tried = 0
    deepest = 0
    while k < len(nodes):
        nd = nodes[k]
        start = choice.get(k, -1) + 1
        ok = False
        for oi in range(start, len(opts)):
            d, m = opts[oi]
            g.restore(snaps[k - 1])
            tried += 1
            st = "ok"
            if d:
                st, r = wait_frames(g, d, MODES[m], weapon, poke_inv)
            if st == "ok":
                st, r = play_node(g, nd, MODES[m], weapon=weapon, poke_inv=poke_inv)
            if st == "ok":
                choice[k] = oi
                ok = True
                break
            if tried > budget:
                break
        if ok:
            if k in snaps:
                g.free(snaps[k])
            snaps[k] = g.snap()
            if k > deepest:
                deepest = k
                if log and (opts[choice[k]] != (0, modes[0])):
                    log(f"  node {k} (row {nd.q}): passed with delay {opts[choice[k]][0]}, mode {opts[choice[k]][1]}")
            k += 1
            continue
        if tried > budget:
            log and log(f"  budget exhausted at node {k}")
            break
        # back up
        choice.pop(k, None)
        k -= 1
        if k < 1 or deepest - k >= back:
            log and log(f"  cannot pass node {deepest + 1} (row {nodes[min(deepest + 1, len(nodes) - 1)].q})")
            k = deepest + 1
            break
        log and log(f"  node {k + 1} failed with every option: back to node {k}, next option")
    # leave the emulator at the deepest node reached
    last = min(k - 1, len(nodes) - 1) if k <= len(nodes) else len(nodes) - 1
    last = max(last, 0)
    while last not in snaps and last > 0:
        last -= 1
    g.restore(snaps[last])
    used = [opts[choice[i]] if i in choice else None for i in range(1, last + 1)]
    return last, used

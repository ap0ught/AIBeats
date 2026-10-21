"""Beam search for a boss fight with Spread under the press cap (stage 3 dragon, stage 8 guardian and heart).

Why a beam: the damage rate is limited by the 10 bullet slots, not by the press rate. A slot is busy for the
pellet's flight + 7 frames after its hit (or until it leaves the screen after a miss), so WHEN each press is made
(Bill's height in the jump, the aim) decides how many of its 5 pellets exist, hit, and how soon their slots return.
The search therefore decides, for every 5-row layer: no press, or a press on one of the legal rows with one of the
aims; jumps are taken as soon as Bill lands ("asap") or are a choice per layer ("free", used on the approach).
Every candidate is played in the emulator from its parent's savestate; nothing is modelled except the ranking
credit for pellets still in flight (straight-line prediction from the bullet RAM against the boss's bullet box).

    cfg = FightCfg(...); rows, info = beam_fight(eng, ck, cfg)       # rows after ck up to the kill row (inclusive)
"""
from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, field

from .s3s8_lib import Pad
from .s3s8_engine import pellets_born

AIM_BTN = {"UR": ("Up",), "R": (), "U": ("Up",), "DR": ("Down",), "UL": ("Up",), "L": ()}


@dataclass
class FightCfg:
    typ: int                               # enemy type of the boss slot
    box: tuple                             # bullet box relative to the boss position: (dx0, dx1, dy0, dy1) inclusive
    hp_full: int = 103
    virt: tuple | None = None              # (scroll position at which the boss appears, its X then, its Y, scroll stop pos)
    aims: tuple = ("UR", "R")
    base: tuple = ("Right",)
    W: int = 20
    T: int = 5
    weapon: int = 0x13
    max_layers: int = 90
    jump_mode: object = None               # f(state) -> "asap" | "free" | "none"
    hp_fn: object = None                   # f(state) -> hp or None (default: slot of type typ)
    kill_fn: object = None                 # f(state) -> True when the fight is over (default: hp == 0)
    alive_fn: object = None                # extra validity test f(state) -> bool
    free_offsets: tuple = (0,)             # A offsets tried per layer in "free" mode
    panic_moves: tuple = ()                # moves offered after a wipe-out (dodging)
    slot_value: float = 0.0                # hits one bullet slot is worth per frame (10 slots: about rate / 10)
    moves: tuple = (None,)                 # extra direction held on the rows without a B press: None / "Left" / "Right"
    t_exist_fn: object = None              # f(state, row) -> frames until the existing boss slot can be hit (0 = now)
    strat_until: int | None = None         # absolute row up to which the beam is stratified by the first jump(s)
    strat_jumps: int = 1                   # how many leading jumps make a stratum
    name: str = "fight"
    log: object = print
    stop_fn: object = None                 # f(state, row) -> True: stop the beam here and return the best node
    aim_dir: dict = field(default_factory=dict)   # aim -> base override, e.g. {"U": ()} to stand still
    first_jump_rows: tuple | None = None   # "free" mode: the only rows on which a jump may start (None = any)


def _slot(s, typ):
    for k in range(16):
        if s[f"r{k}"] and s[f"t{k}"] == typ:
            return k
    return None


def _hp(s, typ):
    k = _slot(s, typ)
    return None if k is None else s[f"h{k}"]


def _s8(v):
    return v - 256 if v >= 128 else v


def pending_hits(m, bx, by, box, scroll_left=0, t_exist=0, horizon=48):
    """Number of flying pellets that a straight-line prediction puts inside the boss box (boss at bx, by now;
    during a scroll both the boss and the bullets lose 1 px per frame, so the relative motion is the bullet's own
    velocity). One hit per frame at most. Returns (count, busy slots)."""
    dx0, dx1, dy0, dy1 = box
    wins = []
    busy = 0
    miss_t = 0          # slot-frames that pellets predicted to miss will still occupy
    for s in range(10):
        if not m[0x388 + s]:
            continue
        busy += 1
        if m[0x438 + s] != 1:
            continue
        x, y = m[0x3C8 + s], m[0x3B8 + s]
        vx = _s8(m[0x408 + s]) + m[0x3E8 + s] / 256.0
        vy = _s8(m[0x3F8 + s]) + m[0x3D8 + s] / 256.0
        ent = None
        ext = None
        t_out = horizon
        for t in range(0, horizon):
            px, py = x + vx * t, y + vy * t
            sx = px - min(t, scroll_left)
            if t > 0 and (sx < 5 or sx >= 251 or py < 5 or py >= 232):
                t_out = t
                break
            if t >= t_exist and bx + dx0 <= px <= bx + dx1 and by + dy0 <= py <= by + dy1:
                if ent is None:
                    ent = t
                ext = t
            elif ent is not None:
                break
        if ent is not None:
            wins.append((ent, ext, t_out))
        else:
            miss_t += t_out
    wins.sort()
    last = -1
    n = 0
    hit_t = 0           # slot-frames the predicted hits still occupy (flight + the 7 frames after the hit)
    for ent, ext, t_out in wins:
        t = max(ent, last + 1)
        if t <= ext:
            n += 1
            last = t
            hit_t += t + 7
        else:
            miss_t += t_out
    return n, busy, hit_t, miss_t


@dataclass
class Node:
    name: str
    i: int                 # absolute row index of the segment at this node
    rows: list             # rows since the beam's start
    pad: Pad
    aim: str
    last: dict             # last trace state
    jumps: tuple = ()
    next_jump: int | None = None
    score: float = 0.0
    hp: int = 0
    np: int = 0            # B presses since the beam's start (rule v2: the fewer the better at equal damage)


def _child_rows(n: Node, cfg: FightCfg, o, aim, J, move=None):
    p = n.pad.copy()
    rows = []
    for k in range(cfg.T):
        r = n.i + k
        a = aim if (o is not None and k >= o) else n.aim
        want = set(cfg.aim_dir.get(a, cfg.base))
        if a in ("UL", "L"):
            want.discard("Right")
            want.add("Left")
        want.update(AIM_BTN[a])
        press = o is not None and k in (o, o + 1)
        if move and not press and not p.must_hold("B"):
            want.add(move)
        if press:
            want.add("B")
        if r in J or (r - 1) in J:
            want.add("A")
        row = p.fix(want)
        p.push(row)
        rows.append(row)
    return rows, p


def beam_fight(eng, ck, cfg: FightCfg, aim0: str = "R"):
    """Beam from checkpoint ck. Returns (rows from ck to the kill row inclusive, info dict)."""
    log = cfg.log
    hp_fn = cfg.hp_fn or (lambda s: _hp(s, cfg.typ))
    kill_fn = cfg.kill_fn or (lambda s: hp_fn(s) == 0)
    uid = f"{id(cfg) & 0xFFFF:04x}{int(time.time()) & 0xFFF:03x}"
    t0 = time.time()
    root_last = None
    e = eng.q.get()
    try:
        root_last = dict(e.load(ck.name))
    finally:
        eng.q.put(e)
    beam = [Node(ck.name, ck.i, [], ck.pad.copy(), aim0, root_last)]
    frames = 0
    best_kill = None
    stats = {"layers": 0, "children": 0}

    def ground(s):
        return not s["jump"] and not s["edge"]

    panic = {"n": 0, "until": -1}
    history = []

    def mode_of(s, jumps=(), row=None):
        if row is not None and row < panic["until"]:
            return "free"
        return cfg.jump_mode(s, jumps) if cfg.jump_mode else "asap"

    def evaluate(n: Node, e, J, variants):
        """Run every (o, aim) child of n with jump rows J on emulator e. Returns list of result dicts."""
        out = []
        base_sig = {}
        for (o, aim, mv) in variants:
            rows, p = _child_rows(n, cfg, o, aim, J, mv)
            pressed = 0
            if o is not None:
                # rule v2: the Pad may have refused the press (5-frame rule, press budget): that child is the
                # "no press" child with a pointless change of aim
                pressed = 1 if (o < len(rows) and "B" in rows[o] and p.start["B"] == n.pad.t + o) else 0
                if not pressed:
                    stats["refused"] = stats.get("refused", 0) + 1
                    continue
            e.mload(sid_of[id(e)])
            e.run(rows)
            tr = e.last_trace
            # every bullet slot's (active, routine) on every row of the layer: equal to the "no press" child's
            # means the press created no pellet
            sig = tuple((s[f"b{q}"], s[f"br{q}"]) for s in tr for q in range(10))
            if o is None:
                base_sig[mv] = sig
            elif pressed and o <= cfg.T - 2 and base_sig.get(mv) == sig:
                # rule v2: a press that created no pellet (no bullet slot was free) is pure waste under the
                # sustained limits: the game is where the "no press" child is, the Pad is worse off
                stats["wasted"] = stats.get("wasted", 0) + 1
                continue
            ok = True
            kill = None
            lagrun = 0
            for k, s in enumerate(tr):
                lagrun = lagrun + 1 if s["lagged"] else 0
                if s["death"] & 1 or s["pstate"] == 2 or s["weapon"] != cfg.weapon or lagrun >= 12 \
                        or (cfg.alive_fn and not cfg.alive_fn(s)):
                    ok = False
                    break
                if kill_fn(s):
                    kill = k
                    break
            if not ok:
                continue
            m = e.ram_all() if kill is None else None
            out.append({"o": o, "aim": aim if o is not None else n.aim, "rows": rows, "pad": p, "tr": tr, "kill": kill,
                        "m": m, "J": J, "np": n.np + pressed})
        return out

    sid_of = {}

    def expand(n: Node):
        e = eng.q.get()
        try:
            e.load(n.name)
            sid_of[id(e)] = e.msave()
            om = n.pad.wait_press("B")
            mvs = cfg.moves(n.i) if callable(cfg.moves) else cfg.moves
            if n.i < panic["until"] and cfg.panic_moves:
                mvs = cfg.panic_moves
            variants = [(o, a, mv) for mv in mvs
                        for (o, a) in [(None, n.aim)] + [(o, a) for o in range(om, cfg.T) for a in cfg.aims]]
            mode = mode_of(n.last, n.jumps, n.i)
            res = []
            Jsets = []
            base_J = set()
            if n.next_jump is not None and n.next_jump < n.i + cfg.T:
                base_J.add(n.next_jump)
            if mode == "free":
                Jsets = ([set()] + [{n.i + a} for a in cfg.free_offsets
                                    if cfg.first_jump_rows is None or (n.i + a) in cfg.first_jump_rows
                                    or n.i < panic["until"]]) if ground(n.last) else [set()]
            elif mode == "asap":
                if not base_J and ground(n.last):
                    base_J = {n.i}
                Jsets = [base_J]
            else:
                Jsets = [set()]
            for J in Jsets:
                r = evaluate(n, e, J, variants)
                if mode == "asap" and not J and r and r[0]["kill"] is None:
                    # landed inside this layer? then the jump goes on the row after the landing: run it again
                    k = next((k for k, s in enumerate(r[0]["tr"]) if ground(s)), None)
                    if k is not None and k + 1 < cfg.T:
                        r = evaluate(n, e, {n.i + k + 1}, variants)
                res.extend(r)
            e.mfree(sid_of[id(e)])
            return res
        finally:
            eng.q.put(e)

    def par(fn, items):
        out = [None] * len(items)
        errs = []

        def work(k):
            try:
                out[k] = fn(items[k])
            except Exception as ex:  # noqa: BLE001
                errs.append(ex)
        th = [threading.Thread(target=work, args=(k,)) for k in range(len(items))]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            raise errs[0]
        return out

    def cleanup():
        import glob
        import os
        from .s3s8_lib import STATES_DIR
        for f in glob.glob(str(STATES_DIR / eng.tag / "tmp" / f"fb_{uid}_*.State")):
            try:
                os.remove(f)
            except OSError:
                pass

    for layer in range(cfg.max_layers + 40):
        history.append(beam)
        results = par(expand, beam)
        cands = []
        kills = []
        for n, res in zip(beam, results):
            for c in res:
                stats["children"] += 1
                frames += cfg.T
                if c["kill"] is not None:
                    kills.append((n.i + c["kill"], len(kills), n, c))
                    continue
                s = c["tr"][-1]
                hp = hp_fn(s)
                k = _slot(s, cfg.typ)
                pos = s["screen"] * 256 + s["scroll"]
                if k is not None:
                    bx, by = s[f"ex{k}"], s[f"ey{k}"]
                    t_exist = cfg.t_exist_fn(s, n.i + cfg.T) if cfg.t_exist_fn else 0
                elif cfg.virt:
                    bx, by = cfg.virt[1] + (cfg.virt[0] - pos), cfg.virt[2]
                    t_exist = max(0, cfg.virt[0] - pos)
                else:
                    bx, by, t_exist = 0, 0, 10 ** 6
                scroll_left = max(0, cfg.virt[3] - pos) if cfg.virt else 0
                pend, busy, hit_t, miss_t = pending_hits(c["m"], bx, by, cfg.box, scroll_left, t_exist)
                hpv = cfg.hp_full if hp is None else hp
                # a busy slot cannot carry a new pellet: every slot-frame is worth about slot_value hits
                c["score"] = round(hpv - pend + cfg.slot_value * (hit_t + miss_t), 2)
                c["hp"] = hpv
                c["busy"] = busy
                cands.append((c["score"], busy, c["np"], len(cands), n, c))
        if kills:
            kills.sort(key=lambda z: (z[0], z[3]["np"], z[1]))
            krow, _, n, c = kills[0]
            rows = n.rows + c["rows"][:c["kill"] + 1]
            log(f"[{cfg.name}] kill at row {krow} (layer {layer}, {stats['children']} children, "
                f"{frames} frames, {time.time() - t0:.0f}s); B presses {c['np']}, children dropped: "
                f"{stats.get('wasted', 0)} with a press that fired nothing, {stats.get('refused', 0)} refused by the Pad")
            cleanup()
            return rows, {"kill_row": krow, "layers": layer + 1, "children": stats["children"], "frames": frames,
                          "seconds": round(time.time() - t0), "presses": c["np"], "wasted_dropped": stats.get("wasted", 0),
                          "refused_dropped": stats.get("refused", 0)}
        if not cands:
            panic["n"] += 1
            if panic["n"] > 4 or len(history) < 2:
                cleanup()
                raise RuntimeError(f"{cfg.name}: every candidate died at row {beam[0].i}")
            back = max(0, len(history) - 1 - 5 * panic["n"])
            panic["until"] = beam[0].i + 3 * cfg.T
            log(f"[{cfg.name}] every candidate died at row {beam[0].i}: back to row {history[back][0].i}, jumps free "
                f"and stratified until row {panic['until']}")
            beam = history[back]
            del history[back:]
            continue
        cands.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
        # selection: best scores; up to row cfg.strat_until the first jump's row is a stratum of its own (round
        # robin over the strata, best first), because the value of an approach only shows at the wall
        in_panic = beam[0].i < panic["until"]
        strat = in_panic or (cfg.strat_until is not None and beam[0].i + cfg.T <= cfg.strat_until)
        groups = {}
        seen = set()
        for sc, busy, _np, _, n, c in cands:
            js = tuple(sorted(n.jumps + tuple(c["J"])))
            sig = ((js[-2:], c["m"][0x334] >> 2) if in_panic else js[:cfg.strat_jumps]) if strat else ()
            m = c["m"]
            key = (c["hp"], bytes(m[0x388:0x392]), bytes(m[0x3C8:0x3D2]), bytes(m[0x3B8:0x3C2]), m[0x31A], m[0x334],
                   c["pad"].t - c["pad"].start["B"], c["pad"].down["B"], c["aim"])
            if key in seen:
                continue
            seen.add(key)
            groups.setdefault(sig, []).append((n, c))
        chosen = []
        order = list(groups.values())
        if strat and () in groups and order[0] is not groups[()]:
            order.remove(groups[()])               # the "has not jumped yet" stratum always keeps its seats
            order.insert(0, groups[()])
        depth = 0
        while len(chosen) < cfg.W and any(depth < len(g) for g in order):
            for g in order:
                if depth < len(g) and len(chosen) < cfg.W:
                    chosen.append(g[depth])
            depth += 1

        def materialise(item):
            k, (n, c) = item
            e = eng.q.get()
            try:
                e.load(n.name)
                e.run(c["rows"])
                name = f"{eng.tag}/tmp/fb_{uid}_{layer}_{k}"
                e.save(name)
            finally:
                eng.q.put(e)
            s = dict(c["tr"][-1])
            nj = None
            js = tuple(sorted(n.jumps + tuple(c["J"])))
            if mode_of(s, js, n.i + cfg.T) == "asap" and ground(s):
                nj = n.i + cfg.T
            return Node(name, n.i + cfg.T, n.rows + c["rows"], c["pad"], c["aim"], s,
                        js, nj, c["score"], c["hp"], c["np"])
        beam = par(materialise, list(enumerate(chosen)))
        frames += cfg.T * len(beam)
        stats["layers"] = layer + 1
        b0 = beam[0]
        if layer % 4 == 0:
            log(f"[{cfg.name}] layer {layer} row {b0.i}: best score {b0.score} hp {b0.hp} (beam {len(beam)}, "
                f"scores {beam[-1].score}..{b0.score}, y {b0.last['y']}, jumps {b0.jumps[-3:]}) {time.time() - t0:.0f}s")
        if cfg.stop_fn and cfg.stop_fn(b0.last, b0.i):
            cleanup()
            return b0.rows, {"kill_row": None, "layers": layer + 1, "children": stats["children"], "frames": frames,
                             "seconds": round(time.time() - t0), "stopped": True}
    cleanup()
    raise RuntimeError(f"{cfg.name}: no kill in {cfg.max_layers} layers")


def polish_rows(eng, ck, rows, kill_fn, weapon=0x13, iters=200, seed=1, log=print, name="polish", lo=0,
                moves=False):
    """Hill climbing on a finished fight given as rows (from checkpoint ck to the kill row): a press left out or
    moved by a row or two, the aim (Up) of one press flipped, a jump moved; rows are rebuilt through the press
    rules. Accepts only an earlier kill without a death. Returns (rows to the kill row inclusive, kill index)."""
    import random
    rng = random.Random(seed)
    rows = [tuple(r) for r in rows]
    n = len(rows)
    base = [set(r) - {"B", "A"} for r in rows] + [set(rows[-1]) - {"B", "A"}] * 3

    def starts(btn):
        return [i for i, r in enumerate(rows) if btn in r and (i == 0 or btn not in rows[i - 1])]

    def build(bs, js, bw):
        p = ck.pad.copy()
        out = []
        bset, jset = set(bs), set(js)
        for i in range(n + 3):
            want = set(bw[i])
            if i in bset or (i - 1) in bset:
                want.add("B")
            if i in jset or (i - 1) in jset:
                want.add("A")
            row = p.fix(want)
            p.push(row)
            out.append(row)
        return out

    def cost(tr):
        for k, s in enumerate(tr):
            if s["death"] & 1 or s["pstate"] == 2 or s["weapon"] != weapon:
                return 10 ** 6
            if kill_fn(s):
                return k
        return 10 ** 5

    cur = (starts("B"), starts("A"), base)
    best = cost(eng.sim(ck, build(*cur)))
    if best != n - 1:
        log(f"[{name}] the seed does not regenerate ({best} vs {n - 1}); skipped")
        return rows, n - 1
    it = 0
    while it < iters:
        batch = []
        for _ in range(len(eng.emus) * 2):
            bs, js, bw = list(cur[0]), list(cur[1]), cur[2]
            r = rng.random()
            cand_b = [b for b in bs if b >= lo]
            if r < 0.30 and cand_b:
                bs.remove(rng.choice(cand_b))
            elif r < 0.62 and cand_b:
                b = rng.choice(cand_b)
                bs.remove(b)
                bs.append(b + rng.choice((-2, -1, 1, 2)))
            elif r < 0.72:
                bs.append(rng.randrange(lo, n))
            elif r < 0.86 and cand_b:
                b = rng.choice(cand_b)
                bw = [set(x) for x in bw]
                for i in range(b, min(b + 2, len(bw))):
                    bw[i] ^= {"Up"}
            elif js:
                j = rng.choice(js)
                if j >= lo:
                    js.remove(j)
                    js.append(j + rng.choice((-2, -1, 1, 2)))
            if moves and rng.random() < 0.15:
                a = rng.randrange(lo, n)
                bw = [set(x) for x in bw]
                d = rng.choice(("Left", "Right"))
                for i in range(a, min(a + rng.choice((2, 3, 5)), len(bw))):
                    bw[i] -= {"Left", "Right"}
                    bw[i].add(d)
            batch.append((sorted(set(bs)), sorted(set(js)), bw))
        trs = eng.sims(ck, [build(*c) for c in batch])
        it += len(batch)
        for c, t in zip(batch, trs):
            v = cost(t)
            if v < best:
                best, cur = v, c
                log(f"[{name}] it {it}: kill index {best}")
    out = build(*cur)[:best + 1]
    return out, best

"""Round 2 boss planner (agent a56): beam over "jump steps" instead of TAS-following chunks.

A step = optional pre-move (walk/wait w frames in direction pd), then a jump (A held 2 frames) with an air
direction pattern d, and a slash pattern during the jump: the legal cancel cycle `Down | Down+B | B | - | -`
starting o frames after the jump press (or a sub-weapon throw Up+B at o), played until Ryu lands / clings or the
target dies (then the step ends at once). Every row goes through the a56 Enforcer (legal by construction).

Score = remaining target HP (sum over target slots) * hpw + frame. Beam width K, dedupe by (x,y,hp...).

    python work/a56r2/jplan.py <cfg name> [--width K] [--tag t] [--hours h]
cfg names: demon, jaquio, mdevil (see CFGS).
Output: states/tmp/a56r2_<cfg>_<tag>.inputs.txt (rows from the start state up to the kill frame) + log.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT / "ng" / "stages"))
sys.path.insert(0, str(PROJECT))
import a56_common as C  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402

AIR = (5, 6, 0x0B)
WHY = {}


def target_hp(e, cfg):
    """$66 (boss HP display; it reads 0 on the kill frame) + for the demon the pod (slot 6 while its id is 38)."""
    v = e.ram(0x66, 1)[0]
    if cfg.get("pod"):
        if e.ram(0x406, 1)[0] == 38:
            v += e.ram(0x496, 1)[0]
    return v


def zone_pen(e, cfg, n):
    """frames-equivalent penalty for standing outside the hitting zone of the current target"""
    z = cfg.get("zone")
    if not z:
        return 0.0
    lo, hi = z(e)
    d = lo - n.x if n.x < lo else (n.x - hi if n.x > hi else 0)
    return 0.7 * d


def jaquio_zone(e):
    return (112, 132)        # the record's "plate" (middle pedestal), RAM x ~ 121-139


def demon_zone(e):
    return (68, 100) if e.ram(0x406, 1)[0] == 38 and e.ram(0x496, 1)[0] else (110, 136)


CFGS = {
    # 6-5: control state = room47 + 151 blank rows; slots 6 (id 38, pod) and 7 (id 40, heart)
    "demon": {"start": "tmp/a56r2_65_control", "pod": True, "hist": "logs/a56_6-4b_b15.inputs.txt",
              "pre_hist_blank": 151, "hpw": 6, "zone": demon_zone},
    "jaquio": {"start": "tmp/a56r2_64b_control",  "hist": "logs/a56_6-4a_b11.inputs.txt",
               "pre_hist_blank": 151, "hpw": 6, "zone": jaquio_zone},
    "mdevil": {"start": "ref4751/19_6-4a_control",  "hist": None, "hpw": 6},
    # DEBUG research only (RAM poke: Windmill $82 with 5 ninpo instead of the TAS's Fire Wheel): never a deliverable
    "mdevil_wm": {"start": "ref4751/19_6-4a_control", "hist": None, "hpw": 6, "poke": {0xC9: 0x82, 0x64: 5}},
}

CYC = [("Down",), ("Down", "B"), ("B",), (), ()]


def step_rows(pd, w, d, o, n, mode="slash"):
    """desired rows for a step of total length w + n (n = max air frames)."""
    rows = []
    for _ in range(w):
        rows.append((pd,) if pd else ())
    for i in range(n):
        r = set()
        if i < 2:
            r.add("A")
        if mode == "slash" and i >= o:
            r |= set(CYC[(i - o) % 5])
        elif mode == "throw" and i in (o, o + 1):
            r |= {"Up", "B"}
        elif mode == "throwslash":
            if i in (o, o + 1):
                r |= {"Up", "B"}
            elif i >= o + 5:
                r |= set(CYC[(i - o - 5) % 5])
        dd = d
        if d == "RN":
            dd = None if ("B" in r) else "Right"
        elif d == "LN":
            dd = None if ("B" in r) else "Left"
        elif d in ("RL",):        # forward first half, then back
            dd = "Right" if i < 14 else "Left"
        elif d in ("LR",):
            dd = "Left" if i < 14 else "Right"
        if dd:
            r.add(dd)
        rows.append(tuple(sorted(r)))
    return rows


class Node:
    __slots__ = ("sid", "rows", "frame", "thp", "hp", "x", "y", "en", "score")


def thp_of(cfg, t):
    v = t["bosshp"]
    if cfg.get("pod") and t.get("pod_id") == 38:
        v += t.get("pod_hp", 0)
    return v


def play_step(e, cfg, node, desired, w):
    """play desired rows from node (one traced run, then a replay up to the cut); stop at landing (after the jump
    started) or target death. -> (rows, state, thp, enforcer) or None (death / no jump)"""
    e.mload(node.sid)
    en = node.en.copy()
    rows = [en.emit(want, retry=0) for want in desired]
    e.trace(True)
    e.run(rows)
    tr = e.last_trace
    cut = None
    started = False
    airn = 0
    thp0 = node.thp
    for i, s in enumerate(tr):
        if s["hp"] == 0 or (s.get("dead", 0) & 0x80) or s.get("dw"):
            WHY["dead%d%s%s" % (s["hp"] == 0, "D" if s.get("dead", 0) & 0x80 else "", "W" if s.get("dw") else "")] = WHY.get("dead%d%s%s" % (s["hp"] == 0, "D" if s.get("dead", 0) & 0x80 else "", "W" if s.get("dw") else ""), 0) + 1
            return None
        if thp_of(cfg, s) == 0:
            cut = i
            break
        if i >= w + 1:
            if s["anim"] in AIR:
                started = True
                airn += 1
            elif started:
                if airn < 8 and thp_of(cfg, s) >= thp0:
                    WHY["hop"] = WHY.get("hop", 0) + 1
                    return None          # a hop that went nowhere (cling / ledge): not a step
                cut = i
                break
            elif i >= w + 6:
                WHY["nojump"] = WHY.get("nojump", 0) + 1
                return None
    if cut is None:
        cut = len(tr) - 1
    s = tr[cut]
    en = node.en.copy()
    rows = [en.emit(want, retry=0) for want in desired[:cut + 1]]
    if cut < len(tr) - 1:
        e.mload(node.sid)
        e.trace(False)
        e.run(rows)
    return rows, s, thp_of(cfg, s), en


def run(cfgname, width=4, tag="t", hours=1.0, topb=8, prefix=None, ws=None, ds=None, os_=None, pds=None, modes=("slash",), maxsteps=12):
    cfg = CFGS[cfgname]
    e = C.open_emu(f"a56r2_{cfgname}_{tag}.log")
    logf = open(PROJECT / "logs" / f"a56r2_{cfgname}_{tag}.out", "a")

    def log(*a):
        print(*a, flush=True)
        print(*a, file=logf, flush=True)

    try:
        from ng.mode import TICKS
        e.tick(TICKS)
        e.set_fields(dict(e.fields, pod_id=0x406, pod_hp=0x496))
        s0 = e.load(cfg["start"])
        for a_, v_ in cfg.get("poke", {}).items():
            e.poke(a_, v_)
        hist = []
        if cfg.get("hist"):
            hist = list(read_inputs(PROJECT / cfg["hist"]))[-1700:] + [()] * cfg.get("pre_hist_blank", 0)
        f0 = s0["frame"]
        root = Node()
        root.en = C.Enforcer(hist)
        root.rows = []
        if prefix:
            root.rows = [root.en.emit(r, retry=0) for r in prefix]
            s0 = e.run(root.rows)
        root.sid = e.msave()
        root.frame = s0["frame"]
        root.thp = 32 if cfg.get("pod") else 16
        root.hp = s0["hp"]
        root.x, root.y = s0["x"], s0["y"]
        if prefix:
            root.thp = thp_of(cfg, s0)
        root.score = root.thp * cfg["hpw"]
        log("start", cfgname, f0, "thp", root.thp, "x", root.x, "y", root.y)
        beam = [root]
        visited = {}
        best_done = None
        deadline = time.time() + hours * 3600
        ws = ws or [0, 4, 10, 18, 28]
        ds = ds or ["Right", None, "RN", "Left"]
        os_ = os_ or [2, 0, 1, 3, 4]
        pds = pds or ["Right", "Left", None]
        for depth in range(maxsteps):
            cands = []

            def try_one(node, pd, w, d, mode, o):
                nonlocal best_done
                des = step_rows(pd, w, d, o, 70, mode)
                r = play_step(e, cfg, node, des, w)
                if r is None:
                    return None
                rows, s, thp, en = r
                n = Node()
                n.rows = node.rows + rows
                n.frame = s["frame"]
                n.thp = thp
                n.hp = s["hp"]
                n.x, n.y = s["x"], s["y"]
                n.en = en
                n.score = n.frame - f0 + thp * cfg["hpw"] + zone_pen(e, cfg, n)
                n.sid = None
                if thp == 0:
                    if best_done is None or n.frame < best_done.frame:
                        best_done = n
                        log("DONE", n.frame, "rows", len(n.rows), "hp", n.hp, "depth", depth)
                        save(cfgname, tag, n, f0)
                    return None
                if best_done is not None and n.frame + thp * 5 >= best_done.frame:
                    return None
                cell = (n.x // 6, n.y // 8, n.thp, min(n.hp, 4))
                if visited.get(cell, 1 << 30) < n.frame:
                    WHY["visited"] = WHY.get("visited", 0) + 1
                    return n
                n.sid = e.msave()
                cands.append(n)
                return n

            for node in beam:
                # phase A: every pre-move / air direction with one slash phase; phase B: other phases for the best
                trials = []
                for pd in pds:
                    for w in (ws if pd else [4, 8, 14, 22]):
                        if w == 0 and pd != pds[0]:
                            continue
                        for d in ds:
                            for mode in modes:
                                if time.time() > deadline:
                                    break
                                n = try_one(node, pd, w, d, mode, os_[0])
                                trials.append(((n.score if n else 1e9), pd, w, d, mode))
                trials.sort(key=lambda t: t[0])
                for sc, pd, w, d, mode in trials[:topb]:
                    for o in os_[1:]:
                        if time.time() > deadline:
                            break
                        try_one(node, pd, w, d, mode, o)
            # select
            cands.sort(key=lambda n: n.score)
            seen = set()
            nb = []
            # Pareto first: the earliest node of every target-HP level that beats all lower-HP... (frame, thp) front
            front, bestf = [], 1 << 30
            for n in sorted(cands, key=lambda n: (n.thp, n.frame)):
                if n.frame < bestf:
                    front.append(n)
                    bestf = n.frame
            for n in sorted(front, key=lambda n: n.score)[:max(1, width // 2)]:
                k = (n.x // 2, n.y // 4, n.thp, n.hp, n.frame // 3)
                seen.add(k)
                nb.append(n)
            for n in cands:
                k = (n.x // 2, n.y // 4, n.thp, n.hp, n.frame // 3)
                if k in seen:
                    continue
                seen.add(k)
                nb.append(n)
                if len(nb) >= width:
                    break
            for n in cands:
                if n not in nb and n.sid:
                    e.mfree(n.sid)
            for n in beam:
                if n.sid and n is not root:
                    try:
                        e.mfree(n.sid)
                    except Exception:
                        pass
            beam = nb
            for n in nb:
                cell = (n.x // 6, n.y // 8, n.thp, min(n.hp, 4))
                visited[cell] = min(visited.get(cell, 1 << 30), n.frame)
            if beam:
                save(cfgname, tag + "_partial", beam[0], f0)
            log("why", dict(WHY))
            WHY.clear()
            log("depth", depth, "cands", len(cands), "best", [(n.frame - f0, n.thp, n.hp, n.x, n.y) for n in beam])
            if not beam or time.time() > deadline:
                break
        return best_done
    finally:
        e.close()
        logf.close()


def save(cfgname, tag, n, f0):
    p = PROJECT / "states" / "tmp" / f"a56r2_{cfgname}_{tag}.inputs.txt"
    C.save_rows(p, n.rows, f"a56r2 {cfgname} kill at frame {n.frame} (start frame {f0}), hp {n.hp}")


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v) if default is not None else v
    return default


if __name__ == "__main__":
    a = sys.argv[1:]
    width = opt(a, "--width", 4)
    tag = opt(a, "--tag", "t")
    hours = opt(a, "--hours", 1.0)
    modes = opt(a, "--modes", "slash").split(",")
    hpw = opt(a, "--hpw", 0.0)
    if hpw:
        CFGS[a[0]]["hpw"] = hpw
    pre = opt(a, "--prefix", None)
    pre_n = opt(a, "--prefix-frames", 0)
    prefix = list(read_inputs(pre))[:pre_n] if pre else None
    r = run(a[0], width, tag, hours, modes=tuple(modes), prefix=prefix)
    print("RESULT", None if r is None else (r.frame, r.hp))

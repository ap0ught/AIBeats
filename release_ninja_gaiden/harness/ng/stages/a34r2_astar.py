"""Acts 3-4 round 2: A* over "stable" states (Ryu standing or clinging, rflags bit 2 clear) with legal macro actions.
Owned by the Acts 3-4 agent.

    python ng/stages/a34r2_astar.py <stage> <start state> <prefix rows|-> <goal> <out> [--max-exp N] [--hist rows]

<goal> = "pos:<room>:<wpos>:<y>:<tol>"  (standing within tol of that point)
       = "room:<room>"                   (any frame in that room, e.g. the next room / stage)
Macros (each one ends when Ryu is stable again, or after its own frames for runs/waits):
  C8/C8m one single-wall climb cycle (wall right / left), JO<dir><tail><k> jump off a wall, run R/L n, jumps with
  a held direction that may switch at frame m, slashes in the air, waits. Every macro is made legal against the
  node's own input history (a34_core.greedy_legal). Nodes are deduplicated by (room, wpos, y, facing, hp) keeping the
  earliest frame. f = t + h, h = |dx|/1.5 + max(0, y - gy)/2.4 (optimistic).
Output: logs/a34/<out>.inputs.txt = prefix + found rows; end state states/tmp/a34r2_x/<out>.State.
"""
from __future__ import annotations

import heapq
import itertools
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

R = lambda *a: tuple(a)  # noqa: E731
import os  # noqa: E402
FINE = os.environ.get("A34_FINE", "") == "1"
ENEMYKEY = os.environ.get("A34_ENEMYKEY", "") == "1"
# round 3: A34_HMAX=1 -> h = max(dx/1.5, climb/2.4) (a jump moves right and up at once; the sum over-estimates)
HC = (lambda a, b: max(a, b)) if os.environ.get("A34_HMAX", "") == "1" else (lambda a, b: a + b)
# round 3: A34_SWITCH=1 -> jumps switch the held direction at more points (m = 4..24)
SWITCH = os.environ.get("A34_SWITCH", "") == "1"
AIRRUN = os.environ.get("A34_AIRRUN", "") == "1"   # dedup key includes the coarse enemy layout   # extra fine-grained macros (waits 1-4, C7, runs 3/6/12)


def macros():
    M = {}
    M["C8"] = [R("Left", "A")] * 2 + [R("Right")] * 6
    M["C8m"] = [R("Right", "A")] * 2 + [R("Left")] * 6
    M["C9"] = [R("Left", "A")] * 2 + [R("Right")] * 7
    M["C9m"] = [R("Right", "A")] * 2 + [R("Left")] * 7
    if FINE:
        M["C7"] = [R("Left", "A")] * 2 + [R("Right")] * 5
        M["C7m"] = [R("Right", "A")] * 2 + [R("Left")] * 5
    for side, (aw, to) in (("L", ("Left", "Right")), ("R", ("Right", "Left"))):
        for tail in ("N", "A", "T"):          # none, keep away dir, drift back toward the wall
            for k in ((2, 4, 8, 12, 20, 28) if tail == "A" else (2, 4, 8, 12)):
                t = () if tail == "N" else (R(aw) if tail == "A" else R(to))
                M[f"JO{side}{tail}{k}"] = [R(aw, "A")] * 2 + [t] * k
    for n in (2, 4, 8, 16):
        M[f"R{n}"] = [R("Right")] * n
        M[f"L{n}"] = [R("Left")] * n
    for n in ((1, 2, 3, 4, 6, 12) if FINE else (2, 6, 12)):
        M[f"W{n}"] = [()] * n
    if FINE:
        for n in (3, 6, 12):
            M[f"R{n}"] = [R("Right")] * n
    for jd in ("N", "R", "L"):
        jr = R("A") if jd == "N" else (R("Right", "A") if jd == "R" else R("Left", "A"))
        for hold in ("N", "R", "L"):
            for m in ((0, 4, 8, 12, 16, 20, 24) if SWITCH else (0, 16)):
                if m and hold == "N":
                    continue
                h = () if hold == "N" else (R("Right") if hold == "R" else R("Left"))
                pre = [() if jd == "N" else (R("Right") if jd == "R" else R("Left"))] * m
                M[f"J{jd}{hold}{m}"] = [jr] * 2 + pre + [h] * 50
        # jump with air slashes (Down+B every 5 frames from frame 4), holding the jump direction
        d = () if jd == "N" else (R("Right") if jd == "R" else R("Left"))
        rows = [jr] * 2
        for k in range(10):
            rows += [tuple(sorted(set(d + ("Down", "B")), key=K.BTNS.index))] * 2 + [d] * 3
        M[f"J{jd}S"] = rows
    if os.environ.get("A34_THROW", "") == "1":      # sub-weapon throw (Up+B, no direction), standing or in the air
        M["TH"] = [R("Up", "B")] * 2 + [()] * 4
        for jd in ("N", "R", "L"):
            jr = R("A") if jd == "N" else (R("Right", "A") if jd == "R" else R("Left", "A"))
            d = () if jd == "N" else (R("Right") if jd == "R" else R("Left"))
            for k in (4, 10):
                M[f"J{jd}T{k}"] = [jr] * 2 + [d] * k + [R("Up", "B")] * 2 + [()] * 2 + [d] * 50
    M["SB"] = [R("B")] * 2 + [()] * 4
    M["SRB"] = [R("Right", "B")] * 2 + [R("Right")] * 4
    return M


class Node:
    __slots__ = ("t", "sid", "L", "parent", "rows", "tag", "s")

    def __init__(self, t, sid, L, parent, rows, tag, s):
        self.t, self.sid, self.L, self.parent, self.rows, self.tag, self.s = t, sid, L, parent, rows, tag, s


def path_rows(n):
    out = []
    while n is not None:
        out.append(n.rows)
        n = n.parent
    res = []
    for r in reversed(out):
        res.extend(r)
    return res


def path_tags(n):
    out = []
    while n is not None:
        out.append(n.tag)
        n = n.parent
    return list(reversed(out))


def main():
    a = sys.argv[1:]
    def opt(name, dflt):
        if name in a:
            i = a.index(name); v = a[i + 1]; del a[i:i + 2]
            return type(dflt)(v)
        return dflt
    max_exp = opt("--max-exp", 3000)
    hist_name = opt("--hist", "")
    only = opt("--only", "")
    wh = opt("--w", 1.0)
    name, start, pre, goal, out = a[:5]
    st = K.BY_NAME[name]
    M = macros()
    if only:
        keep = only.split(",")
        M = {k: v for k, v in M.items() if any(k.startswith(p) for p in keep)}
    g = goal.split(":")
    e = K.open_emu(f"a34r2_astar_{out}.log")
    try:
        e.load(start)
        rows0 = K.load_rows(pre) if pre != "-" else []
        hist = (K.load_rows(hist_name) if hist_name else []) + rows0
        s = e.run(rows0) if rows0 else e.state()
        t0 = s.frame
        print("start", t0, "room", s.room, "x", s.x, "y", s.y, "wpos", K.wpos(s), "macros", len(M), flush=True)

        def h(s):
            if g[0] == "room":
                if s.room == int(g[1]):
                    return 0.0
                if len(g) >= 4:      # room:<next room>:<exit wpos>:<exit y> -> head for the exit point
                    return HC(abs(K.wpos(s) - int(g[2])) / 1.5, max(0, s.y - int(g[3])) / 2.4)
                return 30.0
            gr, gx, gy = int(g[1]), int(g[2]), int(g[3])
            if s.room != gr:
                return 999.0
            return HC(abs(K.wpos(s) - gx) / 1.5, max(0, s.y - gy) / 2.4)

        def is_goal(s):
            if g[0] == "room":
                return s.room == int(g[1]) or s.stage != st
            gr, gx, gy, tol = int(g[1]), int(g[2]), int(g[3]), int(g[4])
            return s.room == gr and abs(K.wpos(s) - gx) + abs(s.y - gy) <= tol and not (s.rflags & 4)

        root = Node(t0, e.msave(), K.Legal(hist), None, [], "start", s)
        cnt = itertools.count()
        heap = [(t0 + wh * h(s), next(cnt), root)]
        best = {}
        nexp = 0
        tstart = time.time()
        found = None
        while heap and nexp < max_exp:
            f, _, n = heapq.heappop(heap)
            if n.sid is None:
                continue
            nexp += 1
            if nexp % 50 == 0:
                print(f"  exp {nexp} f={f:.1f} t={n.t} room={n.s.room} wpos={K.wpos(n.s)} x={n.s.x} y={n.s.y} hp={n.s.hp} open={len(heap)} "
                      f"{time.time() - tstart:.0f}s tags={path_tags(n)[-6:]}", flush=True)
            wallmode = bool(n.s.coll & 0x2A) or bool(n.s.rflags & 4)
            for tag, mrows in M.items():
                if wallmode != (tag[0] == "C" or tag.startswith("JO")) and tag[0] != "W":
                    # round 3 (A34_AIRRUN=1): while airborne (e.g. the upward launch at a room entered from below)
                    # also allow plain Left/Right holds = air drift
                    if not (AIRRUN and wallmode and (n.s.rflags & 4) and tag[0] in "RL" and tag[1:].isdigit()):
                        continue
                L = n.L.copy()
                legal = K.greedy_legal(mrows, L)
                e.mload(n.sid)
                e.trace(True)
                if tag[0] == "J" and len(legal) > 24:
                    # jumps: run in pieces and stop once Ryu has been airborne and is stable again
                    tr = []
                    pos = 0
                    for piece in (16, 12, 12, 100):
                        e.run(legal[pos:pos + piece])
                        tr += e.last_trace
                        pos += piece
                        if pos >= len(legal):
                            break
                        air = any(x["rflags"] & 4 for x in tr)
                        if air and not (tr[-1]["rflags"] & 4):
                            break
                        if any(x["y"] >= 0xF8 or (x["dead"] & 0x80) for x in tr):
                            break
                    truncated = len(tr) < len(legal)
                    legal = legal[:len(tr)]
                else:
                    truncated = False
                    e.run(legal)
                    tr = e.last_trace
                e.trace(False)
                # cut the macro at the first stable frame after it has left the stable state (jumps / jump-offs),
                # or keep it whole (runs, waits, climbs)
                cut = len(tr)
                airborne = False
                hit_goal = None
                dead = False
                for i, x in enumerate(tr):
                    if x["y"] >= 0xF8 or (x["dead"] & 0x80) or x["hp"] == 0:
                        dead = True
                        break
                    if is_goal(x):
                        hit_goal = i
                        break
                    if x["rflags"] & 4:
                        airborne = True
                    elif airborne and tag[0] == "J":
                        cut = i + 1
                        break
                if dead:
                    continue
                if hit_goal is not None:
                    cut = hit_goal + 1
                legal2 = legal[:cut]
                if cut < len(legal) or truncated:
                    L = n.L.copy()
                    for r in legal2:
                        L.push(r)
                    # a press that is still too short at the cut: hold it (still legal) one more frame
                    need = tuple(b for b in K.BTNS if L.held[b] and L.run[b] < L.HOLD)
                    if need:
                        legal2 = legal2 + [need]
                        L.push(need)
                        cut += 1
                    e.mload(n.sid)
                    s2 = e.run(legal2)
                else:
                    s2 = e.state()
                t2 = n.t + len(legal2)
                if hit_goal is not None and is_goal(s2):
                    nn = Node(t2, None, L, n, legal2, tag, s2)
                    if found is None or t2 < found.t:
                        found = nn
                        print(f"  GOAL at {t2} via {path_tags(nn)}", flush=True)
                    continue
                if (s2.rflags & 4) and tag[0] == "J":
                    continue          # still in the air after the whole macro: discard
                key = (s2.room, K.wpos(s2), s2.y, s2.rflags & 0x40, s2.hp >= n.s.hp, s2.coll & 0x3F)
                if ENEMYKEY:     # coarse enemy layout: arrivals with other enemy positions are kept apart
                    rb = e.ram(0x400, 0xC0)
                    key = key + tuple((int(rb[j]), int(rb[0x60 + j]) // 32, int(rb[0x80 + j]) // 32)
                                      for j in range(8) if rb[j])
                if key in best and best[key] <= t2:
                    continue
                best[key] = t2
                if found is not None and t2 + h(s2) >= found.t:
                    continue
                nn = Node(t2, e.msave(), L, n, legal2, tag, s2)
                heapq.heappush(heap, (t2 + wh * h(s2) + 0.5 * max(0, 16 - s2.hp), next(cnt), nn))
            if n is not root:
                e.mfree(n.sid)
            n.sid = None
            if found is not None and (wh > 1.0 or (heap and heap[0][0] >= found.t)):
                break
        if found is None:
            print("no goal found; expansions", nexp, flush=True)
            return
        rows = rows0 + path_rows(found)
        K.save_rows(out, rows, f"{start} + {pre} + A* to {goal}: frame {found.t}; macros {path_tags(found)}")
        e.load(start)
        s = e.run(rows)
        e.save(f"tmp/a34r2_x/{out}")
        print(f"RESULT {out}: goal at {found.t}; replay end frame {s.frame} room {s.room} x {s.x} y {s.y} hp {s.hp} "
              f"wpos {K.wpos(s)}; tags {path_tags(found)}", flush=True)
    finally:
        e.close()


if __name__ == "__main__":
    main()

"""[track C copy of chain B's u16b_climb3.py: outputs logs/fix/u17c_climb_<tag>.json and u17c_climb_mark<px>_<tag>.json, env U17C_*;
extra env U17C_STOP=<px>: stop as soon as a node standing at >= that height is expanded (a local study of one gate)]
u16b (chain B, 2026-10-10): Intruder Excluder's climb, the search of early_l8climb.py with its queue fixed.

early_l8climb.py is an earliest-arrival search by LANDING (node = the toad standing somewhere unhurt; candidates = stand /
walk or run / wait + run + jump; uniform cost).  It reached 2,300 px of 4,030 and then choked: uniform cost expands every
node younger than the front, wherever it stands, and the queue grew to 400-1,100 nodes.  Changes here:

  * order: frames + (top - height) / RATE instead of frames alone.  A node lower down is only expanded when it is that
    much YOUNGER than the front (64 px = one floor = 64/RATE frames), i.e. entries dominated in (height, frame) sink in
    the queue instead of being expanded first.  RATE = 0 gives the old uniform cost.
  * hard drops: more than DEPTH px under the highest expanded node; the queue is cut to its best 2/3 when it passes MAXQ
  * failed candidates stop as soon as the toad is falling below where it started (they used to run 125 frames)
  * the standing move and the wide candidate count are kept; a jump may switch its air direction once
  * the END is part of the search: when the arrival cutscene starts (animation 50) the candidate idles on until the
    game hands control back; its cost is that control frame plus the run to the boss (x 183 is next to him).  A toad
    flattened by the descending boss (animation 85/86; it stood at x >= 234) is rejected.  So the last jump is steered
    by the search itself, and the camera's lag at the top (the cutscene waits for the camera) is paid for honestly.
  * root = bookmark early_L8_p0 (up14 frame 12488, the placement; checked equal to cap14's row); nodes keep parent
    links instead of whole input lists

    python u16b_climb.py <tag> [tries per node = 140] [seed = 1] [resume: a milestone json {inputs from 12488}]
        env U17C_RATE (2.0)  U17C_DEPTH (260)  U17C_CELL (3)  U17C_EXTRA (expansions after the first finish, 300)
    -> logs/fix/u17c_climb_<tag>.json       {from_frame 12488, inputs through the control frame, cut, control, ...}
       logs/fix/u17c_climb_mark<px>_<tag>.json  every 100 px (inputs so far; a later run can resume from it)
No memory writes.  Nothing here is a route segment; u16b_build.py makes B8 from the result.

u16b_climb2.py (this file) = u16b_climb.py + REFINEMENT: the random moves come from a coarse grid (waits 0/1/2/4/8/16/32,
runs 0/2/4/8/12/16/24/32/48/64, A held 4..32), which costs a frame or two on every floor.  After the random tries the best
kids of a node (the climbing ones first) are polished: every neighbour move (wait, run length, A hold a frame or two
shorter or longer, dash on/off) is tried, and one that stands in the same spot sooner replaces it, until nothing improves.
    env U17C_REFINE (kids polished per node, 6)  U17C_ROUNDS (3)

u16b_climb3.py (this file) = u16b_climb2.py + DUCKING.  The flier floors (1,900-2,600 px up, again near the top) shoot
sparks 22 px above the floor; up14 passes them by holding Down (animation 75: the toad ducks and slides, sparks pass
overhead), and a jump pressed straight out of a duck leaves at sprint speed (192).  The earlier families had no Down
at all and stalled at 2,496 px.  Moves now: ("stand", frames, ducked) | ("walk", w, ducked wait, d, n, dash, k) |
("jump", w, ducked wait, d, n, dash, k, h, da, da2), k = frames of Down between the run and the jump.  A ducking toad
(animation 75) counts as standing.
"""
import heapq
import json
import os
import random
import sys
import time

from toads.emulator import BizHawk, LOGS_DIR

START = 12488
GOAL = 4032                                                   # the arena floor, px above the placement
F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11,
     "camlo": 0x89, "camhi": 0x8A}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
RATE = float(os.environ.get("U17C_RATE", 2.0))
DEPTH = int(os.environ.get("U17C_DEPTH", 260))
CELL = int(os.environ.get("U17C_CELL", 3))
EXTRA = int(os.environ.get("U17C_EXTRA", 300))
REFINE = int(os.environ.get("U17C_REFINE", 6))
ROUNDS = int(os.environ.get("U17C_ROUNDS", 3))
MAXQ = int(os.environ.get("U17C_MAXQ", 3000))
STOP = int(os.environ.get("U17C_STOP", 0))
P_STAND = float(os.environ.get("U17C_PSTAND", 0.1))
REM = 166                                                     # arena floor -> control, roughly (only to rank finished lines among open nodes)
FIX = LOGS_DIR / "fix"


def Hof(s):
    return s.height | s.hh << 8


def finish(e, ins, s, lives0):
    """the arrival cutscene has started: idle until the game hands control back -> ("END", inputs, state, cut index, x at the cut, flattened)"""
    cut, cutx, flat = len(ins), s.x, False
    for k in range(280):
        s = e.step((), 1)
        ins.append("")
        if s.anim in (85, 86):
            flat = True
        if s.lives < lives0 or s.level != 7:
            return None
        if k >= 5 and s.anim not in (50, 85, 86) and s.hp == 47:
            return ("END", ins, s, cut, cutx, flat)
    return None


DUCK = float(os.environ.get("U17C_PDUCK", 0.3))


def standing(s):
    return s.z == 0 and (1 <= s.anim <= 8 or s.anim == 75)


def sample(rng):
    """one random move: ("stand", wait, ducked) | ("walk", w, wd, d, n, dash, k) | ("jump", w, wd, d, n, dash, k, h, da, da2)"""
    if rng.random() < P_STAND:                               # just stand (or duck): the flier columns need a spark to pass first
        return ("stand", rng.choice([4, 6, 12, 24, 40]), rng.random() < 0.45)
    w = rng.choice([0, 0, 0, 0, 1, 2, 4, 8, 16, 32])
    wd = w > 0 and rng.random() < DUCK
    d = rng.choice(["Right", "Left", None, None])
    walk = rng.random() < 0.2
    if walk and d is None:
        d = rng.choice(["Right", "Left"])
    n = rng.choice([0, 0, 2, 4, 8, 12, 16, 24, 32, 48, 64]) if d else 0
    if walk:
        n = rng.choice([4, 8, 16, 24, 32, 48])
    k = rng.choice([1, 2, 4, 8, 12, 16, 24]) if rng.random() < DUCK * 0.8 else 0
    h = 0 if walk else rng.choice([4, 8, 10, 11, 12, 13, 14, 16, 20, 26, 32])
    da = rng.choice([d, d, "Right", "Left", None])
    da2 = rng.choice(["Right", "Left", None]) if rng.random() < 0.25 else da     # the air direction after A is let go
    dash = n >= 10 and rng.random() < 0.6
    if walk:
        return ("walk", w, wd, d, n, dash, k)
    return ("jump", w, wd, d, n, dash, k, h, da, da2)


def neighbours(mv):
    """the moves one or two frames away from mv (same directions)"""
    out = []
    if mv[0] == "stand":
        out = [("stand", mv[1] - q, mv[2]) for q in (1, 2, 4) if mv[1] - q >= 1]
    elif mv[0] == "walk":
        _, w, wd, d, n, dash, k = mv
        out += [("walk", w - q, wd, d, n, dash, k) for q in (1, 2, 4) if w - q >= 0]
        out += [("walk", w, wd, d, n + q, dash, k) for q in (-4, -2, -1, 1, 2) if n + q >= 1]
        out += [("walk", w, wd, d, n, not dash, k)] if n >= 4 else []
        out += [("walk", w, wd, d, n, dash, k + q) for q in (-4, -2, -1, 1, 2) if k and k + q >= 0]
    else:
        _, w, wd, d, n, dash, k, h, da, da2 = mv
        out += [("jump", w - q, wd and w - q > 0, d, n, dash, k, h, da, da2) for q in (1, 2, 4) if w - q >= 0]
        out += [("jump", w + 1, wd, d, n, dash, k, h, da, da2)]
        if d:
            out += [("jump", w, wd, d, n + q, dash, k, h, da, da2) for q in (-4, -2, -1, 1, 2) if n + q >= 0]
            out += [("jump", w, wd, d, n, not dash, k, h, da, da2)] if n >= 3 else []
        out += [("jump", w, wd, d, n, dash, k + q, h, da, da2) for q in (-4, -2, -1, 1, 2) if k and k + q >= 0]
        out += [("jump", w, wd, d, n, dash, k, h + q, da, da2) for q in (-2, -1, 1, 2) if 2 <= h + q <= 34]
    return out


def run_move(e, s0, mv, base):
    """play one move from a standing toad -> (inputs, state) when it stands again unhurt and not lower, ("END", ...) when the
    arrival cutscene started during it, None otherwise"""
    H0 = Hof(s0)
    near_top = H0 - base >= 3900
    if mv[0] == "stand":
        ins, s = [], s0
        inp = ("Down",) if mv[2] else ()
        for _ in range(mv[1]):
            s = e.step(inp, 1)
            ins.append("+".join(inp))
            if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
                return None
            if near_top and s.anim == 50:
                return finish(e, ins, s, s0.lives)
        return (ins, s) if (s.z == 0 and Hof(s) - H0 >= -4) else None
    walk = mv[0] == "walk"
    if walk:
        _, w, wd, d, n, dash, k = mv
        h, da, da2 = 0, None, None
    else:
        _, w, wd, d, n, dash, k, h, da, da2 = mv
    seq = [("Down",) if wd else ()] * w
    if d and n:
        seq += ([(d,), ()] if dash else []) + [(d,)] * n
    seq += [("Down",)] * k
    seq += [tuple(x for x in (da, "A") if x)] * h
    ins, s, air = [], s0, False
    for j in range(125):
        inp = seq[j] if j < len(seq) else ((da2,) if (da2 and not walk) else ())
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
            return None
        if near_top and s.anim == 50:
            return finish(e, ins, s, s0.lives)
        H = Hof(s)
        if walk:
            if j >= len(seq) - 1:                              # the last frame of the sequence: a ducking toad may stay ducked
                return (ins, s) if (standing(s) and H - H0 >= -4) else None
            if s.z != 0 and H < H0 - 6:
                return None                                    # walked off an edge
        elif j >= len(seq) - h:
            if s.z != 0:
                air = True
                if H < H0 - 6 and j >= len(seq):
                    return None                                # falling below where it started: it cannot stand "not lower" any more
            elif air and 1 <= s.anim <= 8:
                return (ins, s) if H - H0 >= -4 else None
        elif s.z != 0 and H < H0 - 6:
            return None                                        # ran off an edge before the jump
    return None


def main():
    tag = sys.argv[1]
    tries = int(sys.argv[2]) if len(sys.argv) > 2 else 140
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rng = random.Random(seed)
    e = BizHawk(log_name=f"u17c_climb_{tag}.log", fields=F)
    s = e.load("early_L8_p0")
    base = Hof(s)
    assert base == 3934 and s.x == 128 and s.hp == 47, s
    lives0 = s.lives
    # up14's own milestones from the per-frame RAM capture: first frame standing at +g px (frames since the placement)
    UP14 = {}
    with open(LOGS_DIR / "cap14.ram", "rb") as R:
        for f in range(START, 15660):
            R.seek((f - 1) * 2048)
            m = R.read(2048)
            dh0 = (m[0x439] | m[0x42A] << 8) - base
            for g in range(100, 4100, 100):
                if g not in UP14 and dh0 >= g and m[0x475] == 0:
                    UP14[g] = f - START
    ins0 = []
    if len(sys.argv) > 4:                                    # resume: a saved milestone is the new root
        ins0 = list(json.load(open(sys.argv[4]))["inputs"])
        for b in ins0:
            s = e.step(bt(b), 1)
        assert s.hp == 47 and s.lives == lives0 and s.z == 0, s
        print(f"resumed from {sys.argv[4]}: {len(ins0)} frames in, +{Hof(s) - base} px, x {s.x}", flush=True)
    print(f"u16b_climb3 {tag}: duck {DUCK}, refine {REFINE}x{ROUNDS}, tries {tries} seed {seed} rate {RATE} depth {DEPTH} cell {CELL}; root +{Hof(s) - base} px at {len(ins0)} frames, lives {lives0}", flush=True)

    nodes = {0: (None, ins0)}                                # id -> (parent id, inputs of its own move)

    def line(nid):
        parts = []
        while nid is not None:
            p, ci = nodes[nid]
            parts.append(ci)
            nid = p
        out = []
        for ci in reversed(parts):
            out += ci
        return out

    def prio(frames, dh):
        return frames + REM + (max(0, GOAL - dh) / RATE if RATE > 0 else 0)

    # heap entries: (priority, -height, seq, node id, frames, state or None, savestate id or None, end info or None)
    heap = [(prio(len(ins0), Hof(s) - base), -(Hof(s) - base), 0, 0, len(ins0), s, e.msave(), None)]
    seq_no, cells, expanded, top, marks = 0, {}, 0, 0, {}
    best_end, after_end, t0, last_say = None, 0, time.time(), time.time()

    def write_end(info, nid, frames, final=False):
        ci_all = line(nid)
        st, cut, cutx, flat = info
        d = {"from_frame": START, "inputs": ci_all, "frames_to_control": frames, "control_x": st.x, "cut_index": cut, "cut_x": cutx,
             "up14_control": 15789 - START + 1, "saves_vs_up14": (15790 - START) - frames, "tag": tag, "tries": tries, "seed": seed, "rate": RATE,
             "note": "inputs from up14 frame 12488 (the placement) through the frame control returns after the arrival cutscene; "
                     "cut_index = input index (in the last move) where animation 50 started"}
        p = FIX / f"u17c_climb_{tag}.json"
        tmp = p.with_suffix(".tmp")
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, p)

    while heap:
        pr, _, _, nid, frames, st, sid, end = heapq.heappop(heap)
        if end is not None:                                   # a finished line
            cost = pr
            if best_end is None or cost < best_end[0]:
                first = best_end is None
                best_end = (cost, nid, frames)
                write_end(end, nid, frames)
                print(f"FINISH{'' if first else ' (better)'}: control after {frames} frames (up14 {15790 - START}): {15790 - START - frames:+d}; toad x {end[0].x} at control, "
                      f"x {end[2]} when the cutscene starts, cost {cost:.1f}   [expanded {expanded}, queue {len(heap)}, {time.time() - t0:.0f} s]", flush=True)
            continue
        dh = Hof(st) - base
        for g in sorted(UP14):
            if dh >= g and g not in marks:
                marks[g] = frames
                print(f"  +{g} px: standing after {frames} frames (up14 {UP14[g]}): {UP14[g] - frames:+d}   [expanded {expanded}, queue {len(heap)}, {time.time() - t0:.0f} s]", flush=True)
                p = FIX / f"u17c_climb_mark{g}_{tag}.json"
                json.dump({"from_frame": START, "inputs": line(nid), "reached_px": dh, "frames": frames, "up14_frames": UP14[g], "x": st.x}, open(p, "w"))
        top = max(top, dh)
        if STOP and dh >= STOP:
            print(f"STOP: +{dh} px standing after {frames} frames at x {st.x}   [expanded {expanded}, {time.time() - t0:.0f} s]", flush=True)
            json.dump({"from_frame": START, "inputs": line(nid), "reached_px": dh, "frames": frames, "x": st.x}, open(FIX / f"u17c_climb_stop_{tag}.json", "w"))
            break
        if dh < top - DEPTH:                                 # far below the front: drop it
            e.mfree(sid)
            continue
        if best_end is not None:
            if frames + 134 + max(0, GOAL - dh) / 3.76 >= best_end[0] or after_end >= EXTRA:   # cannot beat the finished line (the cutscene alone is 134 frames) / enough
                e.mfree(sid)
                continue
            after_end += 1
        cell = (dh // 16, st.x // 32, frames // 48)          # the same spot later is a different node: things up here run on the clock
        if cells.get(cell, 0) >= CELL:
            e.mfree(sid)
            continue
        cells[cell] = cells.get(cell, 0) + 1
        expanded += 1
        kids, ends = {}, None

        def offer(mv):
            """play mv from this node; file the result -> the kid key it landed in (None when it failed, "END" when it finished)"""
            nonlocal ends
            e.mload(sid)
            r = run_move(e, st, mv, base)
            if r is None:
                return None
            if r[0] == "END":
                _, ci, cs, cut, cutx, flat = r
                if not flat:
                    cost = frames + len(ci) + max(0, 183 - cs.x) / 3.0
                    if ends is None or cost < ends[0]:
                        ends = (cost, ci, cs, cut, cutx, flat, mv)
                return "END"
            ci, cs = r
            k = ((Hof(cs) - base) // 16, cs.x // 12, (len(ci) // 24, mv[2]) if mv[0] == "stand" else -1)   # waits of different length are different moves
            if k not in kids or len(ci) < len(kids[k][0]):
                if k in kids:
                    e.mfree(kids[k][2])
                kids[k] = (ci, cs, e.msave(), mv)
            return k

        for _ in range(tries):
            offer(sample(rng))
        # refinement: polish the best kids (the climbing ones first, highest then soonest) and the best finish
        seen = set()
        for rnd in range(ROUNDS):
            order = sorted(kids.items(), key=lambda kv: (-kv[0][0], len(kv[1][0])))
            todo = [(k, v[3]) for k, v in order if k[2] == -1 and (Hof(v[1]) - base) > dh + 24][:REFINE]
            todo += [(k, v[3]) for k, v in order if k[2] == -1 and (Hof(v[1]) - base) <= dh + 24][:2]
            better = False
            for k, mv in todo:
                n0 = len(kids[k][0])
                for nb in neighbours(mv):
                    if nb in seen:
                        continue
                    seen.add(nb)
                    offer(nb)
                if len(kids[k][0]) < n0:
                    better = True
            if ends is not None:
                c0 = ends[0]
                for nb in neighbours(ends[6]):
                    if nb not in seen:
                        seen.add(nb)
                        offer(nb)
                better = better or ends[0] < c0
            if not better:
                break
        kids = {k: v[:3] for k, v in kids.items()}
        if ends is not None:
            ends = ends[:6]
        for ci, cs, csid in kids.values():
            cdh = Hof(cs) - base
            if cdh < top - DEPTH:
                e.mfree(csid)
                continue
            seq_no += 1
            nodes[seq_no] = (nid, ci)
            heapq.heappush(heap, (prio(frames + len(ci), cdh), -cdh, seq_no, seq_no, frames + len(ci), cs, csid, None))
        if ends is not None:
            cost, ci, cs, cut, cutx, flat = ends
            seq_no += 1
            nodes[seq_no] = (nid, ci)
            heapq.heappush(heap, (cost, -GOAL, seq_no, seq_no, frames + len(ci), None, None, (cs, cut, cutx, flat)))
        e.mfree(sid)
        if len(heap) > MAXQ:                                 # keep the best two thirds
            heap.sort()
            for it in heap[MAXQ * 2 // 3:]:
                if it[6] is not None:
                    e.mfree(it[6])
            del heap[MAXQ * 2 // 3:]
            heapq.heapify(heap)
        if time.time() - last_say > 300:
            last_say = time.time()
            print(f"    ... expanded {expanded}, queue {len(heap)}, top +{top} px, {time.time() - t0:.0f} s", flush=True)
    if best_end:
        print(f"RESULT {tag}: control {best_end[2]} frames after the placement (up14: {15790 - START}); saves {15790 - START - best_end[2]}; "
              f"{expanded} nodes expanded, {time.time() - t0:.0f} s -> logs/fix/u17c_climb_{tag}.json", flush=True)
    else:
        print(f"no line reaches the arena; marks {marks}", flush=True)
    e.close()


if __name__ == "__main__":
    main()

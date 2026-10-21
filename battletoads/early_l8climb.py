"""EARLY track (2026-10-09): Intruder Excluder - is the climb's slack real?  A small earliest-arrival search on a snapshot.

up14 stands 600 px above the start 563 frames after the placement (frame 12488), 1,200 px after 1,152; the record's
whole climb is 369 frames shorter than ours.  The old search ranked states by height with 4-frame macros behind a
36-frame entry wait.  This one searches by LANDING instead:
    node      = the toad standing somewhere (z 0), unhurt, with the frame count that got it there
    candidate = wait w, run d for n frames (double tap when long), jump with A held h and an air direction; kept when
                the toad stands at least 30 px higher within 120 frames
    order     = uniform cost: always expand the node with the smallest frame count; at most CELL expanded nodes per
                (16-px height band, 24-px x bucket)
The first node popped at or above the goal height is the earliest arrival this candidate family can produce.

    python early_l8climb.py [goal px = 600] [tries per node = 70] [seed = 1] [resume: a milestone json]
    -> logs/fix/early_l8climb_<goal>.json {inputs from up14 frame 12488, landings}, prints the comparison with up14;
       every 200 px a milestone logs/fix/early_l8climb_mark<px>.json (inputs so far) that a later run can resume from
"""
import heapq
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR

START = 12488
F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
UP14 = {130: 223, 200: 263, 330: 383, 460: 494, 600: 563, 800: 836, 1000: 1004, 1200: 1152, 1800: 1643, 2400: 2117, 3000: 2517, 3600: 2903}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
CELL = 3
TAG = __import__("os").environ.get("EARLY_TAG", "")           # suffix for the milestone files of a second, parallel run


def candidate(e, s0, rng):
    """one move from a standing toad: a walk/run (20 %) or wait + run + jump; -> (inputs, state) when it stands again
    unhurt and not lower than before (the first floor is only reached by two jumps: +2 px, then +62)"""
    if rng.random() < 0.1:                                   # just stand: the flier columns need a spark to pass first
        wait = rng.choice([6, 12, 24, 40])
        ins, s = [], s0
        H0 = s0.height | s0.hh << 8
        for _ in range(wait):
            s = e.step((), 1)
            ins.append("")
            if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
                return None
        return (ins, s) if (s.z == 0 and (s.height | s.hh << 8) - H0 >= -4) else None
    w = rng.choice([0, 0, 0, 0, 1, 2, 4, 8, 16, 32])
    d = rng.choice(["Right", "Left", None, None])
    walk = rng.random() < 0.2
    if walk and d is None:
        d = rng.choice(["Right", "Left"])
    n = rng.choice([0, 0, 2, 4, 8, 12, 16, 24, 32, 48, 64]) if d else 0
    if walk:
        n = rng.choice([8, 16, 24, 32, 48])
    h = 0 if walk else rng.choice([4, 8, 10, 11, 12, 13, 14, 16, 20, 26, 32])
    da = rng.choice([d, d, "Right", "Left", None])
    dash = n >= 10 and rng.random() < 0.6
    seq = [()] * w
    if d and n:
        seq += ([(d,), ()] if dash else []) + [(d,)] * n
    seq += [tuple(x for x in (da, "A") if x)] * h
    ins, s, air = [], s0, False
    H0 = s0.height | s0.hh << 8
    for j in range(125):
        inp = seq[j] if j < len(seq) else ((da,) if (da and not walk) else ())
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
            return None
        H = s.height | s.hh << 8
        if walk:
            if j >= len(seq) + 1:
                return (ins, s) if (s.z == 0 and 1 <= s.anim <= 8 and H - H0 >= -4) else None
        elif j >= len(seq) - h:
            if s.z != 0:
                air = True
            elif air and 1 <= s.anim <= 8:
                return (ins, s) if H - H0 >= -4 else None
    return None


def main():
    goal = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    tries = int(sys.argv[2]) if len(sys.argv) > 2 else 70
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=f"early_l8climb_{goal}.log", fields=F)
    e.load("cap14_f12000")
    for i in range(12000, START):
        s = e.step(bt(lines[i]), 1)
    base = s.height | s.hh << 8
    # up14's own milestones from the per-frame RAM capture: first frame standing at +g px (frames since the placement)
    marks = {}
    with open(LOGS_DIR / "cap14.ram", "rb") as R:
        for f in range(START, 15660):
            R.seek((f - 1) * 2048)
            m = R.read(2048)
            dh0 = (m[0x439] | m[0x42A] << 8) - base
            for g in list(range(100, 4100, 100)) + [130, 330, 460]:
                if g not in marks and dh0 >= g and m[0x475] == 0:
                    marks[g] = f - START
    UP14.clear()
    UP14.update(marks)
    ins0, lands0 = [], []
    if len(sys.argv) > 4:                                    # resume: a saved milestone (early_l8climb_mark<g>.json) is the new root
        mk = json.load(open(sys.argv[4]))
        ins0, lands0 = list(mk["inputs"]), list(mk.get("landings", []))
        for b in ins0:
            s = e.step(bt(b), 1)
        print(f"resumed from {sys.argv[4]}: {len(ins0)} frames in, +{(s.height | s.hh << 8) - base} px", flush=True)
    heap, seq_no, cells, expanded = [(len(ins0), 0, e.msave(), ins0, s, lands0)], 0, {}, 0
    best_by_mark, result = {}, None
    while heap:
        frames, _, sid, ins, st, lands = heapq.heappop(heap)
        dh = (st.height | st.hh << 8) - base
        for g in sorted(UP14):
            if dh >= g and g not in best_by_mark:
                best_by_mark[g] = frames
                print(f"  +{g} px: standing after {frames} frames (up14 {UP14[g]}): {UP14[g] - frames:+d}   [expanded {expanded}, queue {len(heap)}]", flush=True)
                if g % 200 == 0:
                    json.dump({"from_frame": START, "inputs": ins, "landings": lands, "reached_px": dh, "frames": frames, "up14_frames": UP14[g]},
                              open(LOGS_DIR / "fix" / f"early_l8climb_mark{g}{TAG}.json", "w"))
        top = max(best_by_mark) if best_by_mark else 0
        if dh < top - 400:                                   # a straggler far below the front: drop it
            e.mfree(sid)
            continue
        if dh >= goal:
            result = (frames, ins, lands)
            break
        cell = (dh // 16, st.x // 32, frames // 48)          # the same spot later is a different node: things up here run on the clock
        if cells.get(cell, 0) >= CELL:
            e.mfree(sid)
            continue
        cells[cell] = cells.get(cell, 0) + 1
        expanded += 1
        kids = {}
        for _ in range(tries):
            e.mload(sid)
            r = candidate(e, st, rng)
            if r is None:
                continue
            ci, cs = r
            k = (((cs.height | cs.hh << 8) - base) // 16, cs.x // 12, len(ci) // 24 if all(b == "" for b in ci) else -1)   # waits of different length are different moves
            if k not in kids or len(ci) < len(kids[k][0]):
                if k in kids:
                    e.mfree(kids[k][2])
                kids[k] = (ci, cs, e.msave())
        for ci, cs, csid in kids.values():
            seq_no += 1
            heapq.heappush(heap, (frames + len(ci), seq_no, csid, ins + ci, cs, lands + [(frames + len(ci), cs.x, (cs.height | cs.hh << 8) - base)]))
        e.mfree(sid)
    if result:
        frames, ins, lands = result
        ref = UP14.get(goal)
        json.dump({"from_frame": START, "inputs": ins, "landings": lands, "goal_px": goal, "frames": frames, "up14_frames": ref},
                  open(LOGS_DIR / "fix" / f"early_l8climb_{goal}{TAG}.json", "w"))
        print(f"RESULT: +{goal} px in {frames} frames from the placement (up14: {ref}); saves {ref - frames if ref else '?'}; {expanded} nodes expanded", flush=True)
    else:
        print(f"no line reaches +{goal} px; marks {best_by_mark}", flush=True)
    e.close()


if __name__ == "__main__":
    main()

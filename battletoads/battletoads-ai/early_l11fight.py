"""EARLY track (2026-10-09): the Buzzball (Clinger-Winger's boss) once more, with the hit-by-hit beam that worked on
Robo-Manus, on a snapshot of up14.

up14: the ball appears on frame 34938; hits at +28, 98, 124, 164, 204, 246, 297, 356, 427, 588, 618, 697, 774 (dead).
The 1-player TAS: +30, 98, 122, 162, 204, 249, 294, 339, 384, 429, 474, 519, 564.  From its sixth hit the TAS kicks
only when the ball is back on the floor (h 47-48), from 30-34 px away, every 45 frames; five of its kicks use Left+Right
to stay put, the legal ones (Right for one frame, then B) creep 3 px each.  up14 kicks sooner, from 12-16 px, and loses
the ball at the wall after the eighth hit.

Node = the state right after a hit (the ball's health dropped by 16).  Candidate = one randomised cycle:
    wait to land -> walk Left n frames (retreat) -> stand until the ball is at or under height HT and the toad is at least
    D px left of it (give up after 70 frames) -> Right for one frame, B -> wait for the hit
with Select on random waiting frames.  Kept when the ball loses 16 and the toad nothing.  Nodes are ranked by frames
plus L11_PEN (6) per pixel the toad stands right of x 1748; the W best per hit are expanded.

    python early_l11fight.py [width=10] [tries=80] [out=l11fight_a] [seed=1] [root frame = 35036 (after up14's 2nd hit)]
    -> logs/fix/early_<out>.json {inputs from the root frame, hits}
"""
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oxh{q}"] = 0x3EE + q
    F[f"oh{q}"] = 0x439 + q
    F[f"op{q}"] = 0x51A + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
FIRST_SEEN, UP14_KILL = 34938, 34938 + 774
PEN = float(__import__("os").environ.get("L11_PEN", 6))        # frames charged per pixel the toad stands right of x 1748 after a hit


def ball(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x7B:
            return s[f"ox{q}"] | s[f"oxh{q}"] << 8, s[f"oh{q}"], s[f"op{q}"]
    return None


def grounded(s):
    return s.z == 0 and 1 <= s.anim <= 8


def loose(e, s0, rng):
    """fallback when the ball has left the wall: face it, keep 22-40 px away, kick when it is low; up to 220 frames"""
    ht = rng.choice([48, 54, 60, 70, 90])
    near, far = rng.choice([(18, 34), (22, 40), (26, 44)])
    p_sel = rng.choice([0.0, 0.1, 0.25])
    b0 = ball(s0)
    s, ins, prev_h, kick, cool = s0, [], b0[1], [], 0
    tx = lambda t: t.x | t.xh << 8
    for _ in range(220):
        b = ball(s)
        if b is None:
            return (ins, s) if b0[2] <= 16 else None
        dx = b[0] - tx(s)
        d = "Right" if dx >= 0 else "Left"
        away = "Left" if dx >= 0 else "Right"
        inp = ()
        if kick:
            inp = kick.pop(0)
        elif cool > 0:
            cool -= 1
        elif grounded(s):
            if abs(dx) > far:
                inp = (d,)
            elif abs(dx) < near:
                inp = (away,)
            elif b[1] <= ht and b[1] <= prev_h:
                kick, cool = [(d,), ("B",)], 30
                inp = kick.pop(0)
            elif rng.random() < p_sel:
                inp = ("Select",)
        prev_h = b[1]
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 10:
            return None
        b2 = ball(s)
        if b2 is None:
            return (ins, s) if b0[2] <= 16 else None
        if b2[2] <= b0[2] - 16 or (b2[2] < b0[2] and b0[2] <= 16):   # a full hit, or the last one (15 left: any hit kills)
            return ins, s
        if b2[2] < b0[2]:
            return None
    return None


def candidate(e, s0, rng):
    n_left = rng.choice([0, 0, 4, 8, 12, 16, 20, 24, 30, 36, 44])
    ht = rng.choice([46, 48, 50, 54, 60, 70, 90])
    dmin = rng.choice([14, 18, 22, 26, 30, 34])
    p_sel = rng.choice([0.0, 0.05, 0.15, 0.3])
    style = rng.choice(["tapB", "tapB", "RB", "B"])
    jitter = rng.choice([0, 0, 1, 2, 3])
    b0 = ball(s0)
    if b0 is None:
        return None
    s, ins, phase, cnt, waited, prev_h = s0, [], "land", 0, 0, b0[1]
    tx = lambda t: t.x | t.xh << 8
    for _ in range(150):
        b = ball(s)
        if b is None:
            return (ins, s) if b0[2] <= 16 else None        # the ball is gone: dead
        inp = ()
        if phase == "land":
            if grounded(s):
                phase, cnt = "retreat", n_left
            elif rng.random() < p_sel:
                inp = ("Select",)
        if phase == "retreat":
            if cnt > 0:
                inp = ("Left",)
                cnt -= 1
            else:
                phase = "watch"
        if phase == "watch":
            falling = b[1] <= prev_h
            if b[1] <= ht and falling and b[0] - tx(s) >= dmin and grounded(s):
                if cnt < jitter:
                    cnt += 1
                else:
                    phase, cnt = "kick", 0
            else:
                waited += 1
                if waited > 70:
                    return None
                if rng.random() < p_sel:
                    inp = ("Select",)
        if phase == "kick":
            seq = {"tapB": [("Right",), ("B",)], "RB": [("Right", "B")], "B": [("B",)]}[style]
            if cnt < len(seq):
                inp = seq[cnt]
                cnt += 1
            else:
                phase, cnt = "after", 0
        elif phase == "after":
            cnt += 1
            if cnt > 34:
                return None
        prev_h = b[1]
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 10:
            return None
        b2 = ball(s)
        if b2 is None:
            return (ins, s) if b0[2] <= 16 else None
        if b2[2] <= b0[2] - 16 or (b2[2] < b0[2] and b0[2] <= 16):   # a full hit, or the last one (15 left: any hit kills)
            return ins, s
        if b2[2] < b0[2]:
            return None                                       # a weak hit (2-8): not wanted
    return None


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    tries = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    out = sys.argv[3] if len(sys.argv) > 3 else "l11fight_a"
    rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
    root_frame = int(sys.argv[5]) if len(sys.argv) > 5 else 35036
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=f"early_{out}.log", fields=F)
    e.load("cap14_f34000")
    s = None
    for i in range(34000, root_frame):
        s = e.step(bt(lines[i]), 1)
    print(f"root {root_frame} (+{root_frame - FIRST_SEEN} after the ball appears): toad x {s.x | s.xh << 8} h {s.height} ball {ball(s)} hp {s.hp}", flush=True)
    nodes = [{"sid": e.msave(), "ins": [], "state": s, "hits": []}]
    best = nodes[0]
    for level in range(1, 16):
        kids = []
        for nd in nodes:
            for _ in range(tries):
                e.mload(nd["sid"])
                r = candidate(e, nd["state"], rng)
                if r is None:
                    continue
                ins, s2 = r
                kids.append({"ins": nd["ins"] + ins, "state": s2, "hits": nd["hits"] + [len(nd["ins"]) + len(ins)], "sid": e.msave()})
        if not kids:                                             # the ball got away: chase it
            for nd in nodes:
                for _ in range(tries):
                    e.mload(nd["sid"])
                    r = loose(e, nd["state"], rng)
                    if r is None:
                        continue
                    ins, s2 = r
                    kids.append({"ins": nd["ins"] + ins, "state": s2, "hits": nd["hits"] + [len(nd["ins"]) + len(ins)], "sid": e.msave()})
        if not kids:
            print(f"hit {level}: no candidate lands a full hit - stopped", flush=True)
            break
        cost = lambda k: len(k["ins"]) + PEN * max(0, (k["state"].x | k["state"].xh << 8) - 1748)
        kids.sort(key=lambda k: (cost(k), rng.random()))
        keep, seen = [], {}
        for k in kids:
            key = (len(k["ins"]), (k["state"].x | k["state"].xh << 8) // 4)
            if len(keep) < width and seen.get(key, 0) < 2:
                keep.append(k)
                seen[key] = seen.get(key, 0) + 1
            else:
                e.mfree(k["sid"])
        for nd in nodes:
            e.mfree(nd["sid"])
        nodes = keep
        best = nodes[0]
        b = ball(best["state"])
        prev = best["hits"][-2] if len(best["hits"]) > 1 else 0
        print(f"hit {level}: {len(kids)} landed; best +{len(best['ins'])} (interval {best['hits'][-1] - prev}) toad x {best['state'].x | best['state'].xh << 8} ball {b}; "
              f"kept {[(len(k['ins']), k['state'].x | k['state'].xh << 8) for k in nodes]}", flush=True)
        json.dump({"root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"], "partial": True},
                  open(LOGS_DIR / "fix" / f"early_{out}_partial.json", "w"))
        done = [k for k in nodes if ball(k["state"]) is None or ball(k["state"])[2] == 0 or len(k["hits"]) >= 11]
        if done:
            best = done[0]
            break
    b = ball(best["state"])
    dead = b is None or b[2] == 0
    json.dump({"root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"], "dead": dead, "kill_frame_abs": root_frame + len(best["ins"]),
               "up14_kill_frame": UP14_KILL}, open(LOGS_DIR / "fix" / f"early_{out}.json", "w"), indent=1)
    print(f"RESULT {out}: {len(best['hits'])} hits in {len(best['ins'])} frames from the root, ball dead={dead}; last hit at +{root_frame + len(best['ins']) - FIRST_SEEN} "
          f"after it appears (up14 +774, TAS +564); saves {UP14_KILL - root_frame - len(best['ins']) if dead else 'n/a'}", flush=True)
    e.close()


if __name__ == "__main__":
    main()

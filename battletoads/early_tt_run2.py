"""EARLY track (2026-10-09): Terra Tubes staircase top, part 2 - after the sprint pass, get into the tank's water.

early_tt_run.py: from up14 frame 25186 a sprint + dash jump (wait 1, tap Right, gap, Right..., at x >= 776 release one
frame, Right+A x2, Right) carries the toad THROUGH both bugs (x 824 / 840) at 3 px/frame without a grab; holding Right
it then hits something at (915, 6414).  The record drops off the top's right end into the blue tank and swims down-
right under the star chain.  Scan the air control after the pass: from x >= X0 press `mid` (nothing / Left / Down)
for k frames, then `end` (Right / nothing / Left) - report grabbed, hurt, landed (z 0) or SWIMMING (anim 98/99).

    python early_tt_run2.py   -> logs/fix/early_tt_run2.txt (+ early_tt_swim_best.json: inputs from frame 25186)
"""
import itertools
import json

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5,
     "hp": 0x51A, "lives": 0x11, "camx": 0x87, "camxh": 0x88, "spd": 0x565}
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oxh{q}"] = 0x3EE + q
    F[f"oh{q}"] = 0x439 + q
    F[f"ohh{q}"] = 0x42A + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ROOT = 25186
PASS = [(), ("Right",), ()] + [("Right",)] * 4          # then Right until x >= 776, one released frame, Right+A x2 (built below)


def bugs(s):
    return [(s[f"ox{q}"] | s[f"oxh{q}"] << 8, s[f"oh{q}"] | s[f"ohh{q}"] << 8) for q in range(1, 15) if s[f"id{q}"] == 0x74]


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_tt_run2.log", fields=F)
    e.load("cap14_f25000")
    for i in range(25000, ROOT):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    out, stats, swims = [], {}, []
    for x0, k, mid, end in itertools.product(range(836, 912, 4), (2, 4, 6, 8, 12, 16, 20, 26, 32, 40, 60), ("", "Left", "Down"), ("Right", "", "Left")):
        e.mload(root)
        t, ph, cnt, ins, res, kk = s, 0, 0, [], None, 0
        for j in range(200):
            x = t.x | t.xh << 8
            if j == 0:
                inp = ()
            elif j == 1:
                inp = ("Right",)
            elif j == 2:
                inp = ()
            else:
                inp = ("Right",)
                if ph == 0 and x >= 776 and t.z == 0:
                    ph, inp = 1, ()
                elif ph == 1:
                    inp = ("Right", "A")
                    cnt += 1
                    if cnt == 2:
                        ph = 2
                elif ph == 2 and x >= x0:
                    ph = 3
                if ph == 3:
                    if kk < k:
                        inp = bt(mid)
                        kk += 1
                    else:
                        inp = bt(end)
            t = e.step(inp, 1)
            ins.append("+".join(inp))
            x, H = t.x | t.xh << 8, t.height | t.hh << 8
            if t.anim in (36, 37):
                res = ("grabbed", j + 1, x, H)
                break
            if t.hp < 47 or t.lives < s.lives:
                res = ("hurt", j + 1, x, H)
                break
            if t.anim in (98, 99):
                res = ("SWIM", j + 1, x, H, t.camx | t.camxh << 8, bugs(t))
                break
            if ph == 3 and t.z == 0 and j > 40:
                res = ("landed", j + 1, x, H)
                # keep going a little: does a bug come?
        res = res or ("air/timeout", 200, t.x | t.xh << 8, t.height | t.hh << 8)
        stats[res[0]] = stats.get(res[0], 0) + 1
        if res[0] == "SWIM":
            swims.append((res[1], res, (x0, k, mid, end), ins))
        elif res[0] in ("landed",):
            out.append(f"x0 {x0} k {k} mid '{mid}' end '{end}': {res}")
    swims.sort(key=lambda z: z[0])
    out.insert(0, f"stats {stats}")
    for fr, res, P, ins in swims[:25]:
        out.insert(1, f"SWIM: x0 {P[0]} k {P[1]} mid '{P[2]}' end '{P[3]}': {res}")
    if swims:
        json.dump({"from_frame": ROOT, "inputs": swims[0][3], "result": swims[0][1], "params": swims[0][2]},
                  open(LOGS_DIR / "fix" / "early_tt_swim_best.json", "w"))
    print("\n".join(l[:300] for l in out[:40]), flush=True)
    open(LOGS_DIR / "fix" / "early_tt_run2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

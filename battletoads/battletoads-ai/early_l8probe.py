"""EARLY track (2026-10-09): Robo-Manus mechanics probe on a snapshot of up14 (no route is built).

1. From up14 frame 15790 (control after the arrival cutscene) run to the boss the TAS's way (tap, gap, hold Right,
   one released frame, Right+B) for several stopping distances and report which attack comes out.
2. From the state right after the first smash: wait until the toad has landed, press direction+B on the next frame,
   with Select pressed on ONE earlier frame k (k = none, 0..16) - does the dice re-roll change the attack (38 = the
   jump-smash, 24/28 punch, 31/30 kick, 49 ram) and does it hit?
    -> logs/fix/early_l8probe.txt
"""
import sys

from toads.emulator import BizHawk, LOGS_DIR

ROOT_FRAME = 15790
F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "z": 0x475, "anim": 0x3B5, "st": 0x4B1, "hp": 0x51A,
     "face": 0x4A2, "lives": 0x11, "spd": 0x565}
for k in range(6):
    F[f"sc{k}"] = 0x5F4 + k
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oh{q}"] = 0x439 + q
    F[f"oa{q}"] = 0x3B5 + q
    F[f"os{q}"] = 0x4B1 + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
score = lambda s: int("".join(str(s[f"sc{k}"] & 15) for k in range(6)))
out = []


def say(*a):
    t = " ".join(str(x) for x in a)
    print(t, flush=True)
    out.append(t)


def boss(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x7D:
            return s[f"ox{q}"], s[f"oh{q}"], s[f"oa{q}"], s[f"os{q}"]
    return None


def grounded(s):
    return s.z == 0 and 1 <= s.anim <= 8


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8probe.log", fields=F)
    e.load("cap14_f15000")
    for i in range(15000, ROOT_FRAME):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    say(f"root {ROOT_FRAME}: toad x {s.x} anim {s.anim} boss {boss(s)} timer {s.timer}")
    # 1. the approach: run n frames, release g, press
    first = None
    for n in (28, 29, 30, 31, 32, 33):
        for g in (0, 1, 2):
            e.mload(root)
            seq = [("Right",), ()] + [("Right",)] * n + [()] * g + [("Right", "B")] + [("Right",)] * 8 + [()] * 30
            sc0, att, hit, xs = score(s), None, None, None
            for j, b in enumerate(seq):
                t = e.step(b, 1)
                if j == 2 + n + g:
                    att, xs = t.anim, t.x
                if hit is None and score(t) != sc0:
                    hit = (j + 1, boss(t))
                    if att == 38 and first is None:
                        first = (e.msave(), t, j + 1)
            say(f"approach run {n} gap {g}: B at x {xs} -> attack anim {att}, hit {hit}")
    if first is None:
        say("no smash on the approach")
        e.close()
        return
    sid, s1, n1 = first
    say(f"node after hit 1 at +{n1}: toad x {s1.x} h {s1.height} anim {s1.anim} st {s1.st} boss {boss(s1)} timer {s1.timer}")
    # 2. the next cycle, with one Select at frame k
    for k in [None] + list(range(0, 20)):
        for extra in (0, 1, 2):
            e.mload(sid)
            t, j, pressed, att, hit, landed, log = s1, 0, None, None, None, None, []
            sc0 = score(s1)
            while j < 60:
                b = boss(t)
                dirn = "Right" if b and b[0] >= t.x else "Left"
                if pressed is None and grounded(t):
                    if landed is None:
                        landed = j
                    if j - landed >= extra:
                        inp = (dirn, "B")
                        pressed = j
                    else:
                        inp = ()
                elif pressed is not None and j - pressed <= 5:
                    inp = (dirn,)
                else:
                    inp = ("Select",) if k == j else ()
                t = e.step(inp, 1)
                j += 1
                if pressed is not None and j == pressed + 1:
                    att = t.anim
                if hit is None and score(t) != sc0:
                    hit = j
                    bh = boss(t)
            b2 = boss(t)
            say(f"select@{k} extra {extra}: landed {landed} B at {pressed} -> attack {att}, hit at {hit} (boss then {bh if hit else None}); boss at +60: {b2}, toad x {t.x} anim {t.anim} hp {t.hp}")
    open(LOGS_DIR / "fix" / "early_l8probe.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

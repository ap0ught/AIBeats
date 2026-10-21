"""EARLY track (2026-10-09): Robo-Manus arrival, part 2.  early_l8arrive.py: if up14's LAST climb jump (frame 15597) is
steered right (Right+A x16, Right to the landing at x 189, Right until the cutscene starts with the toad at x 244) the
cutscene animation (50) ends at frame 15694 instead of 15789.  Is that real control 95 frames early?  Print the
timeline, then test: stand still vs. attack the boss as early as possible (direction+B on every frame from k).

    python early_l8arrive2.py   -> logs/fix/early_l8arrive2.txt
"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "z": 0x475, "anim": 0x3B5, "st": 0x4B1, "hp": 0x51A, "spd": 0x565,
     "lives": 0x11}
for k in range(6):
    F[f"sc{k}"] = 0x5F4 + k
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oh{q}"] = 0x439 + q
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
            return s[f"ox{q}"], s[f"oh{q}"]
    return None


PRE = [("Right", "A")] * 16 + [("Right",)] * 41          # frames 15597..15653: jump right, keep right (lands 15623 at x 189)


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8arrive2.log", fields=F)
    e.load("cap14_f15000")
    for i in range(15000, 15596):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    # 1. timeline with no input after the cutscene starts
    t, f = s, 15596
    for b in PRE:
        t = e.step(b, 1)
        f += 1
    say(f"after the steered jump, frame {f}: toad x {t.x} h {t.height} anim {t.anim} boss {boss(t)}")
    cut = e.msave()
    prev = None
    for j in range(220):
        t = e.step((), 1)
        f += 1
        key = (t.anim, t.st, t.z)
        if key != prev or j % 20 == 0:
            say(f"  {f}: toad x {t.x} h {t.height} z {t.z} anim {t.anim} st {t.st} hp {t.hp} boss {boss(t)} timer {t.timer}")
            prev = key
    # 2. when does input count?  Walk Left from frame k: the first frame x changes differently from the idle run
    for k in (15680, 15690, 15694, 15696, 15700, 15705, 15710):
        e.mload(cut)
        t, f, moved = None, 15653, None
        for j in range(120):
            f += 1
            t = e.step(("Left",) if f >= k else (), 1)
            if moved is None and f >= k and t.anim in (3, 4, 5, 6, 7, 8) :
                moved = (f, t.x, t.anim)
        say(f"hold Left from {k}: first walking frame {moved}; at {f}: x {t.x} anim {t.anim} hp {t.hp} boss {boss(t)}")
    # 3. earliest hit: direction+B pressed fresh at frame k (then direction held 5), standing where the cutscene leaves the toad
    for k in list(range(15690, 15740, 2)):
        e.mload(cut)
        t, f, hit, att = None, 15653, None, None
        sc0 = None
        for j in range(140):
            f += 1
            if sc0 is None:
                sc0 = score(e.state())
            if f < k:
                inp = ()
            else:
                b = boss(t) if t is not None else None
                dirn = "Right" if (b and b[0] >= t.x) else "Left"
                inp = (dirn, "B") if f == k else ((dirn,) if f <= k + 5 else ())
            t = e.step(inp, 1)
            if f == k + 1:
                att = t.anim
            if hit is None and score(t) != sc0:
                hit = (f, boss(t), t.x, t.height)
        say(f"B at {k}: attack anim {att}, first hit {hit}; at {f}: toad x {t.x} anim {t.anim} hp {t.hp} boss {boss(t)}")
    open(LOGS_DIR / "fix" / "early_l8arrive2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

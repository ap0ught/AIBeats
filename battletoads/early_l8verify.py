"""EARLY track (2026-10-09): independent replay of the Robo-Manus proof (early_l8fight.py result) on up14's snapshot,
through the level's end into Terra Tubes.

    up14 inputs to frame <arrival_from_frame>, the arrival prefix, the fight inputs, then nothing until the boss's
    death animation ends, then a fresh A / B press on alternate frames (early_mash.py: 2-3 frames faster than A/-)
Reports the kill frame, the frame the level byte leaves 7, the first black frame is not measured here; the frame the
toad is placed in Terra Tubes, hp / lives / score there, all against up14 (kill 16877, byte change 17318, placement
17366 by the same detector).  Nothing is written into a route.

    python early_l8verify.py [logs/fix/early_l8fight_e.json]   -> logs/fix/early_l8verify.txt
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
for k in range(6):
    F[f"sc{k}"] = 0x5F4 + k
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
score = lambda s: int("".join(str(s[f"sc{k}"] & 15) for k in range(6)))


def tail(e, first_frame, feed, limit=900):
    """step until the toad is placed in Level 9 (byte 11); feed(j) gives the input of step j"""
    f, stage, left, kill, placed, minhp, prev_sc = first_frame, 0, None, None, None, 99, None
    s = None
    for j in range(limit):
        s = e.step(feed(j), 1)
        f += 1
        if s.level == 7:
            minhp = min(minhp, s.hp)
            sc = score(s)
            if prev_sc is not None and sc - prev_sc >= 10000 and kill is None:
                kill = f
            prev_sc = sc
        if left is None and s.level in (254, 255):
            left = f
        if stage == 0 and s.level == 11:
            stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            placed = f
            break
    return dict(kill=kill, level_left=left, placed=placed, hp=s.hp, lives=s.lives, score=score(s), min_hp_in_level=minhp)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else str(LOGS_DIR / "fix" / "early_l8fight_e.json")
    j = json.load(open(src))
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8verify.log", fields=F)
    out = []
    # reference: up14 itself from frame 15596
    e.load("cap14_f15000")
    for i in range(15000, 15596):
        e.step(bt(lines[i]), 1)
    ref = tail(e, 15596, lambda k: bt(lines[15596 + k]), limit=2000)
    out.append(f"up14      : {ref}")
    print(out[-1], flush=True)
    # the proof
    start = j.get("arrival_from_frame", j["root_frame"])
    seq = list(j.get("arrival_prefix", [])) + list(j["inputs"])
    for label, mash in (("A/B mash", [("A",), ("B",)]), ("A/- mash", [("A",), ()])):
        e.load("cap14_f15000")
        for i in range(15000, start):
            e.step(bt(lines[i]), 1)
        n = len(seq)

        def feed(k):
            if k < n:
                return bt(seq[k])
            return mash[(k - n) % 2] if k - n >= 300 else ()        # the boss's death takes ~440 frames; presses before that only make the toad jump
        res = tail(e, start, feed, limit=n + 700)
        out.append(f"new {label}: {res}")
        if res["placed"] and ref["placed"]:
            out.append(f"   Terra Tubes placement {res['placed']} vs {ref['placed']}: {ref['placed'] - res['placed']} frames earlier; "
                       f"kill {res['kill']} vs {ref['kill']} ({(ref['kill'] or 0) - (res['kill'] or 0)} earlier); hp {res['hp']} lives {res['lives']} (up14 {ref['hp']}/{ref['lives']}); "
                       f"lowest hp during the fight {res['min_hp_in_level']}")
        print("\n".join(out[-2:]), flush=True)
    open(LOGS_DIR / "fix" / "early_l8verify.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

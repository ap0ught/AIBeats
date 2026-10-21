"""EARLY track (2026-10-09): Karnath's Lair, the warp room - the record's line, read off its video frame by frame
(logs/fix/wr_karnath_1.jpg, wr_karnath_2.jpg; 0.1-s steps):

    snake clock S = frames since the head starts to rise (up14: room frame r+71, r = frames since 11910)
    S ~43  the toad JUMPS from the floor at the snake and grabs its body ~60 px up (up14 starts climbing at S 37 from
           the floor and climbs at 2.4 px/f)
    S ~49..107  climbs (mash) and catches the head (the head rises 2 px/f)
    S ~110 goes OVER the still-rising head to the right: a jump that passes ~55 px above the first star (world x 231,
           H ~7647) and then falls under the next two (x 316 / 351, H ~7677) onto the portal's ledge (H 7518)
    black ~S 205-210.  up14: on the ledge at r+332, portal at r+357 (S 286).  About 80-100 frames.
Earlier probes (tubeclimb.py, 2026-10-06) reached the head early but every flight died on the stars at x 257-290.

Random scan on a snapshot of up14 (root = frame 11910, the toad appearing in the room):
    walk to x0, wait, at S=sj press Right+A for a frames, then mash Left+A / Right+A (period p) while on the snake,
    when the toad is within `top` px of the head's height: Right+A for n frames, then Right (optionally release
    Right for `rel` frames after `hold` frames to steepen the fall)
Outcome: portal engaged (routine pointer $E50D) with hp 47 and no life lost -> frame.

    python early_l6fling.py [tries=1500] [seed=1]   -> logs/fix/early_l6fling.txt, best inputs logs/fix/early_l6fling_best.json
"""
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5,
     "hp": 0x51A, "lives": 0x11, "spd": 0x565, "rtnL": 0x23, "rtnH": 0x24}
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oxh{q}"] = 0x3EE + q
    F[f"oh{q}"] = 0x439 + q
    F[f"ohh{q}"] = 0x42A + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ROOT = 11910
UP14_PORTAL = 12282 - ROOT          # frame the routine pointer is $E50D in up14 (black at 12267: the screen fades first)


def head(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x4C:
            return s[f"ox{q}"] | s[f"oxh{q}"] << 8, s[f"oh{q}"] | s[f"ohh{q}"] << 8
    return None


def trial(e, root, s0, P, keep=False):
    e.mload(root)
    s, ins, r = s0, [], 0
    phase, cnt, on_snake, tlog = "walk", 0, None, []
    result = {"P": P}
    while r < 330:
        x, H = s.x | s.xh << 8, s.height | s.hh << 8
        hd = head(s)
        S = r - 71
        inp = ()
        if phase == "walk":
            if S >= P["sj"]:
                phase, cnt = "jump", P["a"]
            elif abs(x - P["x0"]) > 1 and s.z == 0:
                inp = ("Right",) if x < P["x0"] else ("Left",)
        if phase == "jump":
            if cnt > 0:
                inp = ("Right", "A")
                cnt -= 1
            else:
                phase = "climb"
        if phase == "climb":
            if s.anim in (88, 89) and on_snake is None:
                on_snake = (r, x, H)
            if hd and on_snake and H >= hd[1] + P["top"]:
                phase, cnt = "over", P["n"]
                result["over_at"] = (r, x, H, hd)
            else:
                k = (r // P["p"]) % 2
                inp = ("Left", "A") if k == 0 else ("Right", "A")
                if on_snake is None and s.z == 0 and r - 71 > P["sj"] + P["a"] + 12:
                    result["fail"] = "never grabbed"
                    break
        if phase == "over":
            if cnt > 0:
                inp = ("Right", "A")
                cnt -= 1
            else:
                phase, cnt = "fly", 0
        if phase == "fly":
            cnt += 1
            inp = () if P["hold"] <= cnt < P["hold"] + P["rel"] else ("Right",)
        s = e.step(inp, 1)
        r += 1
        ins.append("+".join(inp))
        if s.hp < 47 or s.lives < s0.lives:
            result["fail"] = f"hurt at r+{r} x {s.x | s.xh << 8} H {s.height | s.hh << 8} phase {phase}"
            break
        if s.rtnL == 0x0D and s.rtnH == 0xE5:
            result["portal"] = r
            break
    result["grab"] = on_snake
    result["end"] = (r, s.x | s.xh << 8, s.height | s.hh << 8, s.z, s.anim)
    if keep:
        result["inputs"] = ins
    return result


def main():
    tries = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l6fling.log", fields=F)
    e.load("cap14_f11000")
    s = None
    for i in range(11000, ROOT):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    out = [f"root {ROOT}: toad x {s.x | s.xh << 8} H {s.height | s.hh << 8} head {head(s)}; up14 engages the portal at r+{UP14_PORTAL}"]
    print(out[-1], flush=True)
    best, stats = None, {}
    for t in range(tries):
        P = {"x0": rng.choice([60, 64, 68, 72, 76, 80, 84, 88, 92, 96]), "sj": rng.randint(28, 62), "a": rng.choice([2, 3, 4, 6, 8, 10, 12, 16, 20]),
             "p": rng.choice([1, 1, 1, 2, 4]), "top": rng.choice([-30, -24, -18, -12, -6, 0, 6, 12, 16, 20, 26]),
             "n": rng.choice([1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32]), "hold": rng.choice([999, 999, 20, 30, 40, 50, 60]),
             "rel": rng.choice([4, 8, 12, 20])}
        res = trial(e, root, s, P)
        key = "portal" if "portal" in res else (res.get("fail", "timeout").split(" at ")[0])
        stats[key] = stats.get(key, 0) + 1
        if "portal" in res or (t % 100 == 0):
            line = f"{t}: {('PORTAL r+%d (up14 %d, saves %d)' % (res['portal'], UP14_PORTAL, UP14_PORTAL - res['portal'])) if 'portal' in res else res.get('fail', 'timeout')} | grab {res['grab']} over {res.get('over_at')} end {res['end']} | {P}"
            out.append(line)
            print(line, flush=True)
        if "portal" in res and (best is None or res["portal"] < best["portal"]):
            best = trial(e, root, s, P, keep=True)
            json.dump({"from_frame": ROOT, "inputs": best["inputs"], "portal_r": best["portal"], "up14_portal_r": UP14_PORTAL, "params": P},
                      open(LOGS_DIR / "fix" / "early_l6fling_best.json", "w"))
    out.append(f"stats {stats}; best {best['portal'] if best else None} (up14 {UP14_PORTAL})")
    print(out[-1], flush=True)
    open(LOGS_DIR / "fix" / "early_l6fling.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

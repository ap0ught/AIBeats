"""EARLY track (2026-10-09): Terra Tubes, the staircase top - is the bugs' grab avoidable by SPEED?

The record (logs/fix/wr_tt_1.jpg, wr_tt_2.jpg) runs up the pink staircase, along its top and off its right end into
the blue tank without a pause.  The 1-player TAS runs under the two hovering bugs (0x74 at x 824 / 840, 26-32 px above
the floor) at 3 px/frame and is not grabbed.  up14 walks (2 px/frame) and jumps into one; first version of this probe:
walking or crouch-walking under them is ALWAYS grabbed at x 818-822 (Select does not change it: no dice involved).

Probe on the up14 snapshot at frame 25186 (toad standing at (759,6534) on the structure left of the top):
    wait w, tap Right, gap, hold Right (sprint 3 px/f at once), at x >= xj: [release 1 frame], Right+A for a frames
    (a sprint only survives a jump with that released frame), then Right; optional second jump at x >= xj2
Report (one line per variant, only non-grabbed ones in full): grabbed or not, swimming (anim 98/99) and where, camera.

    python early_tt_run.py   -> logs/fix/early_tt_run.txt
"""
import itertools

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


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_tt_run.log", fields=F)
    e.load("cap14_f25000")
    for i in range(25000, ROOT):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    out = [f"root {ROOT}: toad x {s.x | s.xh << 8} H {s.height | s.hh << 8} z {s.z} anim {s.anim} spd {s.spd}"]
    print(out[-1], flush=True)
    n = grabbed_n = 0
    good = []
    for w, xj, gap, a, xj2, a2 in itertools.product((0, 1, 2, 3), (764, 768, 772, 776, 780, 999), (0, 1), (2, 6, 10, 14), (999, 836, 842, 848, 854), (4, 12)):
        if xj == 999 and (gap or a != 2):
            continue
        if xj2 == 999 and a2 != 4:
            continue
        e.mload(root)
        t, grabbed, swim, ph, cnt, cnt2, track = s, None, None, 0, 0, 0, []
        for j in range(170):
            x = t.x | t.xh << 8
            if j < w:
                inp = ()
            elif j == w:
                inp = ("Right",)
            elif j == w + 1:
                inp = ()
            else:
                inp = ("Right",)
                if ph == 0 and x >= xj and t.z == 0:
                    ph, cnt = 1, a
                    if gap:
                        inp = ()
                if ph == 1 and not (gap and inp == ()):
                    if cnt > 0:
                        inp = ("Right", "A")
                        cnt -= 1
                    else:
                        ph = 2
                elif ph == 1 and gap and inp == ():
                    gap_used = True
                if ph in (0, 2) and x >= xj2 and cnt2 < a2 and (t.z == 0 or cnt2):
                    inp = ("Right", "A")
                    cnt2 += 1
            t = e.step(inp, 1)
            x, H = t.x | t.xh << 8, t.height | t.hh << 8
            if j % 10 == 9:
                track.append((j + 1, x, H, t.z, t.anim, t.spd, t.camx | t.camxh << 8))
            if grabbed is None and t.anim in (36, 37):
                grabbed = (j + 1, x, H)
                break
            if swim is None and t.anim in (98, 99):
                swim = (j + 1, x, H)
            if t.hp < 47 or t.lives < s.lives:
                track.append(("HURT", j + 1, x, H, t.anim))
                break
        n += 1
        if grabbed:
            grabbed_n += 1
        else:
            good.append((w, xj, gap, a, xj2, a2))
            line = f"NOT GRABBED w{w} jump@{xj} gap{gap} A{a} jump2@{xj2} A{a2}: swim {swim}; track (frame,x,H,z,anim,spd,camx) {track[-9:]}"
            out.append(line)
            if len(good) <= 12:
                print(line[:420], flush=True)
    out.append(f"{n} variants, {grabbed_n} grabbed, {len(good)} not grabbed")
    print(out[-1], flush=True)
    open(LOGS_DIR / "fix" / "early_tt_run.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

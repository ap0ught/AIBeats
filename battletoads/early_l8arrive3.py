"""EARLY track (2026-10-09): Robo-Manus arrival, part 3 - where to STAND when the cutscene starts.

Part 2: running into the wall (x 243-244) until the cutscene starts gets the toad flattened by the descending boss
(anim 85/86, hp reads 0 for ~120 frames, then it stands up with hp 47: slower than up14).  The TAS stands at x 244
for 18 frames before the cutscene, is walked left to 225 while the boss lands at 232 and is NOT flattened.
Scan: steer up14's last jump right (Right+A x16, lands x 189 at 15623), dash right, STOP at x >= X (release), stand.
Report for each X: flattened or not, the frame control returns and the toad's x there (up14: 15790 at x 128).

    python early_l8arrive3.py   -> logs/fix/early_l8arrive3.txt, best root saved as bookmark early_L8_arrive
"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "z": 0x475, "anim": 0x3B5, "st": 0x4B1, "hp": 0x51A, "spd": 0x565,
     "lives": 0x11}
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oh{q}"] = 0x439 + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
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


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8arrive3.log", fields=F)
    e.load("cap14_f15000")
    for i in range(15000, 15596):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    results = []
    for stop_x in (252, 244, 242, 240, 238, 236, 234, 232, 230, 228, 224, 220, 216, 212, 208, 200):
        for dash in (True, False):
            e.mload(root)
            t, f, ins, landed, tap, stopped = s, 15596, [], None, 0, False
            cut, ctrl, flat = None, None, False
            for j in range(260):
                if j < 16:
                    inp = ("Right", "A")
                elif landed is None:
                    inp = ("Right",)
                elif cut is None and not stopped:
                    if t.x >= stop_x:
                        stopped, inp = True, ()
                    elif dash and tap == 0:
                        tap, inp = 1, ()                           # release one frame = the gap of a double tap
                    else:
                        inp = ("Right",)
                else:
                    inp = ()
                t = e.step(inp, 1)
                f += 1
                ins.append("+".join(inp))
                if landed is None and j > 6 and t.z == 0 and t.height == 30:
                    landed = (f, t.x)
                if cut is None and t.anim == 50:
                    cut = (f, t.x)
                if t.anim in (85, 86):
                    flat = True
                if cut is not None and ctrl is None and t.anim not in (50, 85, 86) and t.hp == 47 and f > cut[0] + 5:
                    ctrl = (f, t.x)
                    break
            say(f"stop at x>={stop_x} dash {dash}: landed {landed}, cutscene from {cut}, flattened {flat}, control {ctrl}, boss {boss(t)}")
            if ctrl and not flat:
                results.append((ctrl[0] + abs(224 - ctrl[1]) / 3.0, ctrl, stop_x, dash, list(ins)))
    if results:
        results.sort(key=lambda r: r[0])
        est, ctrl, stop_x, dash, ins = results[0]
        say(f"BEST: stop at {stop_x} dash {dash}: control at frame {ctrl[0]} x {ctrl[1]} (up14: 15790 at x 128, 32 px/3 = ~32 f of running further away)")
        import json
        json.dump({"from_frame": 15596, "inputs": ins, "control": ctrl, "note": "replaces up14 inputs from frame 15597 to the control frame"},
                  open(LOGS_DIR / "fix" / "early_l8arrive_best.json", "w"))
    open(LOGS_DIR / "fix" / "early_l8arrive3.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

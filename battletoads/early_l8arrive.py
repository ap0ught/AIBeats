"""EARLY track (2026-10-09): Robo-Manus's arrival cutscene - where should the toad stand when it starts?

up14 lands on the arena floor at x 118 (frame 15616), idles, and the cutscene (toad anim 50, frames 15656-15789) walks
it to x 128; control comes back at 15790 and the run to the boss (x 232) costs 45 frames to the first smash.  The TAS
lands at x 244, is walked LEFT 51 px to x 193 and needs 21 frames.  Between the landing and the cutscene up14 has ~35
free frames: probe running right in them (double tap + hold N frames) and report the toad's x when control returns.

    python early_l8arrive.py   -> logs/fix/early_l8arrive.txt
"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "spd": 0x565}
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oh{q}"] = 0x439 + q
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)


def boss(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x7D:
            return s[f"ox{q}"], s[f"oh{q}"]
    return None


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8arrive.log", fields=F)
    e.load("cap14_f15000")
    for i in range(15000, 15620):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    out = [f"root 15620: toad x {s.x} h {s.height} z {s.z} anim {s.anim} boss {boss(s)}"]
    print(out[-1], flush=True)
    # second probe: steer the LAST JUMP (up14: A x16 from frame 15597 at x 108) to the right, then dash right until the cutscene
    e.load("cap14_f15000")
    for i in range(15000, 15596):
        s = e.step(bt(lines[i]), 1)
    root2 = e.msave()
    out.append(f"root2 15596: toad x {s.x} h {s.height} z {s.z} anim {s.anim}")
    print(out[-1], flush=True)
    best = None
    for hold_a in (16, 20):
        for air in ("Right", "none-then-right"):
            for dash in (True, False):
                e.mload(root2)
                t, f, x_cut, ctrl, landed, tap = s, 15596, None, None, None, 0
                ins = []
                for j in range(260):
                    if j < hold_a:
                        inp = ("Right", "A") if air == "Right" else ("A",)
                    elif landed is None:
                        inp = ("Right",)
                    elif x_cut is None:
                        if dash and tap < 2:
                            inp = [(), ("Right",)][tap] if tap == 0 else ()
                            inp = [(), ("Right",)][0] if False else inp
                            tap += 1
                            inp = () if tap == 1 else ()
                        else:
                            inp = ("Right",)
                    else:
                        inp = ()
                    t = e.step(inp, 1)
                    f += 1
                    ins.append("+".join(inp))
                    if landed is None and j > 6 and t.z == 0 and t.height == 30:
                        landed = (f, t.x)
                    if x_cut is None and t.anim == 50:
                        x_cut = (f, t.x)
                    if x_cut is not None and ctrl is None and t.anim != 50:
                        ctrl = (f, t.x)
                out.append(f"jump A x{hold_a} air {air:16s} dash {dash}: landed {landed}, cutscene starts {x_cut}, control back {ctrl}, boss {boss(t)}, hp {t.hp}")
                print(out[-1], flush=True)
    open(LOGS_DIR / "fix" / "early_l8arrive.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

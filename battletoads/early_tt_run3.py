"""EARLY track (2026-10-09): Terra Tubes staircase top, part 3 - from the tank's rim into the water.

early_tt_run2.py: after the sprint pass (no grab) the toad can be set down on the ledge at (884-893, 6406) by holding
Left for 12-16 frames from x >= 888 - and where are the bugs then?  From that landing try the ways off the ledge
(walk / run / hop right or left, crouch, wait) and report grabbed / hurt / SWIM (anim 98/99) / where it lands.
Also prints a coarse map of where the 'hurt' endings of part 2 happen (one representative flight per x0).

    python early_tt_run3.py   -> logs/fix/early_tt_run3.txt (+ early_tt_swim_best.json when a swim state is reached)
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
out = []


def say(t):
    print(t[:330], flush=True)
    out.append(t)


def objs(s):
    return [(hex(s[f"id{q}"]), s[f"ox{q}"] | s[f"oxh{q}"] << 8, s[f"oh{q}"] | s[f"ohh{q}"] << 8) for q in range(1, 15) if s[f"id{q}"]]


def flight(e, root, s, x0, k, mid, end, n=200, stop_on_land=False):
    """the sprint pass of part 2, then the air control; returns (inputs, state, result)"""
    e.mload(root)
    t, ph, cnt, ins, kk = s, 0, 0, [], 0
    for j in range(n):
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
            return ins, t, ("grabbed", j + 1, x, H)
        if t.hp < 47 or t.lives < s.lives:
            return ins, t, ("hurt", j + 1, x, H, t.anim)
        if t.anim in (98, 99):
            return ins, t, ("SWIM", j + 1, x, H)
        if stop_on_land and ph == 3 and t.z == 0 and kk >= k:
            return ins, t, ("landed", j + 1, x, H)
    return ins, t, ("timeout", n, t.x | t.xh << 8, t.height | t.hh << 8)


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_tt_run3.log", fields=F)
    e.load("cap14_f25000")
    for i in range(25000, ROOT):
        s = e.step(bt(lines[i]), 1)
    root = e.msave()
    say("hurt map (air control = nothing for 60 frames from x0, i.e. a straight drop at about x0+10):")
    for x0 in range(836, 912, 4):
        ins, t, res = flight(e, root, s, x0, 60, "", "")
        say(f"  x0 {x0}: {res}")
    ins, t, res = flight(e, root, s, 888, 12, "Left", "", stop_on_land=True)
    say(f"ledge landing: {res} after {len(ins)} frames from {ROOT}; objects {objs(t)}; camera {t.camx | t.camxh << 8}")
    if res[0] != "landed":
        e.close()
        return
    led = e.msave()
    base = list(ins)
    best = None
    seqs = {}
    for w, d, n1, a, n2 in itertools.product((0, 4, 10, 20, 40), ("Right", "Left"), (2, 6, 10, 16, 24, 40), (0, 2, 6, 12), (0, 20)):
        seq = [()] * w + [(d,)] * n1 + [(d, "A")] * a + [(d,)] * 60 if n2 == 0 else [()] * w + [(d,), ()] + [(d,)] * n1 + [(d, "A")] * a + [(d,)] * 60
        seqs[f"wait {w} {d} {n1} A{a} {'run' if n2 else 'walk'}"] = seq
    for d in ("Right", "Left"):
        seqs[f"Down+{d} 60"] = [("Down", d)] * 60
        seqs[f"{d}+A hold 30"] = [(d, "A")] * 30 + [(d,)] * 60
    stats = {}
    for name, seq in seqs.items():
        e.mload(led)
        r = None
        for j, b in enumerate(seq[:150]):
            t = e.step(b, 1)
            x, H = t.x | t.xh << 8, t.height | t.hh << 8
            if t.anim in (36, 37):
                r = ("grabbed", j + 1, x, H)
                break
            if t.hp < 47 or t.lives < s.lives:
                r = ("hurt", j + 1, x, H)
                break
            if t.anim in (98, 99):
                r = ("SWIM", j + 1, x, H, t.camx | t.camxh << 8)
                break
        r = r or ("end", len(seq[:150]), t.x | t.xh << 8, t.height | t.hh << 8, t.z, t.anim)
        stats[r[0]] = stats.get(r[0], 0) + 1
        if r[0] in ("SWIM", "end"):
            say(f"  {name}: {r}")
        if r[0] == "SWIM" and (best is None or r[1] < best[0]):
            best = (r[1], name, r, base + ["+".join(b) for b in seq[:r[1]]])
    say(f"from the ledge: {stats}")
    if best:
        json.dump({"from_frame": ROOT, "inputs": best[3], "result": best[2], "how": best[1]}, open(LOGS_DIR / "fix" / "early_tt_swim_best.json", "w"))
        say(f"BEST: swimming {best[2]} after {len(best[3])} frames from up14 frame {ROOT} ({best[1]})")
    open(LOGS_DIR / "fix" / "early_tt_run3.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

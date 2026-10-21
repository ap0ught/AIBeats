"""EARLY track (2026-10-09): Terra Tubes - can the toad LET GO of the hovering bug (0x74) that carries it down?

up14 frames 25224-25540: the toad hangs on the bug (anim 36/37) and sinks ~1 px/frame for 316 frames to the floor at
H 6182; every earlier search pruned the carried state, nobody tried the buttons while hanging.  The record leaves the
x-938 column at H ~6380 (120 px down) straight into the star corridor.  Probe: from several heights of the carry,
hold / mash each button for 90 frames and report when the carried animation ends and where the toad is.

    python early_tt_carry.py   -> logs/fix/early_tt_carry.txt
"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5,
     "st": 0x4B1, "hp": 0x51A, "lives": 0x11, "camx": 0x87, "camxh": 0x88, "camy": 0x89, "camyh": 0x8A}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
VARS = {
    "idle": [()],
    "A hold": [("A",)],
    "B hold": [("B",)],
    "Down hold": [("Down",)],
    "Up hold": [("Up",)],
    "Left hold": [("Left",)],
    "Right hold": [("Right",)],
    "Select hold": [("Select",)],
    "A mash": [("A",), ()],
    "B mash": [("B",), ()],
    "Down mash": [("Down",), ()],
    "Left/Right mash": [("Left",), ("Right",)],
    "Left/Right mash slow": [("Left",), ("Left",), ("Right",), ("Right",)],
    "Up/Down mash": [("Up",), ("Down",)],
    "Down+A": [("Down", "A")],
    "Down+B": [("Down", "B")],
    "A+B": [("A", "B")],
    "A+B mash": [("A", "B"), ()],
    "Right+A mash": [("Right", "A"), ()],
    "Right+B": [("Right", "B")],
    "Left+B": [("Left", "B")],
    "Down+Right": [("Down", "Right")],
    "Down+Left": [("Down", "Left")],
    "all-legal mash": [("A", "B", "Right"), ("Left",), ("A", "B", "Down"), ("Up",)],
}


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_tt_carry.log", fields=F)
    out = []
    for start in (25232, 25290, 25350):
        e.load("cap14_f25000")
        for i in range(25000, start):
            s = e.step(bt(lines[i]), 1)
        root = e.msave()
        H = lambda t: t.height | t.hh << 8
        out.append(f"=== from up14 frame {start}: toad x {s.x | s.xh << 8} H {H(s)} anim {s.anim} hp {s.hp}")
        print(out[-1], flush=True)
        for name, pat in VARS.items():
            e.mload(root)
            free, t = None, s
            for j in range(90):
                t = e.step(pat[j % len(pat)], 1)
                if free is None and t.anim not in (36, 37):
                    free = (j + 1, t.anim, t.x | t.xh << 8, H(t))
            out.append(f"  {name:22s} carried ends: {free}; at +90: x {t.x | t.xh << 8} H {H(t)} anim {t.anim} hp {t.hp} lives {t.lives}")
            print(out[-1], flush=True)
        e.mfree(root)
    open(LOGS_DIR / "fix" / "early_tt_carry.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

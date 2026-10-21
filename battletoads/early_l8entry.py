"""EARLY track (2026-10-09): Intruder Excluder's 36 idle frames at the start (up14 frames 12488-12523: the old climb
only replays behind a 38-frame entry wait).  How far does the old climb replay when k of those idle frames are dropped?
For each k: replay up14 from the Level 8 placement with k idle frames removed and compare the toad's track (x, height,
hp) with up14's own, shifted by k.  The frame where they part is the first thing in the tower that runs on the level
timer rather than on the toad's arrival.

    python early_l8entry.py   -> logs/fix/early_l8entry.txt
"""
from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11,
     "camy": 0x89, "camyh": 0x8A}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
START, FIRST_INPUT, END = 12488, 12524, 15600


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l8entry.log", fields=F)
    e.load("cap14_f12000")
    for i in range(12000, START):
        e.step(bt(lines[i]), 1)
    root = e.msave()
    ref = []
    for i in range(START, END):
        s = e.step(bt(lines[i]), 1)
        ref.append((s.x, s.height | s.hh << 8, s.hp, s.z))
    out = []
    for k in (1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 35):
        e.mload(root)
        seq = [lines[i] for i in range(START, END)]
        del seq[2:2 + k]                                   # drop k of the idle frames right after the placement
        part, hurt = None, None
        for j, b in enumerate(seq):
            s = e.step(bt(b), 1)
            cur = (s.x, s.height | s.hh << 8, s.hp, s.z)
            if j + k < len(ref) and j >= 40 and part is None and cur != ref[j + k]:
                part = (START + j + k + 1, cur, ref[j + k])
            if s.hp < 47 and hurt is None:
                hurt = (START + j + k + 1, s.hp)
            if part and (hurt or j > (part[0] - START) + 400):
                break
        out.append(f"drop {k:2d} idle frames: track parts at up14 frame {part[0] if part else None} "
                   f"(ours {part[1] if part else ''} vs old {part[2] if part else ''}); first damage {hurt}")
        print(out[-1], flush=True)
    open(LOGS_DIR / "fix" / "early_l8entry.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

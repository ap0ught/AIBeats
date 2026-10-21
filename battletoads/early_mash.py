"""EARLY track (2026-10-09): is every level transition of up14 skipped on the first possible frame?

up14 mashes one button every other frame (B before Levels 3/4, A elsewhere).  A press only counts when it is fresh, so
a one-button mash can miss the first accepting frame by one.  For each of the eight transitions before Level 12 this
replaces the inputs between the level's end and the toad's placement in the next level by other patterns and reports
the placement frame (the next level's own inputs are NOT replayed: this only measures the transition).

    python early_mash.py            -> logs/fix/early_mash.tsv
Patterns: two-letter cycles such as 'A-' (up14's), '-A', 'AB' (a fresh press EVERY frame, alternating buttons), 'AS'
(A / Start), 'hold A', ...
"""
import re

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11,
     "rtnL": 0x23, "rtnH": 0x24}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
BTN = {"A": ("A",), "B": ("B",), "S": ("Start",), "s": ("Select",), "-": (), "X": ("A", "B"), "Y": ("A", "B", "Start")}
# (cap14 base, first frame of the window (1-based; everything from here to the placement is replaced), next level byte, baseline placement)
BOUNDS = [("L1->L3 warp", 2000, 2313, 3), ("L3->L4", 4000, 4733, 4), ("L4->L6 warp", 9000, 9665, 8), ("L6->L8 warp", 12000, 12281, 7),
          ("L8->L9", 17000, 17239, 11), ("L9->L10", 27000, 27226, 9), ("L10->L11", 29000, 29251, 10), ("L11->L12", 36000, 36034, 5)]
PATTERNS = ["A-", "-A", "B-", "-B", "S-", "-S", "AB", "BA", "AS", "SA", "BS", "X-", "-X", "A", "B", "S", "--"]


def run(e, lines, base, w0, lvl, pat, limit=1400):
    """-> (placement frame, frame the level byte became lvl)"""
    e.load(f"cap14_f{base}")
    for i in range(base, w0 - 1):
        e.step(bt(lines[i]), 1)
    stage, f, set_at = 0, w0 - 1, None
    for j in range(limit):
        s = e.step(BTN[pat[j % len(pat)]] if pat != "route" else bt(lines[w0 - 1 + j]), 1)
        f += 1
        if stage == 0 and s.level == lvl:
            stage, set_at = 1, f
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            return f, set_at
    return None, set_at


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_mash.log", fields=F)
    out = ["boundary\tpattern\tplaced_frame\tvs_up14\tlevel_byte_set"]
    for name, base, w0, lvl in BOUNDS:
        ref, ref_set = run(e, lines, base, w0, lvl, "route")
        out.append(f"{name}\tup14 route\t{ref}\t0\t{ref_set}")
        print(out[-1], flush=True)
        for pat in PATTERNS:
            p, st = run(e, lines, base, w0, lvl, pat)
            out.append(f"{name}\t{pat}\t{p}\t{(p - ref) if p and ref else 'n/a'}\t{st}")
            print(out[-1], flush=True)
    open(LOGS_DIR / "fix" / "early_mash.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

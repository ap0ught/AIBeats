"""EARLY track (2026-10-09): the hidden state behind the dice, measured cleanly.

early_carry.py / early_hidden.py: two entries with byte-identical RAM roll different dice; the difference sits in the
emulator's APU block.  Here: at one level boundary of the verified route up14 the briefing page is skipped K frames
late (K idle frames before the A mash), the toad's placement in the next level is detected, and from the placement on
the BASELINE's inputs are fed frame-aligned to the placement.  So the only thing that differs is WHEN the level loads.
Equal dice stream = the downstream replays verbatim.

    python early_phase2.py <base frame (cap14 state)> <mash start frame> <level byte> <frames after placement> K1 K2 ...
        Kn = integer: idle frames inserted at the mash start;  'sJ' = Select on idle route frame J (no shift);
        'B' / 'AB' / 'St' = mash that button instead of A (same frames)
    -> logs/fix/early_phase2_<base>_<level>.tsv
"""
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "r25": 0x25, "r26": 0x26, "r27": 0x27, "r28": 0x28, "x": 0x3FD, "xh": 0x3EE,
     "height": 0x439, "y": 0x41B, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
row = lambda s: (s.level, s.timer, s.r25, s.r26, s.r27, s.r28, s.x | s.xh << 8, s.height, s.y, s.anim, s.hp, s.lives)


class Placer:
    def __init__(self, lvl):
        self.lvl, self.stage = lvl, 0

    def feed(self, r):
        if self.stage == 0 and r[0] == self.lvl:
            self.stage = 1
        if self.stage == 1 and r[10] == 0 and r[6] == 0:
            self.stage = 2
        if self.stage == 2 and r[10] > 0 and r[6] > 0:
            self.stage = 3
            return True
        return False


def run(e, lines, base, mash, lvl, after, k=0, sel=(), button=None, ref_p0=None):
    """play route[base:mash], then k idle, then the route's own mash until the toad is placed; from the frame after the
    placement feed the baseline's post-placement inputs (index ref_p0+1...) for `after` frames"""
    e.load(f"cap14_f{base}")
    pl = Placer(lvl)
    rows, n = [], 0

    def do(b):
        nonlocal n
        rows.append(row(e.step(b, 1)))
        n += 1
        return pl.feed(rows[-1])

    placed = None
    seq = [(i, bt(lines[i])) for i in range(base, mash)] + [(None, ())] * k + [(i, bt(lines[i])) for i in range(mash, mash + 400)]
    for i, b in seq:
        if i is not None and i in sel:
            assert not b
            b = ("Select",)
        if i is not None and i >= mash and button and b == ("A",):
            b = button
        if do(b):
            placed = n - 1
            break
    if placed is None:
        return None, rows, None
    p0 = ref_p0 if ref_p0 is not None else placed           # baseline: its own placement index
    for j in range(after):
        do(bt(lines[base + p0 + 1 + j]))
    return placed, rows, p0


def main():
    base, mash, lvl, after = int(sys.argv[1]), int(sys.argv[2]) - 1, int(sys.argv[3]), int(sys.argv[4])
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=f"early_phase2_{base}_{lvl}.log", fields=F)
    p0, ref, _ = run(e, lines, base, mash, lvl, after)
    print(f"baseline: level byte {lvl} placed at frame {base + p0 + 1}", flush=True)
    out = [f"# base {base} mash {mash + 1} level {lvl}; baseline placement frame {base + p0 + 1}; {after} frames compared",
           "variant\tplacement_shift\tdice_equal_frames\ttrack_equal_frames\tverbatim"]
    for v in sys.argv[5:]:
        k, sel, button = 0, set(), None
        if v[0] == "s":
            sel = {int(v[1:]) - 1}
        elif v in ("B", "AB", "St", "Se"):
            button = {"B": ("B",), "AB": ("A", "B"), "St": ("Start",), "Se": ("Select",)}[v]
        else:
            k = int(v)
        p, rows, _ = run(e, lines, base, mash, lvl, after, k, sel, button, ref_p0=p0)
        if p is None:
            line = f"{v}\tNOT PLACED"
        else:
            dice = next((j for j in range(after + 1) if ref[p0 + j][1:6] != rows[p + j][1:6]), after + 1)
            track = next((j for j in range(after + 1) if ref[p0 + j][6:] != rows[p + j][6:]), after + 1)
            line = f"{v}\t{p - p0:+d}\t{dice}\t{track}\t{'YES' if dice > after and track > after else 'no'}"
        print(line, flush=True)
        out.append(line)
    open(LOGS_DIR / "fix" / f"early_phase2_{base}_{lvl}.tsv", "a", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

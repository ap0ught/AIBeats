"""EARLY track (2026-10-09): does a time shift upstream change the dice downstream, and can the entry be steered back?

The random numbers ($25-$28) are zero at a level load and are then scrambled in the idle loop, so they depend on hidden
timing state (two entry bookmarks with byte-identical RAM diverge a few frames later: early_carry.py).  This probe
measures how that hidden state reacts to small changes at a level boundary of the verified route up14:

    python early_phase.py <base frame (cap14 state)> <insert frame> <level byte to watch> <replay to frame> <variants...>
        variant  dK      K idle frames inserted at <insert frame> (the briefing-page mash starts K frames later)
                 sJ      Select pressed on (idle) frame J of the route, nothing inserted (frames = trace numbering, 1-based)
                 sJ+dK   both
                 xJ      DROP route frame J (must be an idle frame): the page mash starts 1 frame sooner
    For every variant: where the toad is placed in the watched level (frame), and for how many frames after the
    placement the dice stream and the toad's track equal the baseline's.
    -> logs/fix/early_phase_<base>_<level>.tsv
"""
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "r25": 0x25, "r26": 0x26, "r27": 0x27, "r28": 0x28, "x": 0x3FD, "xh": 0x3EE,
     "height": 0x439, "y": 0x41B, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}


def run(e, lines, base, upto, ins_at=None, d=0, sel=(), drop=()):
    bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
    seq = []
    for i in range(base, upto):
        if i in drop:
            assert not bt(lines[i]), f"frame {i} is not idle"
            continue
        if ins_at is not None and i == ins_at:
            for _ in range(d):
                seq.append(())
        b = bt(lines[i])
        if i in sel:
            assert not b, f"frame {i} is not idle"
            b = ("Select",)
        seq.append(b)
    e.load(f"cap14_f{base}")
    rows = []
    for b in seq:
        s = e.step(b, 1)
        rows.append((s.level, s.timer, s.r25, s.r26, s.r27, s.r28, s.x | s.xh << 8, s.height, s.y, s.anim, s.hp, s.lives))
    return rows


def placed(rows, lvl):
    """index of the first frame the toad exists in the watched level (level byte set -> table cleared -> toad there)"""
    stage = 0
    for k, r in enumerate(rows):
        if stage == 0 and r[0] == lvl:
            stage = 1
        if stage == 1 and r[10] == 0 and r[6] == 0:
            stage = 2
        if stage == 2 and r[10] > 0 and r[6] > 0:
            return k
    return None


def main():
    base, ins_at, lvl, upto = int(sys.argv[1]), int(sys.argv[2]) - 1, int(sys.argv[3]), int(sys.argv[4])   # frames are 1-based (trace numbering)
    variants = sys.argv[5:]
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=f"early_phase_{base}_{lvl}.log", fields=F)
    ref = run(e, lines, base, upto)
    p0 = placed(ref, lvl)
    print(f"baseline: level {lvl} placed at frame {base + p0 + 1}; {len(ref) - p0} frames compared after it", flush=True)
    out = [f"# base {base} insert {ins_at} level {lvl} upto {upto}; baseline placement frame {base + p0 + 1}",
           "variant\tplaced_frame\tshift\tdice_equal_frames\ttrack_equal_frames\tfull_equal"]
    for v in variants:
        d, sel, drop = 0, set(), set()
        for part in v.split("+"):
            if part[0] == "d":
                d = int(part[1:])
            elif part[0] == "s":
                sel.add(int(part[1:]) - 1)
            elif part[0] == "x":
                drop.add(int(part[1:]) - 1)
        rows = run(e, lines, base, upto, ins_at, d, sel, drop)
        p = placed(rows, lvl)
        if p is None:
            line = f"{v}\tNONE\t\t\t\t"
        else:
            n = min(len(ref) - p0, len(rows) - p)
            dice = next((k for k in range(n) if ref[p0 + k][1:6] != rows[p + k][1:6]), n)
            track = next((k for k in range(n) if ref[p0 + k][6:] != rows[p + k][6:]), n)
            line = f"{v}\t{base + p + 1}\t{p - p0:+d}\t{dice}\t{track}\t{'YES' if dice == n and track == n else 'no'} (of {n})"
        print(line, flush=True)
        out.append(line)
    open(LOGS_DIR / "fix" / f"early_phase_{base}_{lvl}.tsv", "a", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

"""Press statistics of an input list or a segment (+ optional prior history): rule v2 windows per button.

    python tools/s8c_presses.py <inputs.txt | seg.json> [--prior <inputs.txt>] [--tail 1800] [--hist]

Prints, per button, presses in the segment, the highest count in any 600 / 1800 frames (windows may reach back
into the prior history), and with --hist the B presses per 100 rows of the segment.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs, BUTTONS  # noqa: E402


def load(p):
    p = Path(p)
    if p.suffix == ".json":
        return [tuple(x for x in r.split("+") if x) for r in json.loads(p.read_text(encoding="utf-8"))["rows"]]
    return [tuple(r) for r in read_inputs(p)]


def starts(rows, b):
    return [i for i, r in enumerate(rows) if b in r and (i == 0 or b not in rows[i - 1])]


def most(st, w, lo=None):
    """(max count of starts within any w frames among windows ending at a start >= lo, the end start)."""
    j, best, at = 0, 0, None
    for i in range(len(st)):
        while st[i] - st[j] >= w:
            j += 1
        if lo is not None and st[i] < lo:
            continue
        if i - j + 1 > best:
            best, at = i - j + 1, st[i]
    return best, at


if __name__ == "__main__":
    args = sys.argv[1:]
    prior = []
    if "--prior" in args:
        i = args.index("--prior")
        prior = load(args[i + 1])
        del args[i:i + 2]
    tail = 1800
    if "--tail" in args:
        i = args.index("--tail")
        tail = int(args[i + 1])
        del args[i:i + 2]
    hist = "--hist" in args
    if hist:
        args.remove("--hist")
    seg = load(args[0])
    prior = prior[-tail:]
    n0 = len(prior)
    rows = prior + seg
    print(f"{args[0]}: {len(seg)} rows, prior {n0} rows")
    for b in BUTTONS:
        st = starts(rows, b)
        ins = [s for s in st if s >= n0]
        if not st:
            continue
        m6, a6 = most(st, 600, n0)
        m18, a18 = most(st, 1800, n0)
        m60, _ = most(st, 60, n0)
        pri = len(st) - len(ins)
        print(f"  {b:6s} presses in segment {len(ins):4d} (prior tail {pri:4d})  max/60 {m60:3d}  max/600 {m6:4d} (ending row "
              f"{None if a6 is None else a6 - n0})  max/1800 {m18:4d} (ending row {None if a18 is None else a18 - n0})")
    if hist:
        st = [s - n0 for s in starts(rows, "B")]
        lo = -((n0 + 99) // 100) * 100
        line = []
        for a in range(lo, len(seg), 100):
            line.append(f"{a}:{sum(1 for s in st if a <= s < a + 100)}")
        print("  B per 100 rows:", " ".join(line))

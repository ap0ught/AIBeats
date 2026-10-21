"""Rule v2 press statistics of an input list (B by default): presses, the highest count in any 600 / 1,800 frames,
and optionally the same per stage segment.

    python tools/s5c_hist.py <inputs.txt | seg.json> [--from row] [--to row] [--button B] [--tail 1800]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402


def load(path):
    p = Path(path)
    if p.suffix == ".json":
        j = json.loads(p.read_text(encoding="utf-8"))
        return [tuple(x for x in r.split("+") if x) for r in j["rows"]]
    return [tuple(r) for r in read_inputs(p)]


def starts(rows, b="B"):
    out, prev = [], False
    for i, r in enumerate(rows):
        h = b in r
        if h and not prev:
            out.append(i)
        prev = h
    return out


def most(st, wf, lo=None, hi=None):
    """Highest number of starts within any span of wf frames; only windows that END on a start in [lo, hi)."""
    j, best, at = 0, 0, None
    for i in range(len(st)):
        while st[i] - st[j] >= wf:
            j += 1
        if (lo is None or st[i] >= lo) and (hi is None or st[i] < hi) and i - j + 1 > best:
            best, at = i - j + 1, st[i]
    return best, at


def main():
    a = sys.argv[1:]

    def opt(name, default):
        if name in a:
            i = a.index(name)
            v = a[i + 1]
            del a[i:i + 2]
            return type(default)(v)
        return default
    lo, hi, b, tail = opt("--from", -1), opt("--to", -1), opt("--button", "B"), opt("--tail", 0)
    rows = load(a[0])
    st = starts(rows, b)
    lo = None if lo < 0 else lo
    hi = None if hi < 0 else hi
    n = sum(1 for s in st if (lo is None or s >= lo) and (hi is None or s < hi))
    print(f"{a[0]}: {len(rows)} rows, {b} presses {len(st)} (in range: {n}); most in 600: {most(st, 600, lo, hi)}, "
          f"in 1800: {most(st, 1800, lo, hi)}")
    if tail:
        e = len(rows)
        print(f"   last {tail} rows: {sum(1 for s in st if s >= e - tail)} presses; last 600: {sum(1 for s in st if s >= e - 600)}")


if __name__ == "__main__":
    main()

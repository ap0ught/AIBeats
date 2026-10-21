"""Read an end_cap.py capture: the Queen's object slot (id 0x7e) through the ending, frame by frame, as change events."""
import json
import sys
from pathlib import Path

FIX = Path(__file__).resolve().parent / "logs" / "fix"
TABLES = list(range(0x3C1, 0x5A0, 15))


def load(tag):
    idx = json.loads((FIX / f"endcap_{tag}.json").read_text())
    raw = (FIX / f"endcap_{tag}.bin").read_bytes()
    rows = [raw[i * 0x800:(i + 1) * 0x800] for i in range(idx["frames"])]
    return idx, rows


if __name__ == "__main__":
    tag = sys.argv[1]
    a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 10 ** 9)
    slot = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    idx, rows = load(tag)
    f0 = idx["first_frame"]
    print(idx)
    prev = None
    for i, m in enumerate(rows):
        f = f0 + i
        if not (a <= f <= b):
            continue
        cur = [m[t + slot] for t in TABLES]
        if prev is None:
            print(f, "lv", m[0x10], "t", m[0x0B], m[0x0C], "ctr", m[0x586], " ".join(f"{t:03x}={v}" for t, v in zip(TABLES, cur)))
        else:
            ch = [(t, p, c) for t, p, c in zip(TABLES, prev, cur) if p != c]
            if ch:
                print(f, "lv", m[0x10], "t", m[0x0B], "ctr", m[0x586], " ".join(f"{t:03x}:{p}>{c}" for t, p, c in ch))
        prev = cur

"""Compare a legal stage solution with the TAS: room entries, stage end, HP / ninpo / item at the end.

    python ng/stages/a12_compare.py <stage> <inputs file> [--start <state>]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ng import legal                                  # noqa: E402
from ng.emulator import BizHawk                        # noqa: E402
from ng.inputs import read_inputs                     # noqa: E402
from ng.mode import TICKS                             # noqa: E402
from ng.stages import NAMES                           # noqa: E402
from run_stage import REF_STATE                       # noqa: E402


def events(tr, f0):
    out = []
    prev = None
    for s in tr:
        if prev is not None:
            if s["room"] != prev["room"]:
                out.append(("room", s["room"], s["frame"] - f0))
            if s["stage"] != prev["stage"]:
                out.append(("load", s["stage"], s["frame"] - f0))
            if s.get("bk") and not prev.get("bk"):
                out.append(("bosskill", s["stage"], s["frame"] - f0))
            if s["hp"] < prev["hp"]:
                out.append(("hit", s["hp"], s["frame"] - f0))
            if s["item"] != prev["item"]:
                out.append(("item", s["item"], s["frame"] - f0))
        prev = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    ap.add_argument("inputs")
    ap.add_argument("--start")
    a = ap.parse_args()
    st = NAMES.index(a.stage)
    ref = legal.TasRef()
    first, tas_rows = ref.stage_rows(st)
    tas_tr = ref.tr[first - 1:first - 1 + len(tas_rows)]
    rows = read_inputs(a.inputs)
    with BizHawk(log_name="a12_compare.log") as e:
        s0 = e.load(a.start or ("ref4751/" + REF_STATE[st]))
        e.tick(TICKS)
        tr = legal.play(e, rows)
    te = events(tas_tr, first - 1)
    oe = events(tr, s0["frame"])
    print(f"{a.stage}: ours {len(rows)} rows, TAS {len(tas_rows)}")
    for k in range(max(len(te), len(oe))):
        t = te[k] if k < len(te) else None
        o = oe[k] if k < len(oe) else None
        d = (o[2] - t[2]) if (t and o and t[:2] == o[:2]) else ""
        print(f"  TAS {str(t):28s} ours {str(o):28s} {d}")
    last = tr[-1]
    print("end:", {k: last.get(k) for k in ("frame", "stage", "hp", "ninpo", "item", "lives", "timer", "subtimer")})


if __name__ == "__main__":
    main()

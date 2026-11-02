"""Replay an input list and write one CSV row per frame (all knowledge/ram.json fields + ng.mode ticks).

    python tools/trace_run.py <inputs> <out name> [--launch]      -> logs/<out name>.trace.csv

Default: reset() first, so row k is frame k (bk2 numbering). --launch: play on the fresh launch (row k -> frame k+1).
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, LOGS_DIR  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402


def trace(rows, launch=False, log_name="trace_run.log", chunk=1000):
    e = BizHawk(log_name=log_name)
    try:
        if not launch:
            e.reset()                 # reset (reboot_core) drops Lua memory callbacks: set the ticks after it
        e.tick(TICKS)
        e.trace(True)
        out = []
        t0 = time.time()
        for i in range(0, len(rows), chunk):
            e.run(rows[i:i + chunk])
            out.extend(e.last_trace)
            if (i // chunk) % 10 == 0:
                print(f"  {i + chunk} rows, {len(out) / (time.time() - t0):.0f} f/s", flush=True)
        return out
    finally:
        e.close()


if __name__ == "__main__":
    rows = read_inputs(sys.argv[1])
    tr = trace(rows, launch="--launch" in sys.argv)
    p = LOGS_DIR / f"{sys.argv[2]}.trace.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        keys = list(tr[0].keys())
        w.writerow(["row", "input"] + keys)
        for i, (r, s) in enumerate(zip(rows, tr)):
            w.writerow([i + 1, "+".join(r)] + [s.get(k, 0) for k in keys])
    print("wrote", p, len(tr), "frames")

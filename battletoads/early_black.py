"""EARLY track (2026-10-09): our per-level end times for a route under the RECORD's rule = the first black frame after
each level (knowledge/wr_splits.json), using the cap14 savestates (every 1,000 frames of up14) instead of a replay from
power-on.  For every change of the level byte away from a real level, screenshot every frame from 300 before to 40 after
and list the black runs.

    python early_black.py            -> logs/fix/early_black_up14.json
"""
import json
import re
import sys

from PIL import Image

from toads.emulator import BizHawk, LOGS_DIR

ROUTE = "up14"
BACK, FWD = 300, 40


def dark(p):
    im = Image.open(p).convert("L").resize((32, 30))
    px = list(im.tobytes())
    return sum(px) / len(px)


def main():
    lines = [l for l in open(LOGS_DIR / f"{ROUTE}.inputs.txt").read().splitlines() if not l.startswith("#")]
    bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
    # level byte per frame from the verified trace
    lv = [0]
    for line in open(LOGS_DIR / f"{ROUTE}.trace.txt"):
        p = line.split("\t")
        lv.append(int(re.search(r"level=(\d+)", p[2]).group(1)))
    changes = [(f, lv[f - 1], lv[f]) for f in range(2, len(lv)) if lv[f] != lv[f - 1] and lv[f - 1] not in (0, 254, 255)]
    print("level-byte changes:", changes, flush=True)
    e = BizHawk(log_name="early_black.log")
    out = []
    for f, a, b in changes:
        f0 = max(0, f - BACK)
        base = (f0 // 1000) * 1000
        e.load(f"cap14_f{base}")
        for i in range(base, f0):
            e.step(bt(lines[i]), 1)
        series = []
        for i in range(f0, min(len(lines), f + FWD)):
            e.step(bt(lines[i]), 1)
            series.append((i + 1, round(dark(e.screenshot("early_black/tmp")), 1)))
        blacks = [fr for fr, d in series if d < 6]
        runs = []
        for k, fr in enumerate(blacks):
            if k == 0 or blacks[k - 1] < fr - 1:
                runs.append([fr, fr])
            else:
                runs[-1][1] = fr
        rec = {"left": a, "to": b, "byte_frame": f, "black_runs": runs, "first_black": runs[0][0] if runs else None,
               "dark_series_every10": series[::10]}
        out.append(rec)
        print({k: v for k, v in rec.items() if k != "dark_series_every10"}, flush=True)
    json.dump(out, open(LOGS_DIR / "fix" / f"early_black_{ROUTE}.json", "w"), indent=1)
    e.close()


if __name__ == "__main__":
    main()

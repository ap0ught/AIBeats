"""Per-frame data of a run for the video panel, from the ROM-level model (no emulator needed).

    python work/make_trace.py s2_5 t2_1
      -> video_assets/data/<name>.frames.csv  one row per frame from power-on
         video_assets/data/<name>.pieces.csv  one row per piece
         video_assets/data/<name>.summary.json
Columns of frames.csv: frame, buttons (A+Left...), mode ($C0), play_state ($68), lines, level, piece, next, x, y,
orient, rng (hex), frame_counter, stack_top (highest filled row, 20 = empty), cells, run_frame (frames since the
Start press on level select; negative before), score.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet import fast
from tet.inputs import read_inputs, to_mask
from tet.nes import Machine

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "video_assets" / "data"
START_BIT = 0x10


def bcd(b):
    return (b >> 4) * 10 + (b & 15)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:]:
        rows = read_inputs(ROOT / "logs" / f"{name}.inputs.txt")
        m = Machine()
        ram = m.ram
        t0 = None
        frames, pieces = [], []
        prev_ps, prev_lines, shown100 = 0, 0, None
        cur = None
        prev_mask = 0
        for f, r in enumerate(rows, 1):
            mask = to_mask(r)
            if ram[0xC0] == 3 and mask & START_BIT and not prev_mask & START_BIT and not pieces:
                t0 = f                                   # first frame Start is held on the level-select screen
            prev_mask = mask
            m.frame(mask)
            ps = ram[0x68]
            lines = (ram[0x71] & 15) * 100 + bcd(ram[0x70])
            in_game = ram[0xC0] == 4
            top, cells = 20, 0
            if in_game:
                for i in range(200):
                    if ram[0x400 + i] != 0xEF:
                        cells += 1
                        if i // 10 < top:
                            top = i // 10
            score = bcd(ram[0x75]) * 10000 + bcd(ram[0x74]) * 100 + bcd(ram[0x73])
            frames.append([f, "+".join(r), ram[0xC0], ps, lines, ram[0x64], fast.NAMES[fast.TYPE_OF[ram[0x62]]] if ram[0x62] < 19 else "",
                           fast.NAMES[fast.TYPE_OF[ram[0xBF]]] if ram[0xBF] < 19 else "", ram[0x60], ram[0x61], ram[0x62],
                           "%02X%02X" % (ram[0x17], ram[0x18]), ram[0xB1] | ram[0xB2] << 8, top, cells,
                           (f - t0) if t0 else "", score])
            if in_game:
                if ps == 1 and prev_ps != 1:             # spawn
                    cur = {"n": len(pieces) + 1, "piece": fast.NAMES[fast.TYPE_OF[ram[0x62]]], "spawn_frame": f}
                if ps == 2 and prev_ps == 1 and cur:     # lock
                    cur.update(lock_frame=f, x=ram[0x60], y=ram[0x61], orient=ram[0x62], lines_before=lines)
                    pieces.append(cur)
                if lines != prev_lines and pieces:
                    pieces[-1]["cleared"] = lines - prev_lines
                    pieces[-1]["lines_after"] = lines
                    pieces[-1]["lines_shown_frame"] = f + 1
                    if lines >= 100 and shown100 is None:
                        shown100 = f + 1
            prev_ps, prev_lines = ps, lines
        with open(OUT / f"{name}.frames.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow("frame buttons mode play_state lines level piece next x y orient rng frame_counter stack_top cells run_frame score".split())
            w.writerows(frames)
        keys = "n piece spawn_frame lock_frame x y orient lines_before cleared lines_after lines_shown_frame".split()
        with open(OUT / f"{name}.pieces.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, keys, restval="")
            w.writeheader()
            w.writerows(pieces)
        # time at every 10 lines (frame the counter shows it), relative to the Start press
        splits = {}
        for p in pieces:
            if "lines_after" in p:
                for k in range(10, 101, 10):
                    if p["lines_after"] >= k and k not in splits:
                        splits[k] = p["lines_shown_frame"] - t0
        clears = {}
        for p in pieces:
            if p.get("cleared"):
                clears[p["cleared"]] = clears.get(p["cleared"], 0) + 1
        summary = {"name": name, "frames_from_power_on": len(rows), "start_frame": t0, "lines100_shown_frame": shown100,
                   "run_frames": shown100 - t0, "run_seconds": round((shown100 - t0) / 60.0988, 2),
                   "pieces_to_100": sum(1 for p in pieces if p["lock_frame"] < shown100),
                   "clears_by_size": clears, "split_frames_every_10_lines": splits,
                   "split_seconds_every_10_lines": {k: round(v / 60.0988, 2) for k, v in splits.items()},
                   "record_frames": 9828, "record_seconds": 163.54}
        (OUT / f"{name}.summary.json").write_text(json.dumps(summary, indent=1))
        print(name, json.dumps({k: summary[k] for k in ("start_frame", "run_frames", "run_seconds", "pieces_to_100", "clears_by_size")}))
        print("  splits (s):", summary["split_seconds_every_10_lines"])


if __name__ == "__main__":
    main()

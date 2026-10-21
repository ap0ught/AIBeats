"""EARLY track (2026-10-09): up14's level ends under the record's rule (first black frame after each level, from
early_black.py) against knowledge/wr_splits.json; the last row is the cut to Professor T. Bird (frame 47253, end_probe).
    python early_table.py   -> logs/fix/early_levels.tsv + prints a Markdown table"""
import json
from toads.emulator import LOGS_DIR, PROJECT

FPS, START = 60.0988, 2074
black = {r["left"]: r for r in json.load(open(LOGS_DIR / "fix" / "early_black_up14.json"))}
wr = json.load(open(PROJECT / "knowledge" / "wr_splits.json"))["levels"]
# first black frame: the first run for warps (170 f before the byte change), the run at the byte change otherwise
pick = {}
for byte, r in black.items():
    runs = r["black_runs"]
    near = min(runs, key=lambda q: abs(q[0] - r["byte_frame"]))[0]
    pick[byte] = runs[0][0] if r["byte_frame"] - runs[0][0] > 100 else near
pick[13] = 47253                                  # the cut to T. Bird (second 13->254 change), not the first byte change
rows, prev_o, prev_w = [], 0.0, 0.0
print("| level | our end frame | ours (s) | record (s) | behind (+) / ahead (-) so far | this level: ours | record | difference (s) | frames |")
print("|---|---|---|---|---|---|---|---|---|")
for lv in wr:
    f = pick[lv["byte"]]
    o = (f - START) / FPS
    d_lvl = (o - prev_o) - (lv["end"] - prev_w)
    rows.append((lv["num"], lv["name"], f, round(o, 2), lv["end"], round(o - lv["end"], 2), round(o - prev_o, 2), round(lv["end"] - prev_w, 2), round(d_lvl, 2), round(d_lvl * FPS)))
    print(f"| {lv['num']} {lv['name']} | {f} | {o:.2f} | {lv['end']:.2f} | {o - lv['end']:+.2f} | {o - prev_o:.2f} | {lv['end'] - prev_w:.2f} | {d_lvl:+.2f} | {d_lvl * FPS:+.0f} |")
    prev_o, prev_w = o, lv["end"]
open(LOGS_DIR / "fix" / "early_levels.tsv", "w").write("\n".join("\t".join(map(str, r)) for r in rows) + "\n")

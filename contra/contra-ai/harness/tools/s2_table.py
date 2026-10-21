"""Per-room table of a base-stage solver run against the record's same rooms.

    python tools/s2_table.py <stage 2|4> <tag>          (reads logs/s<stage>/<tag>_report.json)

Columns: room load (rows after the stage's first frame at which T = 0), core open T, first / last core hit T,
cleared T, next room T, lag frames, our wall-explosion onset (= last hit + 34, frames after the stage's first frame)
against the record's (video frames x 60.0988 / 60 after its medals frame), and the floor the code allows with one
press per 5 frames.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
stage, tag = int(sys.argv[1]), sys.argv[2]
rep = json.loads((ROOT / "logs" / f"s{stage}" / f"{tag}_report.json").read_text())
rec = next(s for s in json.loads((ROOT / "knowledge" / "record_events.json").read_text())["stages"] if s["stage"] == stage)
K = 60.0988 / 60
med = rec["medals_first"]["f"]
FLOOR = {2: [293, 293, 293, 293, 317], 4: [143, None, 143, 293, None, 293, 318, 317]}[stage]
print("| room | load | core open T | first hit T | last hit T | floor | cleared T | next room T | frames | lag | re-plans | onset, ours | onset, record | ahead |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
pause = rep.get("pause_rows", 0)
for r, rr in zip(rep["rooms"], rec["rooms"]):
    cores = {}
    for e in r.get("ents", []):
        m = re.match(r"<core#(\d+) .*open(\d+|None)", e)
        if m:
            cores[int(m.group(1))] = m.group(2)
    hits = [p[0] + 20 for p in (r["plan"] or []) if any(h in cores for h in p[3])]
    onset = r["load"] + (r["last_hit_T"] or 0) + r["lag"] + 34
    ron = (rr["wall_explosion_onset_f"] - med) * K
    fl = FLOOR[r["room"] - 1]
    print(f"| {r['room']} | {r['load']} | {'/'.join(sorted(set(cores.values())))} | {hits[0] if hits else '-'} | {r['last_hit_T']} | "
          f"{fl if fl else '-'} | {r['cleared_T']} | {r['next_T']} | {r['frames']} | {r['lag']} | {r['replans']} | {onset} | {ron:.0f} | {ron - onset:+.0f} |")
bd = rep.get("boss_dead")
rb = (rec["boss_destroyed_first_explosion"]["f"] - med) * K
print(f"\nboss room first frame: row {rep.get('boss_load')}; boss defeated flag: row {bd} (record's first explosion {rb:.0f}, ahead {rb - bd if bd else 0:+.0f}); "
      f"boss fight {rep.get('boss')}")
nxt = {2: 3716, 4: 5761}[stage]
print(f"segment: {rep.get('frames')} frames (record {nxt}, ahead {nxt - rep.get('frames', 0):+d}); pause rows at the start {pause}; "
      f"weapon out ${rep.get('weapon', 0):02X}; lives {rep.get('lives')}; solver time {rep.get('secs')} s; start fc {rep.get('fc0')} rng {rep.get('rng0')}")

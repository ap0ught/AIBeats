"""Record a verified route for the run video: its inputs from power-on, then `tail` idle frames so the picture runs on
into Professor T. Bird's screen (2026-10-10).

    python yt/run_capture.py <name> <inputs file> [tail frames = 420]

Writes video/<name>.mkv and logs/<name>.{inputs,trace}.txt (one row per frame, tail included) through the emulator's own
session recorder, and logs/<name>.capture.json: landing, both 13->254 cuts, the RAM sha1 on the last route input.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from toads.emulator import BizHawk, LOGS_DIR  # noqa: E402

name, src = sys.argv[1], Path(sys.argv[2])
tail = int(sys.argv[3]) if len(sys.argv) > 3 else 420
lines = [l for l in src.read_text().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name=f"{name}_capture.log", record=name)
prev_lv = prev_an = None
landing, cuts, sha, levels = None, [], None, []
for i, l in enumerate(lines + [""] * tail):
    s = e.step(bt(l), 1)
    f = i + 1
    if landing is None and s.level == 1 and prev_an == 5 and s.anim == 4:
        landing = f
    if s.level != prev_lv:
        levels.append((f, s.level))
        if prev_lv == 13 and s.level == 254:
            cuts.append(f)
    if f == len(lines):
        sha = hashlib.sha1(e.ram_all()).hexdigest()
    prev_lv, prev_an = s.level, s.anim
e.close()
out = {"name": name, "source": str(src), "route_inputs": len(lines), "tail": tail, "landing": landing, "cuts": cuts,
       "sha1_at_last_route_input": sha, "level_bytes": levels,
       "time": (cuts[1] - landing) / 60.0988 if len(cuts) > 1 and landing else None}
(LOGS_DIR / f"{name}.capture.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "level_bytes"}))

"""Save the reference run's bookmarks: a savestate at each stage's first playable frame and at each base room.

    python tools/ref_states.py <route>          needs logs/<route>.inputs.txt and logs/<route>.report.json (assemble.py)

Replays the inputs from power-on once and saves, when the emulator frame counter equals the listed frame:
    states/ref_s<k>.State          stage k's first playable frame L (level routine 4 first read on this frame)
    states/ref_s<k>_room<r>.State  base stages: the frame the room index ($64) becomes r
    states/ref_s<k>_boss.State     the frame BOSS_DEFEATED_FLAG is first 1 (for studying the stage ending)
Each state is the emulator AFTER that frame. Writes logs/<route>.states.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402

route = sys.argv[1]
rows = read_inputs(LOGS_DIR / f"{route}.inputs.txt")
rep = json.loads((LOGS_DIR / f"{route}.report.json").read_text(encoding="utf-8"))
marks = {}
for st in rep["stages"]:
    k = st["stage"]
    marks[st["first_frame"]] = f"ref_s{k}"
    for r in st.get("rooms", []):
        marks[r["frame"]] = f"ref_s{k}_room{r['room']}"
    if "boss_defeated_frame" in st:
        marks[st["boss_defeated_frame"]] = f"ref_s{k}_boss"
out = {}
with BizHawk(log_name=f"{route}_states.log", fields={"level": 0x30, "lroutine": 0x2C, "screen": 0x64}) as e:
    done = 1                                    # the bridge starts on frame 1
    for f in sorted(marks):
        n = f - done
        if n > len(rows) - (done - 1):
            break
        s = e.run(rows[done - 1:done - 1 + n])
        done = f
        assert s["frame"] == f, (s, f)
        e.save(marks[f])
        out[marks[f]] = {"frame": f, "level": s["level"], "level_routine": s["lroutine"], "screen": s["screen"]}
        print(marks[f], out[marks[f]])
(LOGS_DIR / f"{route}.states.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

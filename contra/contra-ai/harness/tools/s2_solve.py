"""Run a base-stage solver (stage 2 or 4) on its own emulator.

    python tools/s2_solve.py <stage 2|4> <state> <tag> [--pause N] [--hist logs/x.inputs.txt] [--states DIR]

<state>   savestate (under states/) of the stage's first frame ($2C == 4), e.g. ref_s2 or s4/dbg_L
<tag>     output name: logs/s<stage>/<tag>.inputs.txt (the legal segment), <tag>_rows.json, <tag>_report.json
--pause   test option: pause N frames before the first room (a different start condition; its rows are in the segment)
--hist    the input rows played before this segment (their last 40 are used for the press-rate cap at the boundary)
--states  also save states/<DIR>/room<k>, boss, boss_dead, next_stage

Takes 10-35 minutes (the room planner is pure Python). Then: python check_inputs.py logs/s<stage>/<tag>.inputs.txt
and python tools/s2_table.py <stage> <tag> for the per-room table against the record.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages import s2, s4  # noqa: E402
from contra.stages.base_common import make_fields  # noqa: E402


def main():
    a = sys.argv[1:]


    def opt(name, default=None):
        if name in a:
            i = a.index(name)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return default


    pause = int(opt("--pause", 0))
    hist = opt("--hist")
    states = opt("--states")
    rooms_only = "--rooms-only" in a        # stop at the boss room (third pass: room work)
    old_rooms = "--old-rooms" in a          # the first builder's room driver instead of base_room3
    a[:] = [x for x in a if x not in ("--rooms-only", "--old-rooms")]
    stage, state, tag = int(a[0]), a[1], a[2]
    mod = s2 if stage == 2 else s4
    hist_rows = read_inputs(hist)[-40:] if hist else ()
    t = time.time()
    with BizHawk(log_name=f"s{stage}_solve_{tag}.log", fields=make_fields()) as e:
        out = mod.solve(e, state, hist=hist_rows, pause=pause, save_states=states, rooms_only=rooms_only,
                        rooms3=not old_rooms)
    rows = out.pop("rows", [])
    out["secs"] = round(time.time() - t)
    base = Path(__file__).resolve().parent.parent / "logs" / f"s{stage}"
    base.mkdir(parents=True, exist_ok=True)
    (base / f"{tag}_rows.json").write_text(json.dumps(rows))
    (base / f"{tag}_report.json").write_text(json.dumps(out, indent=1))
    if out.get("ok"):
        write_inputs(base / f"{tag}.inputs.txt", rows, f"stage {stage} segment from state {state} pause={pause}")
    print("ok" if out.get("ok") else "FAILED", "frames", out.get("frames"), "boss", out.get("boss"), "secs", out["secs"])
    for r in out["rooms"]:
        print("  room", r["room"], "frames", r["frames"], "last hit T", r["last_hit_T"], "lag", r["lag"], "re-plans", r["replans"], r["reason"])


if __name__ == "__main__":
    main()

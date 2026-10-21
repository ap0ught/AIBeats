"""Third pass, part 2 (2026-10-16): re-play only the boss fight (and the exit) of a finished base-stage solve with the
current executor (base_fight3: candidate plans probed on the emulator), from that solve's saved boss-room state, with
the same rows before it - so the result is directly comparable (the planners are deterministic).

    python tools/s2t_bossprobe.py <stage 2|4> <old tag> <new tag> <boss state> [--hist inputs.txt]

<old tag>    logs/s<stage>/<old tag>_rows.json + _report.json (rows of the whole segment, boss_load)
<boss state> the state saved at the boss room's first row by that solve (e.g. s2t/U2L2/boss)
Writes logs/s<stage>/<new tag>.inputs.txt (old rows up to the boss room + the new fight + exit), _rows.json,
_report.json. Then: python tools/s2_verify.py <stage> <new tag> <stage start state> [--hist ...].
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages import base_boss as bb  # noqa: E402
from contra.stages import base_fight3 as bf3  # noqa: E402
from contra.stages.base_common import Sess, make_fields  # noqa: E402


def main():
    a = sys.argv[1:]
    hist = None
    if "--hist" in a:
        i = a.index("--hist")
        hist = a[i + 1]
        del a[i:i + 2]
    stage, old, new, bstate = int(a[0]), a[1], a[2], a[3]
    base = ROOT / "logs" / f"s{stage}"
    rows = [tuple(r) for r in json.loads((base / f"{old}_rows.json").read_text())]
    rep = json.loads((base / f"{old}_report.json").read_text())
    n_load = rep["boss_load"]
    pre = rows[:n_load]
    h40 = [tuple(r) for r in read_inputs(ROOT / hist)][-40:] if hist else []
    t = time.time()
    with BizHawk(log_name=f"s{stage}_bossprobe_{new}.log", fields=make_fields()) as e:
        S = Sess(e, hist=h40 + pre, fields=make_fields())
        S.load(bstate)
        S.rows = list(pre)
        info = bf3.solve_boss(S)
        out = {"old": old, "boss_load": n_load, "boss": info, "ok": False}
        if info.get("ok"):
            out["boss_dead"] = len(S.rows)
            x = bb.solve_exit(S)
            out["exit"] = x
            out["ok"] = x["ok"]
            out["frames"] = len(S.rows)
            out["weapon"], out["lives"] = S.s["weapon"], S.s["lives"]
        new_rows = list(S.rows)
    out["secs"] = round(time.time() - t)
    out["rooms"] = rep.get("rooms")
    (base / f"{new}_rows.json").write_text(json.dumps(new_rows))
    (base / f"{new}_report.json").write_text(json.dumps(out, indent=1, default=str))
    if out["ok"]:
        write_inputs(base / f"{new}.inputs.txt", new_rows, f"stage {stage}: {old} up to the boss room + boss re-played "
                                                           f"with base_fight3 probing")
    print("ok" if out["ok"] else "FAILED", "frames", out.get("frames"), "old", rep.get("frames"), "boss",
          info.get("frames"), "old boss", rep["boss"].get("frames"), "secs", out["secs"], flush=True)


if __name__ == "__main__":
    main()

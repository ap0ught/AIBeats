"""Run a stage solver (6 or 7) from a savestate, verify the result by an open-loop replay, write the segment.

    python tools/s6_solve.py <stage 6|7> <state> <out name> [--no-verify] [--param k=v ...]

Writes logs/s<stage>/<out>.inputs.txt (one row per frame of the segment), logs/s<stage>/<out>.seg.json (facts),
states/s<stage>/<out>_*.State (checkpoints) and prints a summary. Can also be imported: run(sim, stage, state, out).
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.inputs import write_inputs  # noqa: E402
from contra.stages.s6lib import Sim, write_json  # noqa: E402


def replay_hash(sim, state, rows):
    sim.load(state)
    tr = sim.run(rows)
    h = hashlib.sha1()
    for f in tr:
        h.update(bytes([f["x"], f["y"], f["screen"], f["scroll"], f["rng"], f["fc"], f["lroutine"], f["level"],
                        f["death"] & 1, f["weapon"], f["lagged"]]))
    last = tr[-1]
    nxt = sim.run([()])[-1]
    return h.hexdigest(), last, nxt, sum(f["lagged"] for f in tr), any(f.dead for f in tr)


def run(sim, stage, state, out, params=None, verify=True, log=print, history=()):
    mod = __import__(f"contra.stages.s{stage}", fromlist=["solve"])
    t0 = time.time()
    res = mod.solve(sim, state, history=history, name=f"s{stage}:{out}", log=log, params=params,
                    save_prefix=f"s{stage}/{out}")
    rows = res.pop("rows")
    res["seconds"] = round(time.time() - t0, 1)
    res["state"] = state
    res["stage"] = stage
    if res["ok"]:
        if verify:
            h1, last, nxt, lag, died = replay_hash(sim, state, rows)
            h2, _, _, _, _ = replay_hash(sim, state, rows)
            res["replay"] = {"sha1": h1, "match": h1 == h2, "died": died, "lag": lag,
                             "last_frame": {"level": last["level"], "lroutine": last["lroutine"]},
                             "next_frame": {"level": nxt["level"], "lroutine": nxt["lroutine"], "fc": nxt["fc"],
                                            "weapon": nxt["weapon"], "lives": nxt["lives"]}}
            res["verified"] = bool(h1 == h2 and not died and nxt["level"] == stage and nxt["lroutine"] == 4
                                   and last["lroutine"] != 4)
        p = ROOT / "logs" / f"s{stage}" / f"{out}.inputs.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        write_inputs(p, rows, f"stage={stage} state={state} segment_frames={len(rows)}")
        chk = subprocess.run([sys.executable, str(ROOT / "check_inputs.py"), str(p)], capture_output=True, text=True)
        res["check_inputs"] = chk.stdout.strip().splitlines()[-1] if chk.stdout.strip() else f"exit {chk.returncode}"
    write_json(ROOT / "logs" / f"s{stage}" / f"{out}.seg.json", res)
    return res, rows


if __name__ == "__main__":
    args = sys.argv[1:]
    verify = "--no-verify" not in args
    params = {}
    while "--param" in args:
        i = args.index("--param")
        k, v = args[i + 1].split("=")
        params[k] = int(v)
        del args[i:i + 2]
    args = [a for a in args if a != "--no-verify"]
    stage, state, out = int(args[0]), args[1], args[2]
    with Sim(f"s{stage}_solve_{out}") as sim:
        res, rows = run(sim, stage, state, out, params, verify)
    print(json.dumps({k: v for k, v in res.items() if k not in ("violations",)}, indent=1))

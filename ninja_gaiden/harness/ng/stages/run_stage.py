"""Stage solver driver: from a start state, produce LEGAL rows for one stage (start state -> the next stage's
control frame), verified by an open-loop replay and by the check_inputs.py rule engine.

    python ng/stages/run_stage.py --stage 1-1 [--start ref4751/00_1-1_control] [--history logs/x.inputs.txt]
        [--ref tas | --ref logs/<legal>.inputs.txt@<state>] [--out a12_1-1] [--width 10] [--step 4] [--horizon 12]
        [--no-effects] [--tag name]

* --start   a savestate under states/ (without .State). Default: the TAS's control state of that stage.
* --history the legal rows played before the start state (from power-on). The press windows (600/1800 frames)
            span stage boundaries, so a chained run must pass the real history. Default: logs/intro_human
            for 1-1, else the TAS-state default "none" (then the check covers the stage alone).
* --ref     what to follow. "tas" (default): the TAS 4751M rows and trace of that stage.
* Output: logs/<out>.inputs.txt (the stage's rows), logs/<out>.stage.json (frames, verification, stats),
          states/<out>_end.State (the next stage's control frame, reached by the open-loop replay).

The stage ends ("done") at: a boss kill (tick bk) in a boss stage, or the change of $6D (the load after the
exit walk; the walk's frames take no input). From there the tail plays nothing until the next stage's control
frame, pressing Start (held 2 frames) on the first frame that skips a cutscene.

Library use (other agents): `solve_stage(emu, stage, start, history, ...)` -> dict (see its doc).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ng import legal                                   # noqa: E402
from ng.emulator import BizHawk, LOGS_DIR, STATES_DIR  # noqa: E402
from ng.inputs import read_inputs, write_inputs        # noqa: E402
from ng.mode import TICKS                              # noqa: E402
from ng.stages import NAMES, BOSS                      # noqa: E402  (the module ng/stages.py)

WORK = ROOT / "work" / "a12"
REF_STATE = {0: "00_1-1_control", 1: "01_1-2_control", 2: "02_2-1_control", 3: "03_2-2_control",
             4: "04_2-3_control", 5: "05_3-1_control", 6: "06_3-2_control", 7: "07_3-3_control",
             8: "08_4-1_control", 9: "09_4-2_control", 10: "10_4-3_control", 11: "11_4-4_control",
             12: "12_5-1_control", 13: "13_5-2_control", 14: "14_5-3_control", 15: "15_5-4_control",
             16: "16_6-1_control", 17: "17_6-2_control", 18: "18_6-3_control", 19: "19_6-4a_control"}


def stage_index(name: str) -> int:
    return NAMES.index(name)


def make_done(stage: int):
    boss = stage in BOSS

    def done(prev, s):
        if s.get("stage") != stage:
            return True
        if boss and s.get("bk"):
            return True
        return False
    return done


def tail_to_control(emu, stage: int, history, log=print, max_frames: int = 12000):
    """From the 'done' frame: play empty rows (Start skips a cutscene as early as legal) until the play loop runs
    in the next stage. Returns the rows."""
    rows = []
    leg = legal.Legality(history)
    emu.trace(True)
    skipped = False
    while len(rows) < max_frames:
        s = emu.state()
        if s.get("stage") == stage + 1 and s.get("gm"):
            break
        row = ()
        if s.get("cs") and not skipped:
            # try a Start press (2 frames) now: does the script end (csskip) within the press?
            if leg.can(("Start",)):
                sid = emu.msave()
                tr = legal.play(emu, [("Start",), ("Start",)])
                ok = any(x.get("csskip") for x in tr)
                emu.mload(sid)
                emu.mfree(sid)
                if ok:
                    for r in [("Start",), ("Start",)]:
                        legal.play(emu, [r])
                        leg.push(r)
                        rows.append(r)
                    skipped = True
                    log(f"  tail: Start skip at tail row {len(rows) - 2}")
                    continue
        legal.play(emu, [row])
        leg.push(row)
        rows.append(row)
    return rows


def effects_for(emu, ref: legal.TasRef, stage: int, log=print, force=False):
    """effects_resolve() on the TAS trajectory of that stage, cached in work/a12/effects_<stage>.json.
    Returns (resolved rows, weights keyed by reference index)."""
    WORK.mkdir(parents=True, exist_ok=True)
    p = WORK / f"effects_{NAMES[stage]}.json"
    first, rows = ref.stage_rows(stage)
    if p.exists() and not force:
        j = json.loads(p.read_text(encoding="utf-8"))
        res = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
        w = {(k.split("@")[0], int(k.split("@")[1])): v for k, v in j["weights"].items()}
        return first, res, w
    emu.load("ref4751/" + REF_STATE[stage])
    t = time.time()
    res, info = legal.effects_resolve(emu, rows, first, log=log)
    log(f"effects {NAMES[stage]}: {len(rows)} rows, {len(info['opposing'])} opposing frames "
        f"({sum(1 for o in info['opposing'] if not o[3])} without an exact legal equivalent), "
        f"{sum(1 for v in info['weights'].values() if v > 1)} / {len(info['weights'])} presses matter, "
        f"{time.time() - t:.0f} s")
    j = {"stage": NAMES[stage], "first_frame": first, "rows": ["+".join(r) for r in res],
         "weights": {f"{b}@{i}": v for (b, i), v in info["weights"].items()},
         "opposing": [[i, "+".join(r), "+".join(c), ex] for i, r, c, ex in info["opposing"]]}
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(j), encoding="utf-8")
    tmp.replace(p)
    return first, res, info["weights"]


def solve_stage(emu, stage: int, start: str, history=(), ref_name: str = "tas4751", use_effects: bool = True,
                log=print, prefix=(), dump=None, ref_sol=None, start_index: int = 0, **beam) -> dict:
    """Solve one stage from savestate `start` (name under states/). Returns {"rows": [...], "frames": n,
    "end_frame": f, "stats": {...}}. The emulator ends at the next stage's control frame."""
    ref = legal.TasRef(ref_name)
    first, tas_rows = ref.stage_rows(stage)
    last = ref.control(stage + 1)
    weights = None
    desired = tas_rows
    if use_effects:
        _, desired, weights = effects_for(emu, ref, stage, log)
    seg = legal.Segment(ref.tr[first - 1:last], desired, raw=tas_rows)
    if ref_sol is not None:
        # follow an earlier LEGAL solution of this stage instead (rows, its start state): its trace is the reference
        sol_rows, sol_start = ref_sol
        emu.load(sol_start)
        emu.tick(TICKS)
        sol_tr = legal.play(emu, sol_rows)
        seg = legal.Segment(sol_tr, sol_rows, raw=sol_rows)
        weights = None
        log(f"  reference: legal solution ({len(sol_rows)} rows from {sol_start})")
    s0 = emu.load(start)
    rep = legal.Repair(emu, seg, history=history, weights=weights, log=log, **beam)
    t = time.time()
    rows, info = rep.solve(make_done(stage), start_index=start_index, prefix=prefix, dump=dump)
    log(f"  {NAMES[stage]} play part: {len(rows)} rows, {info['stats']}, {time.time() - t:.0f} s")
    tail = tail_to_control(emu, stage, list(history) + rows, log)
    rows = rows + tail
    s1 = emu.state()
    return {"rows": rows, "frames": len(rows), "start_frame": s0["frame"], "end_frame": s1["frame"],
            "stats": info["stats"], "tas_frames": last - (first - 1), "end_state": dict(s1)}


def verify(emu, start: str, rows, stage: int) -> dict:
    """Open-loop replay from the start state: returns the frame where the next stage's control is reached and the
    RAM SHA-1 after the last row."""
    s0 = emu.load(start)
    emu.tick(TICKS)
    tr = legal.play(emu, rows)
    ctl = next((s["frame"] for s in tr if s.get("stage") == stage + 1 and s.get("gm")), None)
    deaths = sum(1 for a, b in zip(tr, tr[1:]) if b.get("dw") and not a.get("dw"))
    return {"start_frame": s0["frame"], "next_control": ctl, "ram_sha1": hashlib.sha1(emu.ram_all()).hexdigest(),
            "deaths": deaths, "last_frame": tr[-1]["frame"] if tr else s0["frame"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--start")
    ap.add_argument("--history")
    ap.add_argument("--out")
    ap.add_argument("--width", type=int, default=10)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--horizon", type=int, default=12)
    ap.add_argument("--back", type=int, default=8)
    ap.add_argument("--no-effects", action="store_true")
    ap.add_argument("--ninpo-cost", type=float, default=3.0)
    ap.add_argument("--ninpo-floor", type=int, default=0)
    ap.add_argument("--start-index", type=int, default=0, help="initial reference offset (delta) for --prefix")
    ap.add_argument("--esc-lag", type=float, default=6.0)
    ap.add_argument("--prefix", help="resume: rows (inputs file) to commit first from the start state")
    a = ap.parse_args()
    stage = stage_index(a.stage)
    start = a.start or ("ref4751/" + REF_STATE[stage])
    if a.history:
        history = read_inputs(a.history if Path(a.history).exists() else LOGS_DIR / a.history)
    else:
        history = read_inputs(LOGS_DIR / "a12_intro.inputs.txt") if stage == 0 else []
    out = a.out or f"a12_{a.stage}"
    logf = open(LOGS_DIR / f"{out}.solve.log", "a", encoding="utf-8")

    def log(m):
        line = f"[{time.strftime('%H:%M:%S')}] {m}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()
    log(f"solve {a.stage} from {start}, history {len(history)} rows, width {a.width} step {a.step} "
        f"horizon {a.horizon}")
    with BizHawk(log_name=f"{out}_emu.log") as emu:
        prefix = read_inputs(a.prefix) if a.prefix else ()
        res = solve_stage(emu, stage, start, history, use_effects=not a.no_effects, log=log, width=a.width,
                          step=a.step, horizon=a.horizon, back=a.back, prefix=prefix, start_index=a.start_index,
                          ninpo_cost=a.ninpo_cost, ninpo_floor=a.ninpo_floor, esc_lag=a.esc_lag,
                          dump=str(ROOT / "states" / "tmp" / f"{out}.partial.inputs.txt"))
        emu.save(f"tmp/{out}_end_solver")
        v = verify(emu, start, res["rows"], stage)
        emu.save(f"{out}_end")
    chk = legal.check(res["rows"], history)
    ok = v["next_control"] == res["end_frame"] and chk["pass"] and v["deaths"] == 0
    rep = {"stage": a.stage, "start": start, "history_rows": len(history), "rows": len(res["rows"]),
           "start_frame": res["start_frame"], "end_frame": res["end_frame"],
           "frames_control_to_control": res["end_frame"] - res["start_frame"],
           "tas_frames_control_to_control": res["tas_frames"], "vs_tas": res["end_frame"] - res["start_frame"] - res["tas_frames"],
           "verify": v, "legal": chk["pass"], "violations": {k: r["violations"] for k, r in chk["rules"].items() if r["violations"]},
           "stats": res["stats"], "ok": ok}
    write_inputs(LOGS_DIR / f"{out}.inputs.txt", res["rows"], f"stage {a.stage} from {start}; legal={chk['pass']}")
    (LOGS_DIR / f"{out}.stage.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    log(f"RESULT {a.stage}: {rep['frames_control_to_control']} f control->control (TAS {res['tas_frames']}, "
        f"{rep['vs_tas']:+d}); verify next control {v['next_control']} vs solver {res['end_frame']}; "
        f"legal {chk['pass']}; deaths {v['deaths']}; {'OK' if ok else 'NOT OK'}")
    logf.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

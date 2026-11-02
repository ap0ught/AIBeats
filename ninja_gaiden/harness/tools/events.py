"""Play an input list -> report its events (and optionally save states / screenshots at them).

    python tools/events.py <inputs> [--launch] [--states <dir under states/>] [--name <report name>]

Pass 1 traces every frame (tools/trace_run.trace; all of it -> logs/<name>.trace.csv) and runs ng.events.analyse + ng.clock.measure; the report goes to
logs/<name>.events.json and is printed. With --states, pass 2 replays and saves, for every stage:
<dir>/<NN>_<stage>_control.State (first control frame), and for boss stages <dir>/<NN>_<stage>_boss0.State (the
frame the boss HP display reaches 0) and <dir>/<NN>_<stage>_room<r>.State at each room entry; plus a screenshot of
each in shots/<dir>/. Default numbering: reset() first, row k -> frame k (bk2 numbering); --launch: fresh launch.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng import clock  # noqa: E402
from ng.emulator import BizHawk, LOGS_DIR  # noqa: E402
from ng.events import analyse  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from tools.trace_run import trace  # noqa: E402


def save_points(rep):
    pts = []
    for i, st in enumerate(rep["stages"]):
        tag = f"{st['stage']:02d}_{st['name']}"
        if "control" in st:
            pts.append((st["control"], f"{tag}_control"))
        if "boss_hp_set" in st and st["boss_hp_set"] != st.get("control"):
            pts.append((st["boss_hp_set"], f"{tag}_boss"))
        if "boss0" in st:
            pts.append((st["boss0"], f"{tag}_boss0"))
    for r in rep["rooms"]:
        pts.append((r["frame"], f"room{r['room']:02d}_{r['stage']}"))
    return sorted(set(pts))


if __name__ == "__main__":
    args = sys.argv[1:]
    launch = "--launch" in args
    sdir = args[args.index("--states") + 1] if "--states" in args else None
    nm = args[args.index("--name") + 1] if "--name" in args else Path(args[0]).name.replace(".inputs.txt", "")
    rows = read_inputs(args[0])
    tr = trace(rows, launch=launch, log_name=f"events_{nm}.log")
    import csv
    with open(LOGS_DIR / f"{nm}.trace.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        keys = list(tr[0].keys())
        w.writerow(["row", "input"] + keys)
        for i, (r, st) in enumerate(zip(rows, tr)):
            w.writerow([i + 1, "+".join(r)] + [st.get(k, 0) for k in keys])
    rep = analyse(tr)
    rep["clock"] = clock.measure(tr)
    (LOGS_DIR / f"{nm}.events.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    for st in rep["stages"]:
        print(f"{st['name']:5s} load {st.get('load')} control {st.get('control')} boss0 {st.get('boss0')} "
              f"next {st.get('control_to_next_control')}")
    print("deaths", rep["deaths"])
    print("cutscenes", [(c["first"], c["last"], c["stage"], c["skipped"]) for c in rep["cutscenes"]])
    print("game lag frames", rep["game_lag_frames"], rep["game_lag_first"][:20], "bizhawk lag", rep["bizhawk_lag_total"])
    print("clock", rep["clock"])
    if sdir:
        pts = save_points(rep)
        first = tr[0]["frame"] - 1          # frame before row 1
        e = BizHawk(log_name=f"events_states_{nm}.log")
        try:
            if not launch:
                e.reset()
            done = 0
            for f, tag in pts:
                n = f - first                   # rows to have played
                e.run(rows[done:n])
                done = n
                assert e.state().frame == f, (e.state().frame, f)
                e.save(f"{sdir}/{tag}")
                e.screenshot(f"{sdir}/{tag}")
            print("saved", len(pts), "states in states/" + sdir)
        finally:
            e.close()

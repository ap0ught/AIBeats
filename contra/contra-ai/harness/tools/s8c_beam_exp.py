"""Boss beam experiments from the fight's own start state of a finished stage 8 segment (development; no pokes).

    python tools/s8c_beam_exp.py <state> <seg name under logs/> <guardian|heart> <variant> [<variant> ...] [--prior <inputs>]

A variant is W:offsets[:key=value,...], e.g.  16:0   16:0,2   24:0:strat=150   16:0:slot_value=0.01   12:1:T=4
The fight's start = the segment's rows up to 80 rows before the anchor in its report (guardian_spawn / boss_scroll).
Prints one line per beam (kill row, rows after the anchor, presses).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages.s3s8_engine import Engine  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, read_inputs, history_tail  # noqa: E402
from contra.stages import s8  # noqa: E402


def parse(v):
    parts = v.split(":")
    W = int(parts[0])
    offs = tuple(int(x) for x in parts[1].split(","))
    extra = {}
    if len(parts) > 2:
        for kv in parts[2].split(","):
            k, x = kv.split("=")
            extra[k] = float(x) if "." in x else int(x)
    return (W, offs, extra) if extra else (W, offs)


if __name__ == "__main__":
    args = sys.argv[1:]
    prior = []
    if "--prior" in args:
        i = args.index("--prior")
        prior = history_tail(read_inputs(args[i + 1]))
        del args[i:i + 2]
    state, name, kind = args[0], args[1], args[2]
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / f"{name}.seg.json").read_text())["rows"]]
    rep = json.loads((LOGS_DIR / f"{name}.report.json").read_text())
    anchor = rep["events"]["guardian_spawn" if kind == "guardian" else "boss_scroll"]
    with Engine(3, tag="s8") as eng:
        root = eng.root(state, prior)
        ck0, _ = eng.commit(root, rows[:anchor - 80])
        for v in args[3:]:
            ck = s8.beam_boss(eng, ck0, 0x13, kind, anchor, runs=[parse(v)])
            if ck is None:
                print(f"RESULT {kind} {v}: failed", flush=True)
                continue
            inf = ck.info
            print(f"RESULT {kind} {v}: kill row {inf['kill_row']} (+{inf['kill_row'] - anchor} after the anchor), presses "
                  f"{inf.get('presses')}, item left {inf.get('item_left')}, {inf['seconds']} s", flush=True)

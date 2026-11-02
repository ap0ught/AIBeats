"""Acts 3-4: solve the stages one after another from a chained start state (the Acts 1-2 agent's legal end state
at the 3-1 load, or any of our own end states). Each stage starts from the previous stage's end state (its
next-stage load frame) with the legal history so far.

    python ng/stages/a34_chain.py --start <state name under states/> --hist <inputs file (power-on rows)>
                                  [--from 3-1] [--to 4-4] [--tag ch1] [--W 10]
                                  [--use 3-3=<rows name>]   (replay a fixed rows file for a stage instead of solving)

Writes logs/a34/<stage>_<tag>.inputs.txt per stage, logs/a34/chain_<tag>.inputs.txt (all our stages
concatenated) and logs/a34/chain_<tag>.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402
import a34_solve as S  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402

ORDER = ["3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4"]


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return type(default)(v) if default is not None else v
        return default
    start = opt("--start", "")
    hist_file = opt("--hist", "")
    a = opt("--from", "3-1")
    b = opt("--to", "4-4")
    tag = opt("--tag", "ch1")
    W = opt("--W", 10)
    uses = {}
    while "--use" in args:
        i = args.index("--use")
        k, v = args[i + 1].split("=")
        uses[k] = v
        del args[i:i + 2]
    hist = read_inputs(hist_file) if hist_file else []
    stages = ORDER[ORDER.index(a):ORDER.index(b) + 1]
    summary = {"start": start, "hist": hist_file, "stages": []}
    all_rows = []
    cur = start
    for name in stages:
        hpath = K.OUT_DIR / f"chain_{tag}_hist_before_{name}.inputs.txt"
        write_inputs(hpath, hist + all_rows, f"history before {name}")
        res = S.solve(name, start=cur, hist_file=str(hpath), tag=tag, W=W, sync=False,
                      prefix_name=uses.get(name, ""), log=lambda m: print(m, flush=True))
        rows = K.load_rows(f"{name}_{tag}")
        all_rows += rows
        cur = res["end_state"].replace("states/", "").replace(".State", "")
        summary["stages"].append(res)
        K.save_rows(f"chain_{tag}", all_rows, f"start={start} stages {stages[0]}..{name}")
        (K.OUT_DIR / f"chain_{tag}.json").write_text(json.dumps(summary, indent=1))
        print(f"== {name}: load {res['load']} (TAS {res['tas_load']}, {res['vs_tas']:+d})", flush=True)


if __name__ == "__main__":
    main()

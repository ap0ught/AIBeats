"""chain2 glue (carried from chain1): run the stage 6 or 7 solver from a real state with the real press history.

    python run_s67.py <stage 6|7> <state> <tag> <prior inputs file> <out json> [--param k=v ...]

tools/s6_solve.py has no way to pass the press history on its command line; this calls its run() with it.
Writes <out json> = the solver's facts + "rows" (rows[0] produces the stage's first frame; after the last row the
state is one frame before the next stage's first frame).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "tools"))

from contra.inputs import read_inputs  # noqa: E402
from contra.stages.s6lib import Sim  # noqa: E402
import s6_solve  # noqa: E402  (tools/s6_solve.py of the snapshot)


def main():
    a = sys.argv[1:]
    params = {}
    while "--param" in a:
        i = a.index("--param")
        k, v = a[i + 1].split("=")
        params[k] = int(v)
        del a[i:i + 2]
    stage, state, tag, prior, outj = int(a[0]), a[1], a[2], a[3], a[4]
    hist = read_inputs(prior)[-2000:]
    with Sim(f"chain/s{stage}_{tag}_sim") as sim:
        res, rows = s6_solve.run(sim, stage, state, tag, params or None, True, history=hist)
    res = dict(res)
    res["rows"] = [list(r) for r in rows]
    tmp = Path(outj).with_name(Path(outj).name + ".tmp")
    tmp.write_text(json.dumps(res, default=str), encoding="utf-8")
    tmp.replace(outj)
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "violations", "marks", "remedies")}, indent=1,
                     default=str))


if __name__ == "__main__":
    main()

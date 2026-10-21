"""Rule v2 check of a stage 8 segment on top of the WHOLE real history (not just the tail): writes
<seg>.fullhistory.inputs.txt, runs check_inputs.check with the default windows and reports the violations that lie
in windows reaching into the stage 8 segment separately from those entirely inside the history.

    python tools/s8c_fullcheck.py <prior inputs file> <seg name under logs/>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check_inputs as CI  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

if __name__ == "__main__":
    prior = [tuple(r) for r in read_inputs(ROOT / sys.argv[1])]
    name = sys.argv[2]
    j = json.loads((LOGS_DIR / f"{name}.seg.json").read_text(encoding="utf-8"))
    seg = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
    allr = prior + seg
    out = LOGS_DIR / f"{name}.fullhistory.inputs.txt"
    write_inputs(out, allr, f"full history {len(prior)} rows + segment {len(seg)} rows")
    W = ((600, 109), (1800, 246))
    rep = CI.check(allr, windows=W)
    n0 = len(prior)
    # B starts, sliding maxima for windows that END inside the segment
    st = [i for i, r in enumerate(allr) if "B" in r and (i == 0 or "B" not in allr[i - 1])]
    import bisect
    res = {}
    for w, cap in W:
        best = (0, None)
        for e in range(n0, len(allr)):
            c = bisect.bisect_right(st, e) - bisect.bisect_right(st, e - w)
            if c > best[0]:
                best = (c, e)
        res[f"max_B_in_{w}_ending_in_segment"] = best
    print(json.dumps({"file": str(out), "rows": len(allr), "pass_whole_file": rep["pass"],
                      "violations": {k: r["violations"] for k, r in rep["rules"].items()}, **res}, indent=1))

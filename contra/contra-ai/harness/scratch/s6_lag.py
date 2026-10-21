"""chain2 diagnosis: replay chain A's stage 6 rows from A/s6_pre and list lag frames and progress by row."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from contra.stages.s6lib import Sim
if __name__ == "__main__":
    ch, tag = sys.argv[1], sys.argv[2]
    j = json.loads((HERE / "runs" / ch / f"s6_{tag}_rows.json").read_text())
    rows = [tuple(r) for r in j["rows"]]
    with Sim(f"chain/diag_s6_{ch}") as sim:
        sim.load(f"{ch}/s6_pre")
        tr = sim.run(rows)
    lag = [i for i, f in enumerate(tr) if f["lagged"]]
    print("lag rows", len(lag), lag)
    for i in range(0, len(tr), 50):
        f = tr[i]
        print(i, "x", f["x"], "screen", f["screen"], "scroll", f["scroll"], "fc", f["fc"], "row", "+".join(rows[i]), "lagsofar", sum(1 for l in lag if l <= i))

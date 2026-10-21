"""chain2 diagnosis: chain A stage 6 rows 600-760: buttons, enemies (type table $0528), bullets ($0340?) and lag."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from contra.stages.s6lib import Sim
if __name__ == "__main__":
    ch, tag, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    j = json.loads((HERE / "runs" / ch / f"s6_{tag}_rows.json").read_text())
    rows = [tuple(r) for r in j["rows"]]
    with Sim(f"chain/diag_s6b_{ch}") as sim:
        sim.load(f"{ch}/s6_pre")
        tr = sim.run(rows[:a])
        print(list(tr[-1].keys()) if hasattr(tr[-1], "keys") else tr[-1])
        for i in range(a, b):
            f = sim.run([rows[i]])[-1]
            m = sim.e.ram(0x0528, 16)
            act = sim.e.ram(0x04B8, 16)
            print(i, "+".join(rows[i]) or "-", "lag" if f["lagged"] else "   ", "x", f["x"], "y", f["y"], "types", list(m), "rt", list(act))

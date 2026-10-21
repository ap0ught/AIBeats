"""Development: run the validated climb up to a row and keep the best node's savestate and rows.

    python tools/s3_climb_to.py <q_end> [state=dbg/s3_pre] [emus=3] [name=s3/dbg_q]
Saves states/<name><q_end>.State and logs/<name><q_end>.rows.json; prints the nodes of that row and the enemies.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402
from contra.stages import s3  # noqa: E402

if __name__ == "__main__":
    q_end = int(sys.argv[1])
    state = sys.argv[2] if len(sys.argv) > 2 else "dbg/s3_pre"
    emus = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    name = sys.argv[4] if len(sys.argv) > 4 else "s3/dbg_q"
    valid, cl, games = s3.solve_climb(state, "s3_dbgq", emus, (), 6, 18, q_end)
    try:
        for k in sorted(valid):
            if k[0] <= q_end + 4 and valid[k]:
                print(k, [str(e) for e in valid[k][:4]])
        top = [e for k in valid if k[0] == q_end for e in valid[k]]
        if top:
            best = min(top, key=lambda e: e.t)
            g = games[0]
            r = g.load(best.state, best.pad)
            g.e.save(f"{name}{q_end}")
            (LOGS_DIR / f"{name}{q_end}.rows.json").write_text(json.dumps({"rows": ["+".join(x) for x in best.rows]}))
            print("saved", f"{name}{q_end}", best)
            print("enemies:", r.edesc())
    finally:
        cl.close()
        for g in games:
            g.close()

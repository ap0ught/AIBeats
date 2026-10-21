"""python run_pbeam.py <run> <bookmark> <steps> <width> [scouts] [rollouts] [horizon]"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR
from toads.pbeam import search
from toads import tokens
run, bm, steps, width = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
k = int(sys.argv[5]) if len(sys.argv) > 5 else 6
ro = int(sys.argv[6]) if len(sys.argv) > 6 else 2
hz = int(sys.argv[7]) if len(sys.argv) > 7 else 64
st = int(sys.argv[8]) if len(sys.argv) > 8 else 16
scouts = [BizHawk(log_name=f"pbeam_{run}_{i}.log") for i in range(k)]
t0 = time.time()
try:
    best, hist = search(scouts, bm, run, steps=steps, width=width, rollouts=ro, horizon=hz, step=st,
                        stop=lambda i: i["level"] not in (int(__import__("os").environ.get("LVL", "1")), 0, 255))
finally:
    for e in scouts: e.close()
(LOGS_DIR / f"pbeam_{run}.json").write_text(json.dumps({"bookmark": bm, "inputs": best.inputs, "info": best.info,
                                                        "state": best.state, "history": hist, "wall": time.time() - t0}))
print("done", len(best.inputs), "frames", best.info, f"{time.time()-t0:.0f}s")
tokens.mark(f"pbeam {run}", {"frames": len(best.inputs), "info": best.info})

import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ng import legal
from ng.emulator import BizHawk
from ng.inputs import read_inputs
from ng.mode import TICKS
from run_stage import make_done

if __name__ == "__main__":
    i0 = int(sys.argv[1]); step = int(sys.argv[2]); width = int(sys.argv[3]); hor = int(sys.argv[4])
    ref = legal.TasRef()
    first, tas = ref.stage_rows(0)
    last = ref.control(1)
    j = json.load(open("work/a12/effects_1-1.json"))
    res = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
    hist = read_inputs("logs/a12_intro.inputs.txt")
    proj = legal.enforce(res, hist)
    seg = legal.Segment(ref.tr[first - 1:last], res, raw=tas)
    import os
    seg.progress_mode = os.environ.get("A12_MODE", "nearest")
    seg.height_w = float(os.environ.get("A12_HW", "0"))
    with BizHawk(log_name="a12_probe3.log") as e:
        e.load("ref4751/00_1-1_control"); e.tick(TICKS)
        legal.play(e, proj[:i0])
        rep = legal.Repair(e, seg, history=hist, step=step, width=width, horizon=hor, verbose=True)
        rep._all = hist + proj[:i0]
        leg = legal.Legality(rep._all)
        t = time.time()
        rows, info = rep._beam(leg, i0, 0, make_done(0), min_idx=int(sys.argv[5]) if len(sys.argv) > 5 else 0)
        print("beam", time.time() - t, "s", {k: v for k, v in info.items() if k != "last"}, rep.stats)
        print("ROWS", "|".join("+".join(r) for r in rows))
        tr = legal.play(e, [()] * 1)
        print("end", info["last"])

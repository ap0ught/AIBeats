"""Acts 1-2 chained from power-on (agent a12): intro -> 1-1 -> 1-2 -> 2-1 -> 2-2 -> 2-3 -> 3-1 control.

    python ng/stages/a12_chain.py [--from 1-2] [--to 2-3] [--width 6] [--step 5] [--horizon 16]

Each stage is solved by run_stage.solve_stage() from the previous stage's end state (the next stage's control
frame), with the whole legal history from power-on. Stages already done are reused from
logs/a12_chain_<stage>.inputs.txt (+ states/a12_chain_<stage>_end.State) unless --redo. Writes
logs/a12_chain.inputs.txt (power-on -> last solved stage's end) and logs/a12_chain.json.
Verify afterwards with: python assemble.py a12_act12 logs/a12_chain.inputs.txt --tail 30
and python check_inputs.py logs/a12_act12.inputs.txt
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ng import legal                                  # noqa: E402
from ng.emulator import BizHawk, LOGS_DIR, STATES_DIR  # noqa: E402
from ng.inputs import read_inputs, write_inputs       # noqa: E402
from ng.stages import NAMES                           # noqa: E402
from run_stage import REF_STATE, solve_stage, verify  # noqa: E402

ORDER = ["1-1", "1-2", "2-1", "2-2", "2-3"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", default="1-1")
    ap.add_argument("--to", default="2-3")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--width", type=int, default=6)
    ap.add_argument("--step", type=int, default=5)
    ap.add_argument("--horizon", type=int, default=16)
    ap.add_argument("--esc-lag", type=float, default=8.0)
    ap.add_argument("--esc-horizon", type=int, default=28)
    ap.add_argument("--legal-ref", action="store_true",
                    help="follow logs/a12_<stage>.inputs.txt (a legal solution from the TAS state) when it exists")
    a = ap.parse_args()
    logf = open(LOGS_DIR / "a12_chain.solve.log", "a", encoding="utf-8")

    def log(m):
        line = f"[{time.strftime('%H:%M:%S')}] {m}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()
    intro = read_inputs(LOGS_DIR / "a12_intro.inputs.txt")
    hist = list(intro)
    start = "a12_intro_174"
    summary = json.loads((LOGS_DIR / "a12_chain.json").read_text()) if (LOGS_DIR / "a12_chain.json").exists() else {}
    with BizHawk(log_name="a12_chain_emu.log") as emu:
        for name in ORDER:
            f = LOGS_DIR / f"a12_chain_{name}.inputs.txt"
            idx = ORDER.index(name)
            in_range = ORDER.index(a.frm) <= idx <= ORDER.index(a.to)
            if f.exists() and not (a.redo and in_range):
                rows = read_inputs(f)
                hist += rows
                start = f"a12_chain_{name}_end"
                continue
            if not in_range:
                break
            stage = NAMES.index(name)
            log(f"chain: solving {name} from {start} (history {len(hist)} rows)")
            t = time.time()
            ref_sol = None
            rf = LOGS_DIR / f"a12_{name}.inputs.txt"
            if a.legal_ref and rf.exists() and name != "1-1":
                ref_sol = (read_inputs(rf), "ref4751/" + REF_STATE[stage])
            res = solve_stage(emu, stage, start, hist, log=log, width=a.width, step=a.step, horizon=a.horizon,
                              ref_sol=ref_sol, esc_lag=a.esc_lag, esc_horizon=a.esc_horizon, dump=str(ROOT / "states" / "tmp" / f"a12_chain_{name}.partial.inputs.txt"))
            v = verify(emu, start, res["rows"], stage)
            emu.save(f"a12_chain_{name}_end")
            chk = legal.check(res["rows"], hist)
            ok = v["next_control"] == res["end_frame"] and chk["pass"] and v["deaths"] == 0
            write_inputs(f, res["rows"], f"a12 chain stage {name} from {start}; legal={chk['pass']}")
            summary[name] = {"start_frame": res["start_frame"], "end_frame": res["end_frame"],
                             "frames": res["end_frame"] - res["start_frame"], "tas_frames": res["tas_frames"],
                             "verify": v, "legal": chk["pass"], "ok": ok, "stats": res["stats"],
                             "seconds": round(time.time() - t)}
            (LOGS_DIR / "a12_chain.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
            log(f"chain {name}: {summary[name]['frames']} f (TAS {res['tas_frames']}), end frame {res['end_frame']}, "
                f"verify {v['next_control']}, legal {chk['pass']}, {'OK' if ok else 'NOT OK'}")
            if not ok:
                raise SystemExit(f"stage {name} failed verification")
            hist += res["rows"]
            start = f"a12_chain_{name}_end"
    write_inputs(LOGS_DIR / "a12_chain.inputs.txt", hist, f"a12 chained power-on -> {start}")
    log(f"chain: wrote logs/a12_chain.inputs.txt ({len(hist)} rows), legal {legal.is_legal(hist)}")


if __name__ == "__main__":
    main()

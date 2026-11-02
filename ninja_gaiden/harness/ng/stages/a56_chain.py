"""Acts 5-6: chain the stages legally from a given start state (the Acts 3-4 agent's end state, or a TAS state).

    python ng/stages/a56_chain.py <start state> <history inputs file> [--from 12] [--to 21] [--tag c1]
        [--width W] [--hours-per-stage h] [--prefer <solved tag, e.g. w10>]

For each stage S (from --from, default = the start state's $6D):
  1. if logs/a56_<S>_<prefer>.json exists (a legal solution from the TAS start), replay its rows open-loop from
     the chained state; it counts if the stage completes (no death);
  2. run the beam (reference = that solution if it exists, else the TAS); keep the faster of 1 and 2;
  3. finalize (verified open-loop replay), then continue from the state 150 frames after the load.
The history (for the press windows) is the given inputs file + every row played since. Output:
logs/a56_chain_<tag>.inputs.txt (all rows from the frame after the start state) + logs/a56_chain_<tag>.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402
import a56_solve as S  # noqa: E402
from a56_beam import StageBeam  # noqa: E402

from ng.mode import TICKS  # noqa: E402


def try_replay(e, stage, start, rows, history):
    """Open-loop replay of a stage's rows (made legal again against this history); returns (load frame or None,
    legal rows actually used)."""
    st = e.load(start)
    leg = C.legalize(rows, history=history[-1900:])
    tr = C.play_trace(e, leg)
    for s in tr:
        if s.get("dw") or (s.get("dead", 0) & 0x80):
            return None, leg
        if s["stage"] != stage:
            n = s["frame"] - st["frame"]
            if stage == 21:
                return None, leg
            return s["frame"], leg[:n]
    return None, leg


def main():
    args = sys.argv[1:]
    tag = S.opt(args, "--tag", "c1")
    width = S.opt(args, "--width", 10)
    hps = S.opt(args, "--hours-per-stage", 1.5)
    prefer = S.opt(args, "--prefer", "w10")
    alt = S.opt(args, "--alt", "none")      # replay candidate only (the beam still follows the TAS)
    first = S.opt(args, "--from", -1)
    last = S.opt(args, "--to", 21)
    start, histf = args[0], args[1]
    history = list(C.read_inputs(histf))
    all_rows = []
    report = {"start": start, "history": histf, "stages": []}
    e = C.open_emu(f"a56_chain_{tag}.log")
    try:
        e.tick(TICKS)
        st = e.load(start)
        stage = st["stage"] if first < 0 else first
        cur = start
        while stage <= last:
            nm = C.NAMES[stage]
            t0 = time.time()
            sol = C.PROJECT / "logs" / f"a56_{nm}_{prefer}.json"
            cand = []
            for cs in (sol, C.PROJECT / "logs" / f"a56_{nm}_{alt}.json"):
                if cs.exists() and stage < 21:
                    rows0 = C.read_inputs(json.loads(cs.read_text())["inputs"])
                    load, leg = try_replay(e, stage, cur, rows0, history)
                    print(f"[chain {nm}] open-loop replay of {cs.name}: load {load}", flush=True)
                    if load:
                        cand.append((load, leg, "replay " + cs.stem))
            f0 = e.load(cur)["frame"]
            boss = stage in C.BOSS_STAGES
            b = StageBeam(e, stage, cur, history=history[-1900:], width=width, chunk=5 if boss else 8,
                          ref=C.legal_ref(sol) if sol.exists() else None, boss=boss)
            node = b.run(deadline=time.time() + hps * 3600)
            if node is not None:
                rows = node.rows if stage == 21 else node.rows[:node.done - f0]
                cand.append((node.done, rows, "beam"))
            if not cand:
                print(f"[chain {nm}] FAILED", flush=True)
                break
            cand.sort(key=lambda c: c[0])
            done, rows, how = cand[0]
            rep = S.finalize(e, stage, cur, rows, f"{tag}", {"how": how, "candidates": [(c[0], c[2]) for c in cand]})
            rep["seconds"] = round(time.time() - t0)
            report["stages"].append(rep)
            print(f"[chain {nm}] {how} done {done}; verified {rep['verified']}; hp {rep['hp']} ninpo {rep['ninpo']}",
                  flush=True)
            history += rows
            all_rows += rows
            if stage == 21 or not rep["verified"]:
                break
            blank = [()] * 150
            history += blank
            all_rows += blank
            cur = rep["next_state"]
            stage += 1
            C.save_rows(C.PROJECT / "logs" / f"a56_chain_{tag}.inputs.txt", all_rows,
                        f"a56 chain from {start}; first row = frame after the start state")
            (C.PROJECT / "logs" / f"a56_chain_{tag}.json").write_text(json.dumps(report, indent=1))
        C.save_rows(C.PROJECT / "logs" / f"a56_chain_{tag}.inputs.txt", all_rows,
                    f"a56 chain from {start}; first row = frame after the start state")
        (C.PROJECT / "logs" / f"a56_chain_{tag}.json").write_text(json.dumps(report, indent=1))
    finally:
        e.close()


if __name__ == "__main__":
    main()

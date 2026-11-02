"""Acts 5-6: solve one stage legally with the reference-guided beam, verify open-loop, write the input file.

    python ng/stages/a56_solve.py <stage 12..21> <start state (states/ name)> [--width W] [--chunk C]
        [--history <inputs file whose last rows precede the start>] [--tag name] [--hours h]
        [--ref logs/a56_<name>_<tag>.json]   (follow one of our own legal solutions instead of the TAS)

Output: logs/a56_<stage name>_<tag>.inputs.txt (rows from the frame after the start state up to and including the
next stage's load frame; for 6-5 up to END seen - 1), logs/a56_<name>_<tag>.json (load / END frame, TAS frame,
hp/ninpo/item, open-loop verification), logs/a56_<name>_<tag>.ref.json (per-frame positions, usable as --ref),
and the chain states states/tmp/a56_<name>_<tag>_load.State (at the load frame) and
states/tmp/a56_<name>_<tag>_next.State (load + 150 blank frames = the frame before the next stage's control).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402
from a56_beam import StageBeam  # noqa: E402

from ng import clock  # noqa: E402

REF_FIELDS = ("frame", "stage", "room", "x", "xsub", "y", "scroll", "scroll_scr", "hp", "ninpo", "item", "bosshp", "boss_real",
              "timer", "subtimer")


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v) if default is not None else v
    return default


def solve(stage, start, width=8, chunk=4, tag="t", hours=3.0, histf=None, ref=None, log=None, beam_kw=None,
          prefix=None):
    """prefix: rows played open-loop from `start` before the beam takes over (refinement of a later window)."""
    nm = C.NAMES[stage]
    e = C.open_emu(f"a56_solve_{nm}_{tag}.log")
    try:
        st = e.load(start)
        f0 = st["frame"]
        if histf:
            history = C.read_inputs(histf)[-1900:]
        else:
            history = C.legalize(C.tas_rows()[max(0, f0 - 1900):f0])
        kw = dict(beam_kw or {})
        if stage in C.BOSS_STAGES:
            kw.setdefault("boss", True)
        bstart = start
        prefix = list(prefix or [])
        if prefix:
            from ng.mode import TICKS
            e.tick(TICKS)
            e.load(start)
            history = list(history) + C.legalize(prefix, history=history)
            bstart = e.run(prefix)
        b = StageBeam(e, stage, bstart, history=history, width=width, chunk=chunk,
                      ref=C.legal_ref(ref) if ref else None, log=log, **kw)
        node = b.run(deadline=time.time() + hours * 3600)
        if node is None:
            return None
        rows = prefix + node.rows
        if stage < 21:
            rows = rows[:node.done - f0]
        return finalize(e, stage, start, rows, tag, {"ref": b.ref["name"], "evals": b.evals, "beam_width": width,
                                                     "chunk": chunk, "search_done": node.done})
    finally:
        e.close()


def finalize(e, stage, start, rows, tag, extra=None):
    """Replay rows open-loop from start; write inputs, .json report, .ref.json trace and chain states."""
    nm = C.NAMES[stage]
    st = e.load(start)
    f0 = st["frame"]
    tr = C.play_trace(e, rows)
    rep = {"stage": nm, "start": start, "start_frame": f0, "rows": len(rows)}
    rep.update(extra or {})
    if stage < 21:
        load = next((s["frame"] for s in tr if s["stage"] != stage), None)
        e.save(f"tmp/a56_{nm}_{tag}_load")
        s2 = e.run([()] * 150)
        e.save(f"tmp/a56_{nm}_{tag}_next")
        tas_load = C.tas_stage(stage + 1)["load"]
        rep.update({"load": load, "verified": load is not None and load == len(rows) + f0,
                    "tas_load": tas_load, "frames_from_start": (load or 0) - f0,
                    "tas_frames_from_control": tas_load - C.tas_stage(stage)["control"],
                    "next_state": f"tmp/a56_{nm}_{tag}_next", "next_state_frame": s2["frame"]})
    else:
        tr2 = tr + C.play_trace(e, [()] * 12)
        end = clock.end_frame(tr2)
        seen = end and end.get("seen")
        rep.update({"end": end, "load": seen, "verified": seen is not None and seen == len(rows) + f0 + 1,
                    "tas_end_seen": 39530, "frames_from_start": (seen or 0) - f0})
        e.load(start)
        e.run(rows[:-1] if rows else [])
        e.save(f"tmp/a56_{nm}_{tag}_end")
    last = tr[-1]
    rep.update({"hp": last["hp"], "ninpo": last["ninpo"], "item": last["item"], "timer": last["timer"],
                "subtimer": last["subtimer"], "rng": last["rng"]})
    out = C.PROJECT / "logs" / f"a56_{nm}_{tag}.inputs.txt"
    C.save_rows(out, rows, f"a56 {nm} from {start} (frame {f0}); first row = frame {f0 + 1}; "
                           f"done {rep.get('load')}")
    rep["inputs"] = str(out)
    refj = {"start": {k: st.get(k, 0) for k in REF_FIELDS},
            "trace": {s["frame"]: {k: s.get(k, 0) for k in REF_FIELDS} for s in tr}}
    (C.PROJECT / "logs" / f"a56_{nm}_{tag}.ref.json").write_text(json.dumps(refj))
    (C.PROJECT / "logs" / f"a56_{nm}_{tag}.json").write_text(json.dumps(rep, indent=1))
    return rep


def main():
    args = sys.argv[1:]
    width = opt(args, "--width", 8)
    chunk = opt(args, "--chunk", 4)
    tag = opt(args, "--tag", "t")
    hours = opt(args, "--hours", 3.0)
    histf = opt(args, "--history", None)
    ref = opt(args, "--ref", None)
    fin_rows = opt(args, "--finalize", None)
    pre = opt(args, "--prefix", None)
    pre_n = opt(args, "--prefix-frames", 0)
    if fin_rows:
        e = C.open_emu(f"a56_finalize_{tag}.log")
        try:
            from ng.mode import TICKS
            e.tick(TICKS)
            rep = finalize(e, int(args[0]), args[1], C.read_inputs(fin_rows), tag, {"finalized_from": fin_rows})
        finally:
            e.close()
        print(json.dumps(rep))
        return
    prefix = C.read_inputs(pre)[:pre_n] if pre else None
    rep = solve(int(args[0]), args[1], width, chunk, tag, hours, histf, ref, prefix=prefix)
    if rep is None:
        print("FAILED")
        sys.exit(2)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()

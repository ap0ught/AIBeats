"""Acts 1-2 round 2: solve one stage legally along the RECORD's route (waypoints from the record video) or the TAS.

    python ng/stages/a12r2_solve.py <stage 0..4> <start state> --history <legal inputs from power-on up to the start>
        [--rec work/a12r2/rec/r21.json | --tasref] [--prefix <inputs> --prefix-frames N] [--width 8] [--chunk 8]
        [--hours 2] [--tag t] [--k0 <ref frame offset for the beam pointer>]

The search is agent a56's StageBeam (ng/stages/a56_beam.py, imported read-only): every row goes through the
legal Enforcer; score = progress along the reference (largest k - 0.75|dX| - 0.5|dy| near the pointer), hp / ninpo /
item penalties vs the reference (taken from the TAS at the time-warped frame), go-explore when stuck. With --rec the
reference is ng/legal.waypoint_ref() (record positions in record time from our start frame), so "lag" = frames
behind the record holder.

Output (stage file convention of round 1: rows from the frame after the start state up to and including the next
stage's control frame):
  logs/a12r2_<stage>_<tag>.inputs.txt, logs/a12r2_<stage>_<tag>.json (verify, frames, legality),
  states/a12r2_<stage>_<tag>_end.State (= the next stage's control frame).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import a56_common as C  # noqa: E402
from a56_beam import StageBeam  # noqa: E402

from ng import legal  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

NAMES = C.NAMES
RECORD_FRAMES = {0: 2309.8, 1: 841.4, 2: 2904.8, 3: 3101.1, 4: 833.3}
TAS_FRAMES = {0: 2294, 1: 834, 2: 2802, 3: 2895, 4: 830}


def opt(a, n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v) if d is not None else v
    return d


def to_control(e, stage, rows_hist):
    """Play blank rows (Start held 2 frames on the first cutscene frame where it skips) until the play loop runs in
    the next stage. Returns rows."""
    leg = legal.Legality(rows_hist[-1900:])
    rows = []
    skipped = False
    e.trace(True)
    for _ in range(9000):
        s = e.state()
        if s.get("stage") == stage + 1 and s.get("gm"):
            return rows
        r = ()
        if s.get("cs") and not skipped and leg.can(("Start",)):
            sid = e.msave()
            e.run([("Start",), ("Start",)])
            ok = any(x.get("csskip") for x in e.last_trace)
            e.mload(sid)
            e.mfree(sid)
            if ok:
                for rr in (("Start",), ("Start",)):
                    e.run([rr])
                    leg.push(rr)
                    rows.append(rr)
                skipped = True
                continue
        e.run([r])
        leg.push(r)
        rows.append(r)
    raise RuntimeError("no control within 9000 frames")


def verify(e, stage, start, rows, history):
    """Open-loop replay from start: (control frame reached, deaths, last state, legal)."""
    st = e.load(start)
    f0 = st["frame"]
    tr = C.play_trace(e, rows)
    deaths = sum(1 for s in tr if s.get("dw"))
    last = tr[-1]
    ok_ctl = last.get("stage") == stage + 1 and last.get("gm") and not any(
        s.get("stage") == stage + 1 and s.get("gm") for s in tr[:-1])
    chk = legal.check(rows, history)
    return {"start_frame": f0, "control_frame": last["frame"], "frames": last["frame"] - f0, "deaths": deaths,
            "control_ok": bool(ok_ctl), "legal": chk["pass"], "hp": last["hp"], "ninpo": last["ninpo"],
            "item": last["item"], "rng": last.get("rng")}


def main():
    a = sys.argv[1:]
    rec = opt(a, "--rec", None)
    tasref = "--tasref" in a
    if tasref:
        a.remove("--tasref")
    hybrid = "--hybrid" in a
    if hybrid:
        a.remove("--hybrid")
    hpad = opt(a, "--hpad", 30)
    explore_n = opt(a, "--explore", 0)
    histf = opt(a, "--history", None)
    pre = opt(a, "--prefix", None)
    pre_n = opt(a, "--prefix-frames", 0)
    width = opt(a, "--width", 8)
    chunk = opt(a, "--chunk", 8)
    hours = opt(a, "--hours", 2.0)
    tag = opt(a, "--tag", "t")
    tshift = opt(a, "--tshift", 0)
    opfx = opt(a, "--pfx", "a12r2")
    stage, start = int(a[0]), a[1]
    nm = NAMES[stage]
    out = f"{opfx}_{nm}_{tag}"
    logf = open(ROOT / "logs" / f"{out}.solve.log", "a", encoding="utf-8")

    def log(*x):
        s = time.strftime("%H:%M:%S ") + " ".join(str(y) for y in x)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    history = [tuple(r) for r in read_inputs(histf)] if histf else []
    prefix = [tuple(r) for r in read_inputs(pre)[:pre_n]] if pre else []
    e = C.open_emu(f"{out}_emu.log")
    try:
        e.tick(TICKS)
        st = e.load(start)
        f0 = st["frame"]
        log(f"{out}: stage {nm} from {start} (frame {f0}), history {len(history)} rows, prefix {len(prefix)}, "
            f"ref {'TAS' if tasref or not rec else rec}, width {width} chunk {chunk} hours {hours}")
        hist = history + prefix
        if prefix:
            assert legal.is_legal(prefix, history), "prefix not legal"
            bstart = e.run(prefix)
        else:
            bstart = st
        if rec and hybrid:
            wp = legal.Waypoints(rec, stage)
            ref = legal.hybrid_ref(wp, f0 - tshift, pad=hpad, name="hybrid_" + Path(rec).stem, ud="--ud" in sys.argv)
            log(f"hybrid ref: TAS with record segments {ref['segments']} (TAS k, record t)")
        elif rec and not tasref:
            wp = legal.Waypoints(rec, stage)
            ref = legal.waypoint_ref(wp, f0 - tshift, name=Path(rec).stem)
            log(f"waypoints: {len(wp.pts)} points, record t 0..{wp.tend}, xoff {wp.xoff} yoff {wp.yoff}; "
                f"ref frames {ref['control']}..{ref['load_next']}")
        else:
            ref = None
        kw = {}
        if stage in (1, 4):
            kw["boss"] = True
        b = StageBeam(e, stage, bstart, history=hist[-1900:], width=width, chunk=chunk, ref=ref, log=log, **kw)
        b.dump = ROOT / "states" / "tmp" / f"{out}.partial.inputs.txt"
        if explore_n and not b.boss:
            b.explore_budget = explore_n
        if not b.boss and "--no-climb" not in sys.argv:
            # legal 5-frame wall-climb cycles (knowledge/legal_a12_notes.md "Walls"), every phase, as explicit rows
            for away, back in (("Left", "Right"), ("Right", "Left")):
                # 5-frame cycles do not re-grab the wall in 2-1 room 3 (probe 17:55); the 7-frame cycle
                # (away+A x2, back x5) is the fastest one that does (~1.1 px/f; 8-frame = MACROS8 "^" k 2)
                for cyc in ([(away, "A"), (away, "A")] + [(back,)] * 5,):
                    for ph in range(7):
                        b.macros = list(b.macros) + [("R",) + tuple((cyc * 4)[ph:ph + chunk])]
        node = b.run(deadline=time.time() + hours * 3600)
        if node is None:
            log("FAILED")
            sys.exit(2)
        rows = prefix + node.rows[:node.done - bstart["frame"]]
        # continue to the next control frame
        e.load(start)
        e.run(rows)
        tail = to_control(e, stage, history + rows)
        rows += tail
        rep = verify(e, stage, start, rows, history)
        e.save(f"{out}_end")
        rep.update({"stage": nm, "start": start, "tag": tag, "ref": ref["name"] if ref else "tas4751",
                    "tas_frames": TAS_FRAMES.get(stage), "record_frames": RECORD_FRAMES.get(stage),
                    "end_state": f"{out}_end", "evals": b.evals, "load": node.done})
        rep["vs_tas"] = rep["frames"] - TAS_FRAMES.get(stage, 0)
        rep["vs_record"] = round(rep["frames"] - RECORD_FRAMES.get(stage, 0), 1)
        write_inputs(ROOT / "logs" / f"{out}.inputs.txt", rows,
                     f"a12r2 stage {nm} from {start} (frame {f0}) to the next control {rep['control_frame']}; "
                     f"legal={rep['legal']}")
        (ROOT / "logs" / f"{out}.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
        log("RESULT", json.dumps(rep))
    finally:
        e.close()
        logf.close()


if __name__ == "__main__":
    main()

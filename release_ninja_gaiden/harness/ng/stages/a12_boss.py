"""Boss-stage beam without a TAS line (agent a12): kill the boss as early as possible with legal input.

    python ng/stages/a12_boss.py --stage 1-2 --start <state> --history <inputs> [--out name] [--width 12] [--step 4]

Score of a node = frames played + hp_w * boss HP ($0497) + 0.04 * |Ryu x - boss x| (+ 6 per Ryu HP lost);
nodes that die are dropped; nodes are deduplicated by (Ryu x/y/vy/anim/flags, boss x/y/HP, ninpo).
Done = the boss-kill tally starts (tick bk); then run_stage.tail_to_control() plays to the next control frame
(Start skips the cutscene as early as legal). Output: logs/<out>.inputs.txt + .stage.json, states/<out>_end.
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

from ng import legal                                   # noqa: E402
from ng.emulator import BizHawk, LOGS_DIR, load_fields  # noqa: E402
from ng.inputs import read_inputs, write_inputs        # noqa: E402
from ng.mode import TICKS                              # noqa: E402
from ng.stages import NAMES                            # noqa: E402
from run_stage import tail_to_control, verify          # noqa: E402

MACROS = []


def macros(step):
    out = []
    for d in ((), ("Right",), ("Left",)):
        for a in (False, True):
            for b in (False, True):
                rows = []
                for f in range(step):
                    r = set(d)
                    if a and f < 2:
                        r.add("A")
                    if b and f < 2:
                        r.add("B")
                    rows.append(tuple(r))
                out.append(rows)
    for d in ((), ("Right",), ("Left",)):
        out.append([tuple(set(d) | {"Down", "B"})] * 2 + [tuple(d)] * (step - 2))
        out.append([tuple(set(d) | {"Up", "B"})] * 2 + [tuple(d)] * (step - 2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--history", required=True)
    ap.add_argument("--out")
    ap.add_argument("--width", type=int, default=12)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--hp-w", type=float, default=8.0)
    ap.add_argument("--max", type=int, default=900)
    a = ap.parse_args()
    stage = NAMES.index(a.stage)
    out = a.out or f"a12_boss_{a.stage}"
    hist = read_inputs(a.history)
    logf = open(LOGS_DIR / f"{out}.solve.log", "a", encoding="utf-8")

    def log(m):
        line = f"[{time.strftime('%H:%M:%S')}] {m}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()
    fields = dict(load_fields())
    fields.update({"bx": 0x467, "by": 0x487})
    with BizHawk(log_name=f"{out}_emu.log", fields=fields) as e:
        s0 = e.load(a.start)
        e.tick(TICKS)
        e.trace(False)
        root = {"sid": e.msave(), "leg": legal.Legality(hist), "rows": [], "last": e.state(), "score": 0.0}
        beam = [root]
        best_done = None
        sids = [root["sid"]]
        hp0 = root["last"]["hp"]
        mac = macros(a.step)
        t = time.time()
        for depth in range(a.max // a.step):
            children = {}
            for node in beam:
                for m in mac:
                    lg = node["leg"].copy()
                    rows = []
                    for r in m:
                        r = legal.norm(r)
                        if not lg.can(r):
                            r = lg.fix(r)
                        lg.push(r)
                        rows.append(r)
                    e.mload(node["sid"])
                    tr = legal.play(e, rows, chunk=len(rows))
                    if any(s.get("dw") or (s.get("dead", 0) & 0x80) for s in tr) or tr[-1]["lives"] < root["last"]["lives"]:
                        continue
                    fin = next((q for q, s in enumerate(tr) if s.get("bk") or s.get("stage") != stage), None)
                    allrows = node["rows"] + rows
                    if fin is not None:
                        n = len(node["rows"]) + fin + 1
                        if best_done is None or n < len(best_done["rows"]):
                            best_done = {"rows": allrows[:n]}
                        continue
                    s = tr[-1]
                    sc = len(allrows) + a.hp_w * s.get("boss_real", 0) + 0.04 * abs(s["x"] - s.get("bx", s["x"])) \
                        + 6.0 * max(0, hp0 - s["hp"])
                    key = (s["x"], s["xsub"], s["y"], s["vy"], s["anim"], s["rflags"], s.get("bx"), s.get("by"),
                           s.get("boss_real"), s["ninpo"], s["hp"])
                    if key in children and children[key]["score"] <= sc:
                        continue
                    if key in children:
                        e.mfree(children[key]["sid"])
                    children[key] = {"rows": allrows, "leg": lg, "last": s, "score": sc, "sid": e.msave()}
            if best_done is not None and all(len(c["rows"]) + 1 >= len(best_done["rows"]) for c in children.values()):
                break
            if not children:
                break
            ranked = sorted(children.values(), key=lambda c: c["score"])
            for c in ranked[a.width:]:
                e.mfree(c["sid"])
            for c in beam:
                if c is not root:
                    e.mfree(c["sid"])
            beam = ranked[:a.width]
            b0 = beam[0]
            log(f"depth {depth}: {len(children)} children, best score {b0['score']:.1f} boss HP "
                f"{b0['last'].get('boss_real')} x {b0['last']['x']} bx {b0['last'].get('bx')} hp {b0['last']['hp']}")
        if best_done is None:
            raise SystemExit("no kill found")
        rows = best_done["rows"]
        e.mload(root["sid"])
        legal.play(e, rows)
        for c in beam:
            try:
                e.mfree(c["sid"])
            except Exception:
                pass
        log(f"kill after {len(rows)} rows ({time.time() - t:.0f} s)")
        tail = tail_to_control(e, stage, hist + rows, log)
        rows = rows + tail
        end = e.state()
        v = verify(e, a.start, rows, stage)
        e.save(f"{out}_end")
    chk = legal.check(rows, hist)
    ok = v["next_control"] == end["frame"] and chk["pass"] and v["deaths"] == 0
    rep = {"stage": a.stage, "start": a.start, "start_frame": s0["frame"], "end_frame": end["frame"],
           "frames_control_to_control": end["frame"] - s0["frame"], "verify": v, "legal": chk["pass"], "ok": ok}
    write_inputs(LOGS_DIR / f"{out}.inputs.txt", rows, f"boss beam {a.stage} from {a.start}; legal={chk['pass']}")
    (LOGS_DIR / f"{out}.stage.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    log(f"RESULT {a.stage}: {rep['frames_control_to_control']} f control->control; verify {v['next_control']} "
        f"vs {end['frame']}; legal {chk['pass']}; {'OK' if ok else 'NOT OK'}")


if __name__ == "__main__":
    main()

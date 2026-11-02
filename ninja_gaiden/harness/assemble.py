"""Stitch segments into one input list from power-on, replay it twice, compare, and time it with ng/clock.py.

    python assemble.py <route> <segment> [<segment> ...] [--tail N] [--serial] [--launch]

segment:  logs/<x>.inputs.txt        a plain input list (the first segment must start at power-on)
          logs/<x>.seg.json          {"rows": ["Right+B", ...]}  (or {"inputs": [...]})
          blank:<n>                  n frames of nothing
--tail N  append N empty frames (default 0)
--launch  play on the fresh launch (row k -> frame k+1) instead of after reset() (row k -> frame k, = bk2 numbering)

Writes logs/<route>.inputs.txt and logs/<route>.report.json. Two independent NesHawk instances replay the list
(in parallel unless --serial); the 2 KB RAM SHA-1 after the last frame must match, and so must the SHA-1 of the
per-frame trace (all knowledge/ram.json fields + ng.mode ticks). Then: per-stage table (ng/events.py), deaths,
cutscenes, game-lag frames, and START / END / RUN TIME (ng/clock.py). Exit code 2 on a mismatch.
This prints a time; it does NOT claim anything about the record (that needs the record's own video timing and an
independent re-derivation).
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from pathlib import Path

from ng import clock
from ng.emulator import BizHawk, LOGS_DIR
from ng.events import analyse
from ng.inputs import read_inputs, write_inputs
from ng.mode import TICKS


def load_segment(spec: str) -> list[tuple[str, ...]]:
    if spec.startswith("blank:"):
        return [()] * int(spec.split(":")[1])
    p = Path(spec)
    if not p.exists():
        p = LOGS_DIR / spec
    if p.suffix == ".json":
        j = json.loads(p.read_text(encoding="utf-8"))
        rows = j.get("rows", j.get("inputs"))
        if rows is None or (("done" in j) and not j["done"]):
            raise SystemExit(f"{spec}: no finished rows in it")
        return [tuple(x for x in r.replace(",", "+").split("+") if x) for r in rows]
    return read_inputs(p)


def replay(route: str, rows, tag: str, out: dict, launch: bool) -> None:
    e = BizHawk(log_name=f"{route}_replay_{tag}.log")
    try:
        if not launch:
            e.reset()                 # reset drops Lua memory callbacks: set the ticks after it
        e.tick(TICKS)
        e.trace(True)
        tr = []
        for i in range(0, len(rows), 2000):
            e.run(rows[i:i + 2000])
            tr.extend(e.last_trace)
        ram = e.ram_all()
        out[tag] = {"ram_sha1": hashlib.sha1(ram).hexdigest(), "trace": tr,
                    "trace_sha1": hashlib.sha1("\n".join(str(s) for s in tr).encode()).hexdigest()}
    finally:
        e.close()


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            if isinstance(default, bool):
                del args[i]
                return True
            v = args[i + 1]
            del args[i:i + 2]
            return type(default)(v)
        return default
    tail, serial, launch = opt("--tail", 0), opt("--serial", False), opt("--launch", False)
    route, segs = args[0], args[1:]
    rows, marks = [], []
    for sp in segs:
        marks.append((len(rows) + 1, sp))
        rows += load_segment(sp)
    rows += [()] * tail
    same = len(segs) == 1 and Path(segs[0]).resolve() == (LOGS_DIR / f"{route}.inputs.txt").resolve()
    if not same:
        write_inputs(LOGS_DIR / f"{route}.inputs.txt", rows,
                     f"assembled from {len(segs)} segment(s); play after {'fresh launch' if launch else 'reset()'}")
    out = {}
    th = [threading.Thread(target=replay, args=(route, rows, t, out, launch)) for t in ("a", "b")]
    if serial:
        for t in th:
            t.start(); t.join()
    else:
        for t in th:
            t.start()
        for t in th:
            t.join()
    if "a" not in out or "b" not in out:
        raise SystemExit("a replay failed; see logs/")
    ok = out["a"]["ram_sha1"] == out["b"]["ram_sha1"] and out["a"]["trace_sha1"] == out["b"]["trace_sha1"]
    tr = out["a"]["trace"]
    rep = analyse(tr)
    rep["clock"] = clock.measure(tr)
    rep.update({"route": route, "input_frames": len(rows), "start_mode": "launch" if launch else "reset",
                "segments": [{"first_row": f, "segment": s} for f, s in marks],
                "ram_sha1_a": out["a"]["ram_sha1"], "ram_sha1_b": out["b"]["ram_sha1"],
                "trace_sha1_a": out["a"]["trace_sha1"], "trace_sha1_b": out["b"]["trace_sha1"], "replays_match": ok})
    (LOGS_DIR / f"{route}.report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(f"{route}: {len(rows)} input frames ({'launch' if launch else 'reset'}); two power-on replays "
          f"{'MATCH' if ok else 'MISMATCH'} (RAM sha1 {out['a']['ram_sha1'][:12]} / {out['b']['ram_sha1'][:12]}, "
          f"trace sha1 {out['a']['trace_sha1'][:12]} / {out['b']['trace_sha1'][:12]})")
    for st in rep["stages"]:
        extra = "".join(f"  {k} {st[k]}" for k in ("boss0", "control_to_next_control") if k in st)
        print(f"  {st['name']:5s} load {st.get('load')}  control {st.get('control')}{extra}")
    print(f"  deaths {len(rep['deaths'])}; cutscenes {len(rep['cutscenes'])} "
          f"(skipped {sum(c['skipped'] for c in rep['cutscenes'])}); game-lag frames {rep['game_lag_frames']}; "
          f"BizHawk lag frames {rep['bizhawk_lag_total']}")
    c = rep["clock"]
    if c["finished"]:
        print(f"{route}: START RAM {c['start']['ram']} seen {c['start']['seen']}; END RAM {c['end']['ram']} seen "
              f"{c['end']['seen']}; RUN TIME {c['time']} = {c['frames']} frames / 60.0988")
    else:
        print(f"{route}: NOT FINISHED - start {c['start']}, end {c['end']}; no run time.")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()

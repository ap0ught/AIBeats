"""Stitch segments into one input list from power-on, replay it twice, compare, and time it with contra/clock.py.

    python assemble.py <route> <segment> [<segment> ...] [--core NesHawk] [--tail N] [--record] [--serial]

segment:  logs/<x>.inputs.txt        a plain input list (the first segment must start at power-on)
          logs/<x>.seg.json          {"rows": ["Right+B", ...]}   (tools/repair.py, tools/build_ref.py)
          logs/pbeam_<x>.json        {"inputs": ["Right+B", ...]} (beam search output)
          blank:<n>                  n frames of nothing
--tail N  append N empty frames (default 0)

Writes logs/<route>.inputs.txt and logs/<route>.report.json. Two independent emulators replay the list from
power-on (in parallel unless --serial); the 2 KB RAM SHA-1 after the last frame must match, and so must the
SHA-1 of the per-frame trace of the clock/state bytes. Then:
    START / END frames (RAM and as seen) and the RUN TIME under the leaderboard rule (frames / 60.0988),
    per-stage frames and lag frames, frames on which the game ignored the controller (see README_HARNESS.md).
This prints a time; it does NOT claim anything about the record (that needs the record's own video timing).
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from pathlib import Path

from contra import clock
from contra.emulator import BizHawk, LOGS_DIR
from contra.inputs import read_inputs, to_mask, write_inputs

FIELDS = dict(clock.FIELDS)
FIELDS.update({"lives": 0x32, "death": 0xB4, "screen": 0x64, "scroll": 0x65, "weapon": 0xAA, "fc": 0x1A, "rng": 0x34,
               "gameover": 0x38, "loc": 0x40, "pause": 0x25, "x": 0x334, "y": 0x31A})


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


def replay(route: str, rows, core: str, tag: str, out: dict, record: bool = False) -> None:
    e = BizHawk(log_name=f"{route}_replay_{tag}.log", fields=FIELDS, core=core, record=f"{route}" if record else None)
    try:
        e.trace(True)
        e.run(rows)
        tr = e.last_trace
        ram = e.ram_all()
        out[tag] = {"ram_sha1": hashlib.sha1(ram).hexdigest(), "trace": tr, "core": e.info["core_seen"],
                    "trace_sha1": hashlib.sha1("\n".join(str(s) for s in tr).encode()).hexdigest()}
    finally:
        e.close()


def analyse(rows, tr) -> dict:
    """Stage table, lag, ignored-controller frames, clock. tr[i] is the state after rows[i]."""
    rep = clock.measure(tr)
    if "frames" in rep:
        rep["frames_timed"] = rep.pop("frames")
    stages = {}
    prev = None
    deaths = 0
    ignored = []
    for i, s in enumerate(tr):
        lv = s["level"]
        if s["groutine"] == 5 and s["demo"] == 0 and lv < 8:
            st = stages.setdefault(lv, {"stage": lv + 1})
            if s["lroutine"] == 4 and "first_frame" not in st:
                st["first_frame"] = s["frame"]
                st["lag_at_first_frame"] = s["lag"]
                st["weapon_at_start"] = s["weapon"]
                st["rooms"] = []
            if "first_frame" in st and s["lroutine"] == 4 and s["loc"] in (1, 0x80) and prev is not None \
                    and prev["level"] == lv and s["screen"] != prev["screen"]:
                st["rooms"].append({"room": s["screen"], "frame": s["frame"]})
            if s["bossdef"] == 1 and "boss_defeated_frame" not in st and "first_frame" in st:
                st["boss_defeated_frame"] = s["frame"]
            if s["lroutine"] == 9 and "control_lost_frame" not in st and "first_frame" in st:
                st["control_lost_frame"] = s["frame"]
        if prev is not None:
            if s["level"] != prev["level"] and prev["level"] in stages and "first_frame" in stages[prev["level"]]:
                stages[prev["level"]]["level_byte_change_frame"] = s["frame"]
                stages[prev["level"]]["lag_at_level_change"] = s["lag"]
            if (s["death"] & 1) and not (prev["death"] & 1) and s["groutine"] == 5:
                deaths += 1
        # the game read something else than what was sent (DMC conflict -> it reuses the previous frame's read)
        if not s["lagged"] and s["groutine"] == 5 and s["lroutine"] == 4 and s["pause"] == 0 and s["pad"] != to_mask(rows[i]):
            ignored.append(s["frame"])
        prev = s
    order = sorted(k for k in stages if "first_frame" in stages[k])
    table = []
    for n, k in enumerate(order):
        st = stages[k]
        nxt = stages[order[n + 1]] if n + 1 < len(order) else None
        if nxt:
            end, lag_end, how = nxt["first_frame"], nxt["lag_at_first_frame"], "to the next stage's first frame"
        elif rep.get("end"):
            end = rep["end"]["ram"]
            lag_end = next(s["lag"] for s in tr if s["frame"] == end)
            how = "to the END event (RAM frame)"
        else:
            end, lag_end, how = tr[-1]["frame"], tr[-1]["lag"], "to the end of the inputs (NOT finished)"
        st["frames"] = end - st["first_frame"]
        st["lag_frames"] = lag_end - st["lag_at_first_frame"]
        st["measured"] = how
        if "level_byte_change_frame" in st:
            st["frames_in_level"] = st["level_byte_change_frame"] - st["first_frame"]
        table.append(st)
    rep.update({"stages": table, "deaths": deaths, "controller_ignored_frames": len(ignored),
                "controller_ignored_first": ignored[:20], "lag_total": tr[-1]["lag"], "last_state": dict(tr[-1])})
    return rep


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
    core, tail = opt("--core", "NesHawk"), opt("--tail", 0)
    record, serial = opt("--record", False), opt("--serial", False)
    route, segs = args[0], args[1:]
    rows = []
    marks = []
    for sp in segs:
        marks.append((len(rows) + 1, sp))
        rows += load_segment(sp)
    rows += [()] * tail
    same = len(segs) == 1 and Path(segs[0]).resolve() == (LOGS_DIR / f"{route}.inputs.txt").resolve()
    if not same:
        write_inputs(LOGS_DIR / f"{route}.inputs.txt", rows, f"assembled from {len(segs)} segment(s), core={core}")
    out = {}
    th = [threading.Thread(target=replay, args=(route, rows, core, "a", out)),
          threading.Thread(target=replay, args=(route, rows, core, "b", out, record))]
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
    rep = analyse(rows, out["a"]["trace"])
    rep.update({"route": route, "input_frames": len(rows), "core": out["a"]["core"], "segments": [{"first_row": f, "segment": s} for f, s in marks],
                "ram_sha1_a": out["a"]["ram_sha1"], "ram_sha1_b": out["b"]["ram_sha1"],
                "trace_sha1_a": out["a"]["trace_sha1"], "trace_sha1_b": out["b"]["trace_sha1"], "replays_match": ok})
    (LOGS_DIR / f"{route}.report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(f"{route}: {len(rows)} input frames on {rep['core']}; two power-on replays "
          f"{'MATCH' if ok else 'MISMATCH'} (RAM sha1 {out['a']['ram_sha1'][:12]} / {out['b']['ram_sha1'][:12]}, "
          f"trace sha1 {out['a']['trace_sha1'][:12]} / {out['b']['trace_sha1'][:12]})")
    for st in rep["stages"]:
        rooms = f"  rooms at {[r['frame'] for r in st['rooms']]}" if st.get("rooms") else ""
        print(f"  stage {st['stage']}: first frame {st['first_frame']:6d}  frames {st['frames']:5d}  lag {st['lag_frames']:3d}  "
              f"weapon ${st['weapon_at_start']:02x}  ({st['measured']}){rooms}")
    print(f"  deaths {rep['deaths']}; lag frames in total {rep['lag_total']}; frames on which the game ignored the "
          f"controller during play {rep['controller_ignored_frames']}")
    if rep["finished"]:
        st, en = rep["start"], rep["end"]
        print(f"{route}: START medals: RAM frame {st['ram']}, seen on frame {st['seen']}; END Bill stands: control lost "
              f"{en['control_lost']}, RAM frame {en['ram']}, seen on frame {en['seen']} (Up/Down held: {en['up_or_down_held']})")
        print(f"{route}: RUN TIME {rep['time']} = {rep['frames_timed']} frames / 60.0988"
              f"  (as seen: {st['seen']} -> {en['seen']})")
    else:
        print(f"{route}: NOT FINISHED - start {rep['start']}, end {rep['end']}; no run time. Last state: {rep['last_state']}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()

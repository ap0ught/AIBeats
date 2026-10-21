"""Stitch the run together: the fixed intro plus the searched segments, from power-on, with the panel's notes.

    python assemble.py <route name> <segment>...      segment = logs/pbeam_<name>.json (in order)

Writes logs/<route>.inputs.txt / .events.txt, verifies it twice from power-on (RAM SHA-1 must match), records
the second replay with A/V, and reports the run time on the leaderboard's terms (fixed 2026-10-09):

    clock start = the toad landing in level 1 ($3B5 5->4)
    clock stop  = the cut to Professor T. Bird's final dialogue = the SECOND time the level byte goes 13 -> 254.

The FIRST 13 -> 254 is only the cut to the Dark Queen's speech (the game returns to the tower after it); it is reported
as queen_speech_cut for reference and is NOT the end of the run (up14's "12:23.39" was that number; real time 12:31.75).
A route whose inputs stop before the T. Bird cut is reported as NOT FINISHED. See knowledge/end_timing.md, end_tail.py.
"""
import hashlib
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR
from toads import tokens

INTRO = [("Right", 1170, "POWER ON. Right held from frame 1: with a direction held through the logos the title accepts "
                         "Start 349 frames sooner (frame 1,170).||Measured by pressing Start on every frame from 1,161"),
         ("Start", 4, "START on 1,170, the first frame that counts.||1,169 is ignored; bisected"),
         ("A", 727, "Holding A: the story pages skip the moment they allow it.||Nothing, Start, Select, the directions: all slower"),
         ("", 16, "LEVEL 1: RAGNAROK'S CANYON. The toad lands; the clock starts when it does.||speedrun.com rule: timing starts on control")]


def build(route, segs):
    ins, ev = [], []
    for b, n, t in INTRO:
        ev.append((len(ins) + 1, t))
        ins += [b] * n
    for name in segs:
        j = json.loads((LOGS_DIR / f"pbeam_{name}.json").read_text())
        ev.append((len(ins) + 1, j.get("note", f"SEARCHED SEGMENT {name}: beam {j.get('width', '?')} wide, random playouts.||"
                                             f"score: camera, damage dealt, kills, health, distance to the portal")))
        ins += j["inputs"]
    (LOGS_DIR / f"{route}.inputs.txt").write_text(f"# frames={len(ins)}\n" + "\n".join(ins) + "\n")
    (LOGS_DIR / f"{route}.events.txt").write_text("\n".join(f"{f}\t{t}" for f, t in ev) + "\n")
    return ins, ev


def replay(route, ins, ev, record=False):
    e = BizHawk(log_name=f"{route}_replay.log", record=route if record else None)
    notes = {}
    for f, t in ev:
        notes.setdefault(f, []).append(t)
    t_start = None
    t_end = None
    prev = None
    prev_lv = None
    cuts = []                                           # frames where the level byte goes 13 -> 254: [Queen's speech, T. Bird]
    for i, b in enumerate(ins):
        for t in notes.get(i + 1, []):
            e.note(t)
        s = e.step(tuple(x for x in b.split("+") if x), 1)
        if t_start is None and s.level == 1 and prev == 5 and s.anim == 4:
            t_start = i + 1
        prev = s.anim
        if t_start is not None and t_end is None and ((s.rtnL == 0x0D and s.rtnH == 0xE5) or s.level not in (1, 0, 255)):
            t_end = i + 1
        if prev_lv == 13 and s.level == 254:
            cuts.append(i + 1)
        prev_lv = s.level
    h = hashlib.sha1(e.ram_all()).hexdigest()
    st = e.state()
    e.close()
    replay.ends = {"queen_speech_cut": cuts[0] if cuts else None, "tbird_cut": cuts[1] if len(cuts) > 1 else None}
    return h, t_start, st, t_end


if __name__ == "__main__":
    route, segs = sys.argv[1], sys.argv[2:]
    ins, ev = build(route, segs)
    h1, t1, st, e1 = replay(route, ins, ev)
    h2, t2, _, _ = replay(route, ins, ev, record=True)
    ok = h1 == h2
    ends = replay.ends
    timed = (e1 or len(ins)) - (t1 or 0)
    print(f"{route}: {len(ins)} frames, timing starts at {t1}, level 1 done at {e1} ({timed} frames = {timed / 60.0988:.2f}s), "
          f"replay {'MATCH' if ok else 'MISMATCH'} sha1 {h1[:8]}, end state {st}")
    qc, tb = ends["queen_speech_cut"], ends["tbird_cut"]
    run = None
    if t1 and tb:
        run = (tb - t1) / 60.0988
        print(f"{route}: RUN TIME {int(run // 60)}:{run % 60:05.2f} = {tb - t1} frames (landing {t1} -> cut to Professor T. Bird {tb}); "
              f"queen_speech_cut {qc} (reference only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 "
              f"for a landing at 2074 -> {'UNDER' if run < 749.25 else 'NOT under'} the record by {abs(749.25 - run):.2f}s")
    else:
        print(f"{route}: NOT FINISHED - the inputs stop before the cut to Professor T. Bird (the second level-byte 13 -> 254); "
              f"queen_speech_cut {qc}. No run time. Append the ending with end_tail.py.")
    tokens.mark(f"route {route}", {"frames": len(ins), "timed": timed, "match": ok, "sha1": h1, "clock_start": t1,
                                   "queen_speech_cut": qc, "tbird_cut": tb, "run_seconds": run})

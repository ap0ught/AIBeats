"""Pellet-fate log for a boss fight (read-only replay, no pokes).

    python tools/s8_pellets.py <state> <seg.json> <row_from> <row_to> <boss type hex> [--full]

Replays the segment's rows from the state; from row_from to row_to prints one line per frame (Bill, boss HP, live
bullets) and, at the end, what became of every pellet: hit the boss, hit something else, flew off, still alive.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game, LOGS_DIR  # noqa: E402

args = sys.argv[1:]
full = "--full" in args
if full:
    args.remove("--full")
state, seg, a, b, typ = args[0], args[1], int(args[2]), int(args[3]), int(args[4], 16)
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / seg).read_text())["rows"]]


def boss(m):
    for s in range(16):
        if m[0x4B8 + s] and m[0x528 + s] == typ:
            return s
    return None


with Game(log_name="s8_pellets.log") as g:
    r = g.load(state)
    r = g.run(rows[:a])
    live = {}          # slot -> dict(born, x0, y0, aim)
    fates = []
    prev = r
    hp_prev = None
    for i in range(a, min(b, len(rows))):
        r = g.step(rows[i])
        m, pm = r.m, prev.m
        bs = boss(m)
        hp = m[0x578 + bs] if bs is not None else None
        dhp = (hp_prev - hp) if (hp is not None and hp_prev is not None) else 0
        other = sum(1 for s in range(16) if s != bs and pm[0x4B8 + s] and m[0x578 + s] < pm[0x578 + s] and pm[0x578 + s] < 0xF0)
        ev = []
        for s in range(10):
            act, pact = m[0x388 + s], pm[0x388 + s]
            rt, prt = m[0x438 + s], pm[0x438 + s]
            if act and (not pact or (prt >= 2 and rt < 2) or s not in live):
                live[s] = {"born": i, "x0": m[0x3C8 + s], "y0": m[0x3B8 + s], "num": m[0x4A8 + s], "hit": None}
                ev.append(f"+{s}")
            if s in live:
                if act and rt >= 2 and live[s]["hit"] is None:
                    live[s]["hit"] = i
                    live[s]["hx"], live[s]["hy"] = pm[0x3C8 + s], pm[0x3B8 + s]
                    ev.append(f"hit{s}")
                if not act:
                    d = live.pop(s)
                    d["gone"] = i
                    d["slot"] = s
                    d["lx"], d["ly"] = pm[0x3C8 + s], pm[0x3B8 + s]
                    fates.append(d)
                    ev.append(f"-{s}")
        bl = " ".join(f"{s}:{m[0x3C8 + s]},{m[0x3B8 + s]}{'*' if m[0x438 + s] >= 2 else ''}" for s in range(10) if m[0x388 + s])
        if full or dhp or ev:
            print(f"{i:5d} {'+'.join(rows[i]):14s} B {r.x:3d},{r.y:3d} j{r.jump:02x} aim{m[0xC2]} scr{r.pos:5d} "
                  f"boss {None if bs is None else (m[0x33E + bs], m[0x324 + bs])} hp {hp} {'-' + str(dhp) if dhp else '  '} "
                  f"{'o' + str(other) if other else '  '} {'LAG ' if r.lagged else ''}| {bl} | {' '.join(ev)}")
        hp_prev = hp
        prev = r
    n = len(fates)
    hits = [d for d in fates if d["hit"] is not None]
    miss = [d for d in fates if d["hit"] is None]
    print(f"pellets finished {n}: hit something {len(hits)} (mean life {sum(d['gone'] - d['born'] for d in hits) / max(1, len(hits)):.1f}, "
          f"flight {sum(d['hit'] - d['born'] for d in hits) / max(1, len(hits)):.1f}); flew off {len(miss)} "
          f"(mean life {sum(d['gone'] - d['born'] for d in miss) / max(1, len(miss)):.1f}); still alive {len(live)}")
    by = {}
    for d in fates:
        k = (d["num"], d["hit"] is not None)
        by[k] = by.get(k, 0) + 1
    print("by pellet number (num, hit): count", sorted(by.items()))

"""DEBUG ONLY (uses RAM pokes, never part of a run): fly up the waterfall and record the background collision map.

    python tools/s3_dumpmap.py [state=dbg/s3_pre]

Every frame the player is pinned at Y=$40 with a rising velocity (so the game's own scroll code runs) and kept
invincible. The collision ring ($0680, 15 rows of 16 px, indexed by (VERTICAL_SCROLL + Y) mod 240) is read every
frame and written into a world map keyed by the world row  q = (Y - A + c) // 16,  A = screen*240 + offset (pixels
climbed), c = (VERTICAL_SCROLL + A) mod 240 (constant). Output: knowledge/s3_map.json
    {"c": c, "rows": {q: "16 chars, one per 16 px column: . empty, = floor, ~ water, # solid"}, "spawns": [...]}
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game, PROJECT  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "dbg/s3_pre"
CH = ".=~#"


def ring_row(m, rr):
    """16 collision codes of ring row rr (0..14)."""
    base = 0x680 + (0x40 if m[0xFF] & 1 else 0) + rr * 4
    out = []
    for col in range(16):
        b = m[base + (col >> 2)]
        out.append((b >> (6 - 2 * (col & 3))) & 3)
    return out


with Game(log_name="s3_dumpmap.log") as g:
    r = g.load(state)
    for _ in range(45):
        r = g.step(())
    A = r.screen * 240 + r.scroll
    c = (r.vscroll + A) % 240
    print("start", r.desc(), "vscroll", r.vscroll, "c", c)
    rows, conflicts, spawns = {}, [], []
    for rr in range(15):
        y = (rr * 16 - r.vscroll) % 240
        rows[(y - A + c) // 16] = "".join(CH[k] for k in ring_row(r.m, rr))
    prev = r
    n = 0
    stuck = 0
    while n < 4000:
        e = g.e
        e.poke(0xAE, 100)
        e.poke(0xA0, 0x11)
        e.poke(0xA4, 0)
        e.poke(0xC6, 0xFE)
        e.poke(0xC4, 0x00)
        e.poke(0x31A, 0x40)
        e.poke(0x334, 0x80)
        r = g.step(())
        n += 1
        A = r.screen * 240 + r.scroll
        assert (r.vscroll + A) % 240 == c or r.autoscroll or r.autodone, (r.desc(), r.vscroll, c)
        m = r.m
        for rr in range(15):
            # screen Y of the top of ring row rr
            y = (rr * 16 - r.vscroll) % 240
            if not (16 <= y <= 192):
                continue
            q = (y - A + c) // 16
            s = "".join(CH[k] for k in ring_row(m, rr))
            if q in rows and rows[q] != s:
                conflicts.append((n, q, rows[q], s))
            rows.setdefault(q, s)
        for s in range(16):
            if m[0x4B8 + s] and m[0x528 + s] != 1 and (not prev.m[0x4B8 + s] or prev.m[0x528 + s] != m[0x528 + s]):
                spawns.append({"A": A, "slot": s, "type": m[0x528 + s], "x": m[0x33E + s], "y": m[0x324 + s],
                               "attr": m[0x5A8 + s], "hp": m[0x578 + s]})
        if r.pos == prev.pos:
            stuck += 1
            if stuck > 200:
                break
        else:
            stuck = 0
        prev = r
    print("end", r.desc(), "frames", n, "rows", len(rows), "conflicts", len(conflicts))
    for cf in conflicts[:40]:
        print("conflict", cf)
    out = {"c": c, "start_A": 0, "rows": {str(q): rows[q] for q in sorted(rows)}, "spawns": spawns}
    p = PROJECT / "knowledge" / "s3_map.json"
    p.write_text(json.dumps(out, indent=0), encoding="utf-8")
    for q in sorted(rows):
        print(f"{q:5d} {rows[q]}")

"""DEBUG ONLY (pokes the new-life invincibility timer): walk stage 8 naively and record the collision map + spawns.

    python tools/s8_dumpmap.py [state=dbg/s8_pre] [out=knowledge/s8_map.json]

Right held, B tapped, a jump whenever X and the scroll did not advance. World cell = (world x >> 4, y >> 4) with
world x = screen*256 + offset + X. Output: {"cols": {wx16: "15 chars top to bottom"}, "spawns": [...]}.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game, PROJECT  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "dbg/s8_pre"
out = sys.argv[2] if len(sys.argv) > 2 else "knowledge/s8_map.json"
CH = ".=~#"
FLY = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0


def code(m, x, y):
    hs = m[0xFD]
    s = hs + x
    nt = (m[0xFF] & 1) ^ (1 if s > 255 else 0)
    s &= 255
    v = (m[0xFC] + y) % 240
    off = ((v >> 2) & 0x3C) | (s >> 6) | (0x40 if nt else 0)
    return (m[0x680 + off] >> (6 - 2 * ((s >> 4) & 3))) & 3


with Game(log_name="s8_dumpmap.log") as g:
    r = g.load(state)
    cols, spawns = {}, []
    prev = r
    stuck = 0
    i = 0
    jumpcool = 0
    while i < 6000:
        g.e.poke(0xAE, 100)
        if FLY and r.pstate == 1:
            g.e.poke(0xA0, 0x31); g.e.poke(0xA4, 0); g.e.poke(0xC6, 0); g.e.poke(0xC4, 0); g.e.poke(0x31A, FLY)
        want = ["Right"]
        if i % 5 < 2:
            want.append("B")
        if stuck >= 3 and not r.airborne and jumpcool <= 0 and not FLY:
            want.append("A")
            jumpcool = 6
        jumpcool -= 1
        r = g.step(want)
        i += 1
        m, pm = r.m, prev.m
        if r.lroutine == 4:
            wx0 = r.pos
            for x in range(8, 256, 16):
                wx = wx0 + x
                col = "".join(CH[code(m, x, y)] for y in range(8, 240, 16))
                key = wx >> 4
                # only trust columns well inside the screen
                if 16 <= x <= 232:
                    if key in cols and cols[key] != col:
                        cols[key + 0.0] = col      # keep a note of changes (guardian wall removal etc.)
                    cols.setdefault(key, col)
        for s in range(16):
            t = m[0x528 + s]
            if m[0x4B8 + s] and (not pm[0x4B8 + s] or pm[0x528 + s] != t) and t != 1:
                spawns.append({"i": i, "pos": r.pos, "slot": s, "type": t, "x": m[0x33E + s], "y": m[0x324 + s],
                               "attr": m[0x5A8 + s], "hp": m[0x578 + s], "state": m[0x598 + s]})
        stuck = stuck + 1 if (r.pos == prev.pos and r.x == prev.x) else 0
        if r.bossdef or r.lroutine != 4:
            print("boss defeated / routine change at", i, r.desc())
            break
        if i % 200 == 0:
            print(i, r.desc(), flush=True)
        prev = r
    print("end", i, r.desc())
    keys = sorted(k for k in cols if isinstance(k, int))
    j = {"cols": {str(k): cols[k] for k in keys}, "changed": {str(int(k)): v for k, v in cols.items() if isinstance(k, float)},
         "spawns": spawns}
    (PROJECT / out).write_text(json.dumps(j, indent=0), encoding="utf-8")
    for y in range(15):
        print("".join(cols[k][y] if k in cols else "?" for k in range(keys[0], keys[-1] + 1)))
    for s in spawns:
        print(s)

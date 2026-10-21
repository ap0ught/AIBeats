"""Final builder: shortest press patterns for a card page, breadth-first over {nothing, A, B} per frame (track C's u17c_head.py
BFS), from the TRUE route state made by a power-on replay.

    python u17f_bfs.py <tag> <segments before the page, comma separated> <next level byte> [extra layers=2] [cap=500]
    python u17f_bfs.py <tag> @<bookmark>:<segment>:<count> <next level byte> ...      (start = the bookmark + the segment's first <count> inputs)
    -> logs/fix/u17f_bfs_<tag>.txt / .json  {"first_depth", "results": [[length, 0, [PC, ts, parity], "bfs", head], ...]}
       (every placement found from the first depth to first depth + extra layers; same layout as logs/fix/u17c_head_*.json)
No memory writes; never Start."""
import hashlib
import sys

from u17f_lib import *
from u16b_phase import core_of

tag, BEFORE, LVL = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3])
EXTRA = int(sys.argv[4]) if len(sys.argv) > 4 else 2
CAP = int(sys.argv[5]) if len(sys.argv) > 5 else 500
log = Log(f"u17f_bfs_{tag}.txt")
e = BizHawk(log_name=f"u17f_bfs_{tag}.log")


def phase():
    c = core_of(e.save("u17f_phase_" + tag))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, c[8] & 1


if sys.argv[2].startswith("@"):                              # @<bookmark>:<segment>:<count> = the bookmark + the segment's first <count> inputs
    bm_, sg_, n_ = sys.argv[2][1:].split(":")
    e.load(bm_)
    for b in seg(sg_)[:int(n_)]:
        e.step(bt(b), 1)
else:
    for b in route_inputs(BEFORE):
        e.step(bt(b), 1)
m0 = bytes(e.ram(0, 0x800))
ph = phase()
log(f"page behind intro + {' '.join(BEFORE)}: {toad(m0)}; alignment PC ${ph[0]:04X} ts {ph[1]} parity {ph[2]}")
layer = [(e.msave(), [], 0)]
found, first_d = [], None
for depth in range(1, 400):
    nxt, seen = [], set()
    for sid, path, st in layer:
        for b in ("", "A", "B"):
            e.mload(sid)
            e.step(bt(b), 1)
            m = bytes(e.ram(0, 0x800))
            st2 = placed_stage(st, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)
            if st2 == 3:
                p = phase()
                found.append((depth, path + [b], p))
                continue
            k = (hashlib.sha1(m).digest(), st2)
            if k in seen:
                continue
            seen.add(k)
            nxt.append((e.msave(), path + [b], st2))
    for sid, _, _ in layer:
        e.mfree(sid)
    if found and first_d is None:
        first_d = depth
    if len(nxt) > CAP:
        nxt.sort(key=lambda n: -n[2])
        for n in nxt[CAP:]:
            e.mfree(n[0])
        nxt = nxt[:CAP]
    layer = nxt
    if depth % 20 == 0:
        log(f"  BFS depth {depth}: {len(layer)} states, stages {sorted(set(n[2] for n in layer))}, placements so far {len(found)}")
    if first_d is not None and depth >= first_d + EXTRA:
        break
    if not layer:
        break
for sid, _, _ in layer:
    e.mfree(sid)
log(f"BFS: first placement at depth {first_d}; placements by depth: {sorted((d, sum(1 for x in found if x[0] == d)) for d in set(x[0] for x in found))}")
for d, path, p in found:
    log(f"  {d}: presses {[(i, b) for i, b in enumerate(path) if b]}; alignment PC ${p[0]:04X} ts {p[1]} parity {p[2]}")
write_json(FIX / f"u17f_bfs_{tag}.json", {"before": BEFORE, "first_depth": first_d, "results": [[d, 0, list(p), "bfs", path] for d, path, p in found]})
e.close()

"""Track K: run several hand-written input scripts from the warp-room root; compact traces.
    python u16k_runs.py <from> <to> "<spec>" "<spec>" ...     spec = "<n>:<buttons>;..."   trace r:x/rel/z/anim/spd/vy"""
import sys
from u16k_lib import *

f0, f1 = int(sys.argv[1]), int(sys.argv[2])
e, lines = open_room("u16k_runs.log")
room = e.msave()
for spec in sys.argv[3:]:
    ins = []
    for part in spec.split(";"):
        n, b = part.split(":")
        ins += [b] * int(n)
    e.mload(room)
    tr, prev_b = [], None
    for r, b in enumerate(ins):
        e.step(bt(b), 1)
        t = rd(e)
        if f0 <= r + 1 <= f1:
            m = t["m"]
            vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
            rel = (t["H"] - t["head"][1]) if t["head"] else None
            tr.append(f"{r + 1}{('[' + b + ']') if b != prev_b else ''}:{t['x']}/{rel}/z{t['z']}/a{t['an']}/s{t['spd']}/v{vy:.1f}" + ("" if t["hp"] == 47 else f"/HP{t['hp']}"))
            prev_b = b
        if t["hp"] < 47:
            break
    print(spec, "\n   ", " ".join(tr), flush=True)
e.close()

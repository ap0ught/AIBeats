"""Track K2: snake timeline of room 1 for hand-written toad scripts (to learn the heads' undisturbed schedule).
    python u17k_free.py <tag> <n0 = K6 prefix length> "<n>:<buttons>;..." [frames=1500] [toad trace every N]
-> logs/fix/u17k_free_<tag>.txt: per head: appear / direction changes / pauses / vanish"""
import sys
from u17k_lib import *

tag, n0, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]
total = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
every = int(sys.argv[5]) if len(sys.argv) > 5 else 0
ins = seg("K6")[:n0] + parse(spec)
ins += [""] * max(0, total - len(ins))
e = BizHawk(log_name=f"u17k_free_{tag}.log")
e.load("B4_end0")
out, prev, pd, run = [], None, None, None
for n, b in enumerate(ins, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    t = info(m)
    h = t["heads"][0] if t["heads"] else None
    td = f"toad {t['x']},{t['H']} z{t['z']} a{t['an']} s{t['spd']} v{t['vy']:.1f}"
    paused = bool(h and prev and h == prev)
    if run and not paused:
        out.append(f"{run[0]}..{n - 1}: PAUSE x{n - run[0]} head {run[1]} | {run[2]}")
        run = None
    if paused and not run:
        run = (n, h[1:], td)
    if h and not prev:
        out.append(f"{n}: head appears {h} | {td}")
        pd = None
    if prev and not h:
        out.append(f"{n}: head gone (last {prev}) | {td}")
    if h and prev and not paused:
        d = (h[1] - prev[1], h[2] - prev[2])
        if d != pd:
            out.append(f"{n}: head {pd} -> {d} at {prev[1:]} | {td}")
            pd = d
    if every and n % every == 0 and n > n0:
        out.append(f"   {n} [{b}] {td} head {h[1:] if h else None}")
    prev = h
    if t["hp"] < 47 or t["lvl"] != 8:
        out.append(f"{n}: STOP hp {t['hp']} level {t['lvl']} toad {t['x']},{t['H']}")
        break
open(FIX / f"u17k_free_{tag}.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
e.close()

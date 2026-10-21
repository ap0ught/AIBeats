"""Board a circling platform, ride it, bounce (A held) and steer in the air until the toad grabs a pole (anim 94-96).
    python polegrab.py <bookmark> <plat_h> <pole_x list> <out.json> [idle 0|1] [maxride]
Restarts the emulator for every boarding wait (EmuHawk dies after long msave-heavy runs)."""
import json, sys
from toads.emulator import BizHawk, PROJECT
import resync as R
bm, ph = sys.argv[1], int(sys.argv[2]); poles = [int(v) for v in sys.argv[3].split(",")]; out = sys.argv[4]
idle = len(sys.argv) > 5 and sys.argv[5] == "1"; maxride = int(sys.argv[6]) if len(sys.argv) > 6 else 260
N, L, Rt, A = (), ("Left",), ("Right",), ("A",)
def on_plat(r):
    q = R.st(r)
    p = [(r[0x3FD+s]+256*r[0x3EE+s], r[0x439+s]) for s in range(2, 15) if r[0x3C1+s] == 0x36 and abs(r[0x439+s] - ph) <= 40]
    return q[2] == 0 and any(min(abs(px-q[0]), 512-abs(px-q[0])) <= 18 and 0 <= (q[1]-py) % 256 <= 12 for px, py in p)
def fresh():
    e = BizHawk(log_name=f"polegrab_{bm}.log"); e.load(bm)
    if idle: e.step((), 2)
    return e
# 1) the earliest boarding
e = fresh(); root = e.msave(); board = None
for w in range(0, 300):
    e.mload(root)
    for i in range(w): e.step(N, 1)
    ws = e.msave()
    for jb, drift in ((A, L), (A, Rt), (A, N), (("Left", "A"), L), (("Right", "A"), Rt)):
        for k in (2, 6, 12, 18):
            e.mload(ws); seq = [N] * w; air = False
            for b in [jb] * k + [drift] * 60:
                e.step(b, 1); seq.append(b); r = e.ram_all(); q = R.st(r)
                if q[4] < 47: break
                if q[2] > 0: air = True
                if air and q[2] == 0:
                    if on_plat(r): board = seq[:]
                    break
            if board: break
        if board: break
    e.mfree(ws)
    if board: break
e.close()
if not board: print("no boarding"); sys.exit()
print("boarded after", len(board), flush=True)
best = None
for ride in range(0, maxride, 2):
    e = fresh()
    for b in board: e.step(b, 1)
    ok = True
    for i in range(ride):
        e.step(N, 1)
        if e.ram_all()[0x475] != 0: ok = False; break
    if not ok: e.close(); continue
    rs = e.msave()
    for s0 in (0, 3, 6):
        for steer_at in range(0, 60, 4):
            for d in (L, Rt, N):
                e.mload(rs); seq = [N] * s0 + [A] * steer_at + [d + A] * 80
                for i, b in enumerate(seq):
                    e.step(b, 1); q = R.st(e.ram_all())
                    if q[4] < 47: break
                    if q[3] in (94, 95, 96):
                        if q[0] in poles:
                            tot = len(board) + ride + i + 1
                            if best is None or tot < best[0]:
                                best = (tot, q[:4])
                                full = board + [N] * ride + seq[:i + 1]
                                (PROJECT / "knowledge" / out).write_text(json.dumps(["+".join(x) for x in full]))
                                print("GRAB", q[:4], "total", tot, "ride", ride, flush=True)
                        break
    e.close()
    if best and ride > best[0] - len(board): break
print("best", best)

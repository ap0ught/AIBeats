"""Board a moving platform, ride it, bounce-launch (A held, optional sprint double taps), land in a target box.
    python platjump.py <bookmark> <plat_id hex> <plat_h> <dir L|R> <tx0,tx1,th0,th1> <out.json> [idle 0|1] [maxw]
The bookmark is the previous section's solved state; with idle=1 the 2 idle frames of a normal section come first.
Output: inputs from the bookmark (+idle) to the landing in the box, fewest frames first; also prints the landing state."""
import json, sys
from toads.emulator import BizHawk, PROJECT
import resync as R
bm, pid, ph, dirc = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3]), sys.argv[4]
tx0, tx1, th0, th1 = (int(v) for v in sys.argv[5].split(","))
out = sys.argv[6]; idle = len(sys.argv) > 7 and sys.argv[7] == "1"; maxw = int(sys.argv[8]) if len(sys.argv) > 8 else 300
D = ("Left",) if dirc == "L" else ("Right",); O = ("Right",) if dirc == "L" else ("Left",)
N, A = (), ("A",)
DA = D + A
e = BizHawk(log_name=f"platjump_{bm}.log"); e.load(bm)
if idle: e.step((), 2)
root = e.msave(); lives0 = R.st(e.ram_all())[5]
def plat(r): return [(r[0x3FD+s]+256*r[0x3EE+s], r[0x439+s]) for s in range(2, 15) if r[0x3C1+s] == pid and abs(r[0x439+s] - ph) <= 40]
def on_plat(r):
    q = R.st(r)
    return q[2] == 0 and any(min(abs(px - q[0]), 512 - abs(px - q[0])) <= 18 and 0 <= (q[1] - py) % 256 <= 12 for px, py in plat(r))
def in_box(q):
    return q[2] == 0 and (tx0 <= q[0] <= tx1 if tx0 <= tx1 else (q[0] >= tx0 or q[0] <= tx1)) and th0 <= q[1] <= th1
# 1) boardings: wait w, jump (A k frames with a direction), drift, land on the platform
boards = []
for w in range(0, maxw):
    e.mload(root)
    for i in range(w): e.step(N, 1)
    ws = e.msave()
    for jb, drift in ((A, D), (A, O), (A, N), (DA, D), (O + A, O)):
        for k in (2, 6, 12, 18):
            e.mload(ws); seq = [N] * w; air = False
            for b in [jb] * k + [drift] * 60:
                e.step(b, 1); seq.append(b); r = e.ram_all(); q = R.st(r)
                if q[4] < 47: break
                if q[2] > 0: air = True
                if air and q[2] == 0:
                    if on_plat(r): boards.append((len(seq), seq[:]))
                    break
    if len(boards) >= 6: break
e.mfree(root) if False else None
boards.sort(key=lambda t: t[0])
seen = set(); bl = []
for n, seq in boards:
    if n not in seen: seen.add(n); bl.append((n, seq))
print("boardings (frames):", [n for n, _ in bl[:6]], flush=True)
best = None
for n, bseq in bl[:4]:
    e.mload(root)
    for b in bseq: e.step(b, 1)
    bs = e.msave()
    for ride in range(0, 400, 2):
        if best and n + ride > best[0]: break
        e.mload(bs)
        dead = False
        for i in range(ride):
            e.step(N, 1)
            if not on_plat(e.ram_all()): dead = True; break
        if dead: continue
        rs = e.msave()
        for s0 in (0, 2, 4, 6, 8):
            for m in (0, 1, 2, 3, 5, 7, 9, 11, 13):
                for hold in (DA, D):
                    e.mload(rs); seq = [A] * s0 + [DA, A] * m + [hold] * 120; air = False
                    for i, b in enumerate(seq):
                        e.step(b, 1); r = e.ram_all(); q = R.st(r)
                        if q[4] < 47 or q[5] < lives0: break
                        if q[2] > 0: air = True
                        if air and q[2] == 0:
                            if in_box(q):
                                tot = n + ride + i + 1
                                if best is None or tot < best[0]:
                                    full = bseq + [N] * ride + seq[:i + 1]
                                    best = (tot, q[:4])
                                    (PROJECT / "knowledge" / out).write_text(json.dumps(["+".join(b) for b in full]))
                                    print(f"LANDED {q[:4]} total {tot} (board {n}, ride {ride}, s0 {s0}, m {m}, hold {hold})", flush=True)
                            break
        e.mfree(rs)
print("best", best)
e.close()

"""Brute force short legal input sequences from a TAS frame; report the best by a target.
python a12_brute.py <state> <tas_frame> <seq_len> <tail_len> <targetX> <targetY>
Sequences: segments (dir in L/R/-, A held or not, length 2..4) covering seq_len frames, then Right for tail_len.
Target: first frame with absolute X >= targetX and y <= targetY and on the ground (rflags bit 2 clear)."""
import sys, itertools, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng import legal
from ng.emulator import BizHawk
from ng.mode import TICKS

LENS = (2, 3, 4)
DIRS = ("L", "R", "-")
PREFIX = []


def segs(n):
    if n == 0:
        yield []
        return
    for L in LENS:
        if L > n:
            break
        for d in DIRS:
            for a in (0, 1):
                for rest in segs(n - L):
                    yield [(d, a, L)] + rest

if __name__ == "__main__":
    st, f0, n, tail, tx, ty = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    if len(sys.argv) > 7:
        PREFIX[:] = [tuple(x for x in r.split("+") if x) for r in sys.argv[7].split(",")]
    if len(sys.argv) > 8:
        LENS = tuple(int(x) for x in sys.argv[8].split(","))
    ref = legal.TasRef()
    M = {"L": ("Left",), "R": ("Right",), "-": ()}
    with BizHawk(log_name="a12_brute.log") as e:
        s0 = e.load(st); e.tick(TICKS)
        legal.play(e, ref.rows[s0["frame"]:f0])
        sid = e.msave()
        best = []
        seen = set()
        t = time.time(); cnt = 0
        for sg in segs(n):
            rows = list(PREFIX)
            for d, a, L in sg:
                rows += [tuple(M[d]) + (("A",) if a else ())] * L
            key = tuple(rows)
            if key in seen or not legal.is_legal(rows + [("Right",)] * tail):
                continue
            seen.add(key)
            e.mload(sid)
            tr = legal.play(e, rows + [("Right",)] * tail, chunk=n + tail)
            cnt += 1
            hit = next((i for i, s in enumerate(tr) if legal.pos_of(s)[2] >= tx and s["y"] <= ty and not (s["rflags"] & 4)), None)
            score = hit if hit is not None else 10 ** 6 - max(legal.pos_of(s)[2] for s in tr)
            best.append((score, "|".join("+".join(r) for r in rows)))
        best.sort()
        print(cnt, "candidates", round(time.time() - t), "s")
        for b in best[:15]:
            print(b)

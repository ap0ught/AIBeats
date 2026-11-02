"""Acts 3-4: 3-3 Basaquer, hand-structured legal plan + parameter sweeps. Owned by the Acts 3-4 agent.

Facts (TAS replay, measured): the boss path is fixed (does not depend on Ryu): it jumps right->left, lands at
x=43 y=208 on frame 13795, sits until 13817, jumps back right (x 208 at ~13872). Fire Wheel (5 ninpo, 20 ninpo
= 4 throws) hits up to 3 times per throw; a throw needs Up+B with NO left/right held (Up+Left+B = sword slash).
Sword: one legal B press per 5 frames.

    python ng/stages/a34_b33.py [--start state] [--prefix rows] [--out name]
"""
from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402

R = lambda *a: tuple(a)  # noqa: E731


def plan_a(f0, p):
    """rows for frames f0+1 .. f0+n from parameters p (dict). f0 = 13757 (exact TAS sync point)."""
    rows = {}

    def put(f, r):
        rows[f] = r
    put(13758, R("Right"))
    put(13759, ())
    put(13760, ())
    put(13761, R("Up", "B"))
    put(13762, R("Up", "B"))
    for f in range(13763, 13763 + p.get("left1", 5)):
        put(f, R("Left"))
    t2 = p.get("t2", 13777)
    put(t2, R("Up", "B"))
    put(t2 + 1, R("Up", "B"))
    turn = p.get("turn", 13786)
    for f in range(t2 + 2, turn):
        put(f, R("Right") if f >= p.get("r2", 13779) else ())
    t3 = turn + 2 + p.get("t3d", 0)
    for f in range(turn, t3):
        put(f, R("Left"))
    put(t3, R("Up", "B"))
    put(t3 + 1, R("Up", "B"))
    end = f0 + p.get("n", 110)
    # sword phase: from frame j: move (dir) for w frames, jump (dir+A) on frame j+w, Down+B every 5 frames
    j = p.get("j", 13804)
    w = p.get("w", 0)
    d = p.get("dir", "Left")
    for f in range(j, j + w):
        put(f, (d,) if d else ())
    ja = j + w
    if p.get("jump", True):
        put(ja, (d, "A") if d else ("A",))
        put(ja + 1, (d, "A") if d else ("A",))
        sl = ("Down", "B")
    else:
        sl = ("B",)
    t4 = p.get("t4", 0)
    g = ja + p.get("s0", 1)
    while g < end:
        if t4 and t4 - 1 <= g < t4 + 4:
            g = t4 + 4
            continue
        put(g, sl)
        put(g + 1, sl)
        for h in (g + 2, g + 3, g + 4):
            if h not in rows:
                put(h, (d,) if (d and p.get("hold_dir", False)) else ())
        g += 5
    if t4:
        put(t4, R("Up", "B"))
        put(t4 + 1, R("Up", "B"))
    return [rows.get(f, ()) for f in range(f0 + 1, end + 1)]


def evaluate(e, sid, rows, hist, stage=7):
    L = K.Legal(hist)
    leg = K.greedy_legal(rows, L)
    e.mload(sid)
    e.trace(True)
    e.run(leg)
    tr = e.last_trace
    e.trace(False)
    hits = []
    prev = None
    for s in tr:
        b = s["boss_real"]
        if prev is not None and b < prev:
            hits.append((s["frame"], b))
        prev = b
        if (s["dead"] & 0x80) or s["hp"] == 0:
            return None, hits, leg
        if b == 0:
            return s["frame"], hits, leg
    return None, hits, leg


def main():
    args = sys.argv[1:]
    start = "ref4751/07_3-3_control"
    prefix = "follow_3-3"
    out = "b33_plan"
    e = K.open_emu("a34_b33.log")
    try:
        e.load(start)
        pre = K.load_rows(prefix)
        e.run(pre)
        f0 = e.state().frame
        sid = e.msave()
        hist = pre
        best = None
        t = time.time()
        # stage 1: throws 1-3: r2 (when the right drift after throw 2 starts), turn frame; score by 13800
        res = []
        for left1, r2, turn, t3d in itertools.product((3, 5), range(13779, 13787), (13785, 13786, 13787), (0, 1)):
            p = dict(left1=left1, r2=r2, turn=turn, t3d=t3d, n=43, j=13900)
            kill, hits, leg = evaluate(e, sid, plan_a(f0, p), hist)
            left = hits[-1][1] if hits else 16
            res.append((left, -sum(13820 - f for f, _ in hits), p, hits))
        res.sort(key=lambda r: (r[0], r[1]))
        for r in res[:5]:
            print("A", r[0], r[2], r[3], flush=True)
        print(f"{time.time() - t:.0f}s", flush=True)
        # stage 2: sword phase + throw 4
        res2 = []
        for _, _, p, _ in res[:2]:
            for j, w, dr, jump, s0, t4 in itertools.product(range(13800, 13812, 2), (0, 2, 4), ("Left", ""), (True, False),
                                                            (1, 2), (0, 13818, 13821, 13824)):
                q = dict(p, j=j, w=w, dir=dr, jump=jump, s0=s0, t4=t4, n=110)
                kill, hits, leg = evaluate(e, sid, plan_a(f0, q), hist)
                res2.append((kill or 10 ** 6, hits[-1][1] if hits else 16, -sum(13900 - f for f, _ in hits), q, hits, leg))
        res2.sort(key=lambda r: (r[0], r[1], r[2]))
        for r in res2[:6]:
            print("B kill", r[0], "left", r[1], r[3], r[4], flush=True)
        print(f"{time.time() - t:.0f}s", flush=True)
        kill, left, _, q, hits, leg = res2[0]
        K.save_rows(out, pre + leg, f"3-3 plan kill at {kill} left {left} params {q}")
        print("saved", out, "kill", kill, "left", left)
    finally:
        e.close()


if __name__ == "__main__":
    main()

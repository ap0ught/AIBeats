"""4-2 exit wall sweep (round 3): from cut points of a 4-2 prefix, try run/jump timings toward the exit wall and a
closed-loop climb (C7/C8/C9 cycles while touching the wall, else hold Right; optional waits for a bird damage boost).
Records the first frame with Ryu at the stage-end trigger (wpos >= 3030, y <= 84).

    python work/a34r3/s42x.py <prefix rows name> <cut0> <cut1> <cutstep> <out name>
"""
import json
import sys
import time

sys.path.insert(0, "ng/stages")
sys.path.insert(0, ".")
import a34_core as K  # noqa: E402

START = "ref4751/09_4-2_control"
F0 = 16682


def trig(s):
    return s.room == 16 and K.wpos(s) >= 3030 and s.y <= 84


def main():
    pre, c0, c1, cs, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    rows = K.load_rows(pre)
    e = K.open_emu(f"a34r3_s42x_{out}.log")
    best = None
    res = []
    try:
        e.load(START)
        cuts = {}
        s = e.run(rows[:c0 - F0])
        for c in range(c0, c1 + 1, cs):
            if c > F0 + len(rows):
                break
            s = e.run(rows[s.frame - F0:c - F0]) if c > s.frame else s
            cuts[c] = (e.msave(), s)
            en = [(j, e.byte(0x400 + j), e.byte(0x460 + j), e.byte(0x480 + j)) for j in range(8) if e.byte(0x400 + j)]
            print("cut", c, "x", s.x, "y", s.y, "wpos", K.wpos(s), "hp", s.hp, "rfl", s.rflags, "en", en, flush=True)
        t0 = time.time()
        for c, (sid, s0) in cuts.items():
            if s0.rflags & 4:
                dlist = (0,)
            else:
                dlist = (0, 2, 4, 6, 8, 10, 12, 14, 16, 20)
            for d in dlist:
                for a in (2, 4, 8, 12, 16, 24):
                    for cyc in (7, 8, 9):
                        for hold_first in (0, 6, 12):
                            e.mload(sid)
                            L = K.Legal(rows[:c - F0])
                            plan = [("Right",)] * d + ([("Right", "A")] * a if not (s0.rflags & 4) else [])
                            mine = []
                            for r in plan:
                                r2 = K.greedy_legal([r], L)[0]
                                s = e.step(r2, 1)
                                mine.append(r2)
                            # closed loop: hold Right until touching the wall, optionally hold for hold_first more
                            # frames (bird boost chance), then climb cycles
                            k = 0
                            phase = 0
                            touched = -1
                            hit = None
                            while k < 150:
                                if trig(s):
                                    hit = s.frame
                                    break
                                if s.y >= 0xF8 or s.hp == 0:
                                    break
                                wall = bool(s.coll & 0x2A)
                                if touched < 0 and wall:
                                    touched = k
                                if touched < 0 or k - touched < hold_first:
                                    want = ("Right",)
                                else:
                                    i = phase % cyc
                                    want = ("Left", "A") if i < 2 else ("Right",)
                                    phase += 1
                                r2 = K.greedy_legal([want], L)[0]
                                s = e.step(r2, 1)
                                mine.append(r2)
                                k += 1
                            if hit is not None:
                                res.append((hit, c, d, a, cyc, hold_first, s.hp))
                                if best is None or hit < best[0]:
                                    best = (hit, c, d, a, cyc, hold_first, rows[:c - F0] + mine)
                                    print(f"  best {hit} cut {c} d {d} a {a} cyc {cyc} hold {hold_first} hp {s.hp} "
                                          f"{time.time() - t0:.0f}s", flush=True)
            print("done cut", c, "best", best[:6] if best else None, flush=True)
        if best:
            K.save_rows(out, best[6], f"{START} + {pre} cut {best[1]} + s42x d{best[2]} a{best[3]} cyc{best[4]} "
                                      f"hold{best[5]}: trigger at {best[0]}")
            e.load(START)
            s = e.run(best[6])
            print("RESULT", out, "trigger", best[0], "replay end", s.frame, s.x, s.y, K.wpos(s), "trig", trig(s),
                  flush=True)
        res.sort()
        print(json.dumps(res[:30]))
    finally:
        e.close()


if __name__ == "__main__":
    main()

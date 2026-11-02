"""Graft the found rows of an A* run made from a TAS state (geometry learning) onto our own legal prefix.

    python work/a34r3/graft.py <start state> <base rows> <donor rows> <donor prefix rows> <out> [<goal room> <goal wpos> <goal y> <tol>]

Donor tail = donor rows after len(donor prefix rows). It is re-legalised against the base rows (greedy_legal) and
run after the base; prints where Ryu ends and whether/when the goal (standing within tol, or room change if wpos<0)
was met; saves logs/a34/<out>.inputs.txt = base + legal tail cut at the goal frame.
"""
import sys

sys.path.insert(0, "ng/stages")
sys.path.insert(0, ".")
import a34_core as K  # noqa: E402


def main():
    st, base, donor, dpre, out = sys.argv[1:6]
    goal = [int(v) for v in sys.argv[6:10]] if len(sys.argv) >= 10 else None
    B = K.load_rows(base)
    D = K.load_rows(donor)
    n = len(K.load_rows(dpre))
    tail = D[n:]
    L = K.Legal(B)
    leg = K.greedy_legal(tail, L)
    ndiff = sum(1 for a, b in zip(tail, leg) if tuple(a) != tuple(b))
    e = K.open_emu(f"a34r3_graft_{out}.log")
    try:
        e.load(st)
        s = e.run(B)
        print("base end", s.frame, "room", s.room, "wpos", K.wpos(s), "y", s.y, "hp", s.hp, "ninpo", s.ninpo,
              "item", hex(s.item), "rflags", s.rflags, flush=True)
        e.trace(True)
        s = e.run(leg)
        tr = e.last_trace
        e.trace(False)
        hit = None
        if goal:
            gr, gx, gy, tol = goal
            for i, x in enumerate(tr):
                if gx < 0:
                    ok = x["room"] == gr
                else:
                    ok = x["room"] == gr and abs(K.wpos(x) - gx) + abs(x["y"] - gy) <= tol and not (x["rflags"] & 4)
                if ok:
                    hit = i
                    break
        print("tail", len(tail), "changed rows", ndiff, "end", s.frame, "room", s.room, "wpos", K.wpos(s), "y", s.y,
              "hp", s.hp, "goal at", (B and len(B)) and (tr[hit]["frame"] if hit is not None else None), flush=True)
        if hit is not None:
            rows = B + leg[:hit + 1]
            Lc = K.Legal(rows)
            need = tuple(b for b in K.BTNS if Lc.held[b] and Lc.run[b] < Lc.HOLD)
            if need:
                rows.append(need)
            K.save_rows(out, rows, f"{st} + {base} + graft of {donor} tail: goal at {tr[hit]['frame']}")
            print("RESULT", out, "goal at", tr[hit]["frame"], flush=True)
        else:
            print("RESULT", out, "goal NOT met", flush=True)
    finally:
        e.close()


if __name__ == "__main__":
    main()

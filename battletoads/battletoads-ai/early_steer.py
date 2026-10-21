"""EARLY track (2026-10-09): can a changed upstream be STEERED back onto the old dice at the next level boundary?

Real test case from the project's history: Rat Race exists twice behind the same Terra Tubes end (bookmark L9c_end0):
L10c (2,063 inputs, our old line) and L10t (1,945, the TAS's inputs) - same end state, 118 frames apart.  L11r was fitted
behind L10t.  Question: behind the OTHER Rat Race (L10c), is there a briefing-page skip delay K for which L11r's inputs
replay verbatim (same dice, same track)?  If yes, an upstream saving costs K frames at the boundary and nothing else.

    python early_steer.py <N frames of the next segment to compare> K1 K2 ...
    -> logs/fix/early_steer.tsv
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

F = {"level": 0x10, "timer": 0x0B, "r25": 0x25, "r26": 0x26, "r27": 0x27, "r28": 0x28, "x": 0x3FD, "xh": 0x3EE,
     "height": 0x439, "y": 0x41B, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
row = lambda s: (s.level, s.timer, s.r25, s.r26, s.r27, s.r28, s.x | s.xh << 8, s.height, s.y, s.anim, s.hp, s.lives)
ROOT, REFSEG, VARSEG, NEXT, LVL = "L9c_end0", "L10t", "L10c", "L11r", 10
if len(sys.argv) > 1 and "=" in sys.argv[1]:                       # ROOT=..,REF=..,VAR=..,NEXT=..,LVL=..
    kv = dict(p.split("=") for p in sys.argv.pop(1).split(","))
    ROOT, REFSEG, VARSEG, NEXT, LVL = kv["ROOT"], kv["REF"], kv["VAR"], kv["NEXT"], int(kv["LVL"])


class Placer:
    def __init__(self, lvl):
        self.lvl, self.stage, self.left = lvl, 0, None

    def feed(self, r, n):
        if self.left is None and r[0] in (254, 255):
            self.left = n                                     # index of the first frame the level byte has left the level
        if self.stage == 0 and r[0] == self.lvl:
            self.stage = 1
        if self.stage == 1 and r[10] == 0 and r[6] == 0:
            self.stage = 2
        if self.stage == 2 and r[10] > 0 and r[6] > 0:
            self.stage = 3
            return True
        return False


def main():
    n_cmp = int(sys.argv[1])
    ks = sys.argv[2:]
    seg = lambda n: json.loads((LOGS_DIR / f"pbeam_{n}.json").read_text())["inputs"]
    ref_in, var_in, nxt = seg(REFSEG), seg(VARSEG), seg(NEXT)
    e = BizHawk(log_name="early_steer.log", fields=F)

    # reference lineage
    e.load(ROOT)
    pl, rows = Placer(LVL), []
    p_ref = None
    for i, b in enumerate(ref_in):
        rows.append(row(e.step(bt(b), 1)))
        if pl.feed(rows[-1], i) and p_ref is None:
            p_ref = i
    c = len(ref_in) - 1 - p_ref
    left_ref = pl.left
    for b in nxt[:n_cmp]:
        rows.append(row(e.step(bt(b), 1)))
    ref = rows[p_ref:]
    print("reference dice signature (+12/+40):", "".join(f"{x:02x}" for x in ref[12][2:6]) + "/" + "".join(f"{x:02x}" for x in ref[40][2:6]), flush=True)
    print(f"reference {REFSEG}: level left at input {left_ref}, toad placed at input {p_ref} ({p_ref - left_ref} after), {c} inputs after it; "
          f"then {n_cmp} of {NEXT}", flush=True)
    out = [f"# root {ROOT} ref {REFSEG} var {VARSEG} next {NEXT}; ref: left {left_ref}, placed {p_ref}, tail {c}",
           "variant\tplaced_after_level_end\tdice_equal_frames\ttrack_equal_frames\tverbatim"]

    # where the variant segment's own level end is (for negative sJ)
    e.load(ROOT)
    pl = Placer(LVL)
    left_var = None
    for i, b in enumerate(var_in):
        pl.feed(row(e.step(bt(b), 1)), i)
        if pl.left is not None:
            left_var = pl.left
            break
    print(f"variant {VARSEG}: level left at input {left_var}", flush=True)
    for v in ks:
        e.load(ROOT)
        pl, rows, p = Placer(LVL), [], None
        if v == "asis":                                       # the variant segment's own mash, untouched
            seq = list(var_in) + [""] * 40
            for i, b in enumerate(seq):
                rows.append(row(e.step(bt(b), 1)))
                if pl.feed(rows[-1], i):
                    p = i
                    break
        else:
            # "K" = K idle frames before the mash;  "sJ" / "sJ+K" = Select added on input J of the variant segment (J < 0: from its level end)
            sel = None
            if v[0] == "s":
                a, _, kk = v[1:].partition("+")
                sel, k = int(a), int(kk or 0)
                if sel < 0:
                    sel += left_var
            else:
                k = int(v)
            i = 0
            while pl.left is None:                            # the variant segment up to its level end
                b = bt(var_in[i])
                if i == sel:
                    b = tuple(sorted(set(b) | {"Select"}))
                rows.append(row(e.step(b, 1)))
                pl.feed(rows[-1], i)
                i += 1
            j = 0
            while p is None and j < 600:                      # k idle frames, then a fresh A every other frame
                b = () if j < k else (("A",) if (j - k) % 2 == 0 else ())
                rows.append(row(e.step(b, 1)))
                if pl.feed(rows[-1], i):
                    p = i
                i += 1
                j += 1
        if p is None:
            line = f"{v}\tNOT PLACED"
        else:
            for b in ref_in[p_ref + 1:] + nxt[:n_cmp]:
                rows.append(row(e.step(bt(b), 1)))
            var = rows[p:]
            n = min(len(ref), len(var))
            dice = next((q for q in range(n) if ref[q][1:6] != var[q][1:6]), n)
            track = next((q for q in range(n) if ref[q][6:] != var[q][6:]), n)
            line = f"{v}\t{p - pl.left}\t{dice}\t{track}\t{'YES' if dice == n and track == n else 'no'} (of {n})"
        print(line, flush=True)
        out.append(line)
    open(LOGS_DIR / "fix" / "early_steer.tsv", "a", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()

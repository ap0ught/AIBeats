"""Final builder: the last stretch of the Queen segment (stand before the speech cut, speech, reload, tower, T. Bird cut) with ONE
extra press of any legal button on a frame before the speech cut, the speech answered on the first frame it takes a press.

    python u17f_end.py <queen segment> <entry bookmark> <tag> <T0> <T1> [buttons]
        T0..T1 = indices of the segment that get the extra press (after the whirl timer has parked: the dice no longer matter
                 for the final wait, only for the speech / reload lengths)
    For every variant: frame of the first cut (must stay where it is), frames from the cut to the tower (speech), frame of the
    T. Bird cut, and health / lives / score there.  -> logs/fix/u17f_end_<tag>.txt / .json (the shortest are listed)
No memory writes."""
import sys

from u17f_lib import *

SEG, BM, tag, T0, T1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
BTNS = (sys.argv[6] if len(sys.argv) > 6 else "Select,Up,Down,Left,Right,A,B").split(",")
sj, sg = segj(SEG), seg(SEG)
CUT1, TB = sj["cut1_at"], sj["tbird_at"]                     # inputs done when the level byte turns 254 the first / second time
log = Log(f"u17f_end_{tag}.txt")
e = BizHawk(log_name=f"u17f_end_{tag}.log", fields={"level": 0x10})
e.load(BM)
for b in sg[:T0]:
    e.step(bt(b), 1)
base = e.msave()


def lvl():
    return e.ram(0x10, 1)[0]


def finish(i0, press):
    """from index i0 (emulator on the rolling base): the segment's inputs to the first cut with the extra press, then the speech
    answered greedily, then nothing to the T. Bird cut.  -> (first cut, tower frame, T. Bird cut, inputs from i0, end RAM) or None"""
    ins = []
    i = i0
    prev = 13
    cut1 = None
    while i < CUT1 + 3:
        b = sg[i] if i < CUT1 else ""
        if press and press[0] == i:
            b = (b + "+" + press[1]).lstrip("+")
        s = e.step(bt(b), 1)
        ins.append(b)
        i += 1
        if prev == 13 and s.level == 254:
            cut1 = i
            break
        prev = s.level
    if cut1 is None:
        return None
    tower = None
    for _ in range(40):                                      # the speech: nothing, unless A (or else B) brings the tower back at once
        s0 = e.msave()
        s = e.step((), 1)
        idle = s.level
        choice = ""
        for b in ("A", "B"):
            e.mload(s0)
            s = e.step((b,), 1)
            if s.level != idle:
                choice = b
                break
        if not choice:
            e.mload(s0)
            s = e.step((), 1)
        e.mfree(s0)
        ins.append(choice)
        i += 1
        if s.level == 13:
            tower = i
            break
    if tower is None:
        return None
    prev = 13
    for _ in range(520):
        s = e.step((), 1)
        ins.append("")
        i += 1
        if prev == 13 and s.level == 254:
            return cut1, tower, i, ins, bytes(e.ram(0, 0x800))
        prev = s.level
    return None


e.mload(base)
r0 = finish(T0, None)
log(f"{SEG} from {BM}: stored first cut {CUT1}, T. Bird cut {TB}; as it is with the speech answered greedily: first cut {r0[0]}, tower {r0[1]} (speech {r0[1] - r0[0]}), "
    f"T. Bird cut {r0[2]}; end {toad(r0[4])}")
res = []
best = r0[2]
for i in range(T0, T1):
    for btn in BTNS:
        if btn in sg[i].split("+") or banned1((sg[i] + "+" + btn).lstrip("+")):
            continue
        e.mload(base)
        r = finish(i, (i, btn))
        if r is None:
            res.append((9999, i, btn, None, None, None))
            continue
        t = toad(r[4])
        res.append((r[2], i, btn, r[0], r[1], (t["hp"], t["lives"], t["score"])))
        if r[2] < best:
            best = r[2]
            log(f"  {btn} on index {i}: first cut {r[0]}, tower {r[1]} (speech {r[1] - r[0]}), T. Bird cut {r[2]} ({r[2] - TB:+d}); health / lives / score {(t['hp'], t['lives'], t['score'])}")
            write_json(FIX / f"u17f_end_{tag}_best.json", {"segment": SEG, "bookmark": BM, "press": [i, btn], "cut1": r[0], "tower": r[1], "tbird": r[2], "inputs_from": i, "inputs": r[3]})
    e.mload(base)
    e.step(bt(sg[i]), 1)
    nb = e.msave()
    e.mfree(base)
    base = nb
    if (i - T0) % 25 == 24:
        d = {}
        for x in res:
            d[x[0]] = d.get(x[0], 0) + 1
        log(f"    ... index {i}: {len(res)} variants; T. Bird cut -> variants {sorted(d.items())}")
d = {}
for x in res:
    d[(x[0], None if x[3] is None else x[4] - x[3])] = d.get((x[0], None if x[3] is None else x[4] - x[3]), 0) + 1
log(f"variants {len(res)}; (T. Bird cut, speech frames) -> variants: {sorted(d.items(), key=str)}")
write_json(FIX / f"u17f_end_{tag}.json", {"segment": SEG, "bookmark": BM, "T0": T0, "T1": T1, "results": sorted(res, key=str)[:400]})
e.close()

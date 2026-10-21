"""Track END probe: the Dark Queen's speech skip. From up14's state shortly before the first 13->254 cut (frame 46751):
which single-frame press, on which frame, brings the game back to the tower soonest?  -> logs/fix/end_skip.tsv"""
from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
CUT1 = 46751
e = BizHawk(log_name="end_skip.log")
e.load("cap14_f46000")
for i in range(46000, CUT1 - 30):
    e.step(bt(lines[i]) if i < len(lines) else (), 1)
base = e.msave()                                   # frame CUT1-30 done


def trial(sched, limit=400):
    """sched: {frame offset from CUT1 (the press is the input of frame CUT1+j): buttons}. Returns (cut1, back, rtn at back)."""
    e.mload(base)
    f = CUT1 - 30
    cut = back = None
    prev = 13
    while f < CUT1 + limit:
        j = f + 1 - CUT1
        e.step(sched.get(j, ()), 1)
        f += 1
        lv = e.byte(0x10)
        if cut is None and lv == 254:
            cut = f
        if cut is not None and lv == 13:
            back = f
            break
        prev = lv
    return cut, back


rows = []
print("no press:", trial({}, 1400), flush=True)
for btn in ("A", "B", "Select"):
    for j in range(-8, 26):
        c, b = trial({j: (btn,)})
        rows.append((btn, "single", j, c, b))
        print(btn, "single press on frame cut1%+d" % j, "-> cut", c, "back", b, flush=True)
for name, mk in (("A held from cut1-20", lambda j: ("A",) if j >= -20 else ()),
                 ("A every other frame from cut1-20", lambda j: ("A",) if j >= -20 and j % 2 == 0 else ()),
                 ("A every other frame (odd) from cut1-19", lambda j: ("A",) if j >= -19 and j % 2 else ()),
                 ("A,B alternating from cut1-20", lambda j: (("A",) if j % 2 == 0 else ("B",)) if j >= -20 else ()),
                 ("A 2 on 2 off", lambda j: ("A",) if j >= -20 and (j % 4) < 2 else ())):
    c, b = trial({j: mk(j) for j in range(-30, 400)})
    rows.append((name, "pattern", 0, c, b))
    print(name, "-> cut", c, "back", b, flush=True)
(LOGS_DIR / "fix" / "end_skip.tsv").write_text("\n".join("\t".join(map(str, r)) for r in rows) + "\n")
e.close()

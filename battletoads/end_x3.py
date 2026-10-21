"""Track END probe 3: what sets the delay between the cut to the Queen's speech and the first frame a press skips it?
up14 state, Select pressed on one frame during the Queen's 122-frame stand; A/B alternated on every frame after the cut (a new
press every frame), so 'back - cut1' is the exact first polled frame.   -> logs/fix/end_x3.tsv"""
from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
START = 46600
e = BizHawk(log_name="end_x3.log")
e.load("cap14_f46000")
for i in range(46000, START):
    e.step(bt(lines[i]) if i < len(lines) else (), 1)
base = e.msave()
rows = []
for j in [0] + list(range(46602, 46752, 3)):
    e.mload(base)
    f = START
    cut = back = None
    ram_cut = None
    while f < 46800:
        if cut is None:
            b = ("Select",) if f + 1 == j else ()
        else:
            b = ("A",) if (f - cut) % 2 == 0 else ("B",)
        e.step(b, 1)
        f += 1
        lv = e.byte(0x10)
        if cut is None and lv == 254:
            cut = f
            ram_cut = e.ram_all()
        elif cut is not None and lv == 13:
            back = f
            break
    m = ram_cut
    rows.append((j, cut, back, back - cut if back else None, m[0x25], m[0x26], m[0x27], m[0x28], m[0x0B], m[0x0C], m[0xCE], m[0xBD], m[0x0D]))
    print(*rows[-1], flush=True)
(LOGS_DIR / "fix" / "end_x3.tsv").write_text("select_frame\tcut1\tback\tdelay\trng25\trng26\trng27\trng28\tt0b\tt0c\tCE\tBD\tx0D\n" + "\n".join("\t".join(map(str, r)) for r in rows) + "\n")
e.close()

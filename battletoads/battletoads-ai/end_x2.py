"""Track END probe 2: do inputs after the last hit change the Queen's whirl-timer reloads (RNG) and does the toad still move?
From up14's final-hit state (frame 46085). One press of <button> on frame j, then nothing; read the first reload (rise frame 27
= frame 46485): timer $4F0, direction $4E1, angle $559.   -> logs/fix/end_x2.tsv"""
import sys
from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
HIT, RELOAD1 = 46085, 46485
e = BizHawk(log_name="end_x2.log")
e.load("cap14_f46000")
for i in range(46000, HIT):
    e.step(bt(lines[i]), 1)
base = e.msave()
s8 = lambda v: v - 256 if v > 127 else v
rows = []


def trial(sched, upto=RELOAD1):
    e.mload(base)
    f = HIT
    while f < upto:
        e.step(sched.get(f + 1, ()), 1)
        f += 1
    m = e.ram_all()
    return m


m = trial({})
print("idle: A", m[0x4F0], "dir", s8(m[0x4E1]), "theta", m[0x559], "toad x", m[0x3FD], "h", m[0x439], "hp", m[0x51A], "rng", list(m[0x25:0x29]), flush=True)
for btn in (("Select",), ("B",), ("A",), ("Right",), ("Left",), ("Up",), ("Down",), ("Start",)):
    for j in list(range(46090, 46480, 13)):
        if btn == ("Start",) and j > 46100:
            break
        m = trial({j: btn})
        rows.append(("+".join(btn), j, m[0x4F0], s8(m[0x4E1]), m[0x559], m[0x3FD], m[0x439], m[0x51A], m[0x10]))
        print(*rows[-1], flush=True)
# hold Right for 60 frames: does the toad walk?
for btn in ("Right", "Left"):
    m = trial({j: (btn,) for j in range(46260, 46320)})
    print("hold", btn, "60 frames from 46260: A", m[0x4F0], "dir", s8(m[0x4E1]), "toad x", m[0x3FD], "h", m[0x439], "hp", m[0x51A], flush=True)
(LOGS_DIR / "fix" / "end_x2.tsv").write_text("button\tframe\tA\tdir\ttheta\ttoad_x\ttoad_h\ttoad_hp\tlevel\n" + "\n".join("\t".join(map(str, r)) for r in rows) + "\n")
e.close()

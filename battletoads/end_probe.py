"""What happens after the last hit on the Dark Queen? Replay the verified run's tail from the 46000 bookmark, then keep
going with no input, logging the level byte and a few RAM bytes every frame and a screenshot every 15 frames.
(Checks a viewer's claim that the speedrun clock should stop later than our level-byte change.)"""
import sys
from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR
lines = [l for l in open("logs/up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name="end_probe.log")
e.load("cap14_f46000")
rows = []
EXTRA = 2400
for i in range(46000, len(lines) + EXTRA):
    e.step(bt(lines[i]) if i < len(lines) else (), 1)
    f = i + 1
    lv = e.ram(0x10)[0]
    rows.append((f, lv, e.ram(0x0B)[0], e.ram(0x586)[0]))
    if f >= 46060 and (f - 46060) % 15 == 0:
        e.screenshot(f"end_probe/f{f:06d}")
open(LOGS_DIR / "end_probe.tsv", "w").write("\n".join("\t".join(map(str, r)) for r in rows))
prev = None
for f, lv, t, q in rows:
    if lv != prev:
        print("frame", f, "level byte", lv); prev = lv
e.close()

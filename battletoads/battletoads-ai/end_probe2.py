"""From the verified run's last frame (46751, cut to the Dark Queen's speech): how fast can the speech be skipped, and when
does the game cut to Professor T. Bird (level byte 13 -> 254 the second time)? Tries several mash patterns."""
from toads.emulator import BizHawk
lines = [l for l in open("logs/up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name="end_probe2.log")
e.load("cap14_f46000")
for i in range(46000, len(lines)):
    e.step(bt(lines[i]), 1)
base = e.msave()
pats = {"none": [()], "start_alt": [("Start",), ()], "a_alt": [("A",), ()], "b_alt": [("B",), ()],
        "start_hold": [("Start",)], "a_hold": [("A",)], "ab_alt": [("A", "B"), ()], "start_a_alt": [("Start",), ("A",)],
        "sel_alt": [("Select",), ()]}
for name, pat in pats.items():
    e.mload(base)
    back13 = tbird = None
    prev = e.ram(0x10)[0]
    for k in range(2600):
        e.step(pat[k % len(pat)], 1)
        lv = e.ram(0x10)[0]
        f = 46751 + k + 1
        if lv == 13 and prev != 13 and back13 is None:
            back13 = f
        if back13 and lv == 254 and prev == 13:
            tbird = f
            break
        prev = lv
    print(f"{name:12s} back to the tower at {back13}, cut to T. Bird at {tbird}", flush=True)
e.close()

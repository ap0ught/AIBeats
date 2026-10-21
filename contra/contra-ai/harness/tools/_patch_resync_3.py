"""One-off patch of contra/resync.py (kept for the record): base-room advance must start the frame AFTER
INDOOR_SCREEN_CLEARED ($37) reads $80; an Up that is read earlier is a failure ("elec")."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b)


rep('''"hud": 0x6A, "elr": 0x2D, "elec": 0xC8}''', '''"hud": 0x6A, "elr": 0x2D, "elec": 0xC8, "adv": 0xD0}''')
rep('''            el = s.get("elec", 0)
            if stop_on_death and el and not prev_elec:
                reason, stop = "elec", True
                break
            prev_elec = el''',
    '''            el = s.get("elec", 0)
            if stop_on_death and el and not prev_elec:
                reason, stop = "elec", True
                break
            prev_elec = el
            # the walk to the next room must start the frame AFTER $37 reads $80. An Up read on the frame the
            # flag is set still starts the walk, but one frame late, and the movie's next three Ups are then
            # each read one frame too early and ignored.
            ad = s.get("adv", 0)
            if stop_on_death and ad and not prev_adv and prev_cleared != 0x80 and s["loc"] == 1 and s["level"] == lvl0:
                reason, stop = "elec", True
                break
            prev_adv, prev_cleared = ad, s["cleared"]''')
rep('''    prev_elec = s0.get("elec", 0)''', '''    prev_elec = s0.get("elec", 0)
    prev_adv, prev_cleared = s0.get("adv", 0), s0.get("cleared", 0)''')
rep('''            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 and s["cleared"]), None)''',
    '''            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 - 1 and s["cleared"] == 0x80), None)''')
rep('''                n = (c0 + j) - up + 1                    # Up must be read on the frame AFTER the flag is set''',
    '''                n = max(1, (c0 + j) - up + 1)            # Up must be read on the frame AFTER the flag reads $80''')
tmp = p.with_name("resync.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup3"))
os.replace(tmp, p)
print("patched")

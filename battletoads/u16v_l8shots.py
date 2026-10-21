"""Verifier, pictures only: replay the list and photograph Level 8 (frames 12456-16330) every 45 frames."""
import hashlib
import sys
from pathlib import Path
from toads.emulator import BizHawk, BUTTONS

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "logs" / "fix" / "u16v_shots"
path = sys.argv[1]
rows = Path(path).read_text(encoding="utf-8").split("\n")
if rows[-1] == "":
    rows = rows[:-1]
ins = [tuple(t for t in x.replace("+", ",").split(",") if t) for x in rows[1:]]
assert all(b in BUTTONS for f in ins for b in f)
e = BizHawk(log_name="u16v_l8shots_emu.log", fields={"level": 0x10})
for i, btn in enumerate(ins):
    f = i + 1
    e.step(btn, 1)
    if 12456 <= f <= 16335 and (f - 12456) % 45 == 0:
        e.cmd(f"screenshot {SHOTS / ('l8_f%05d.png' % f)}")
print("RAM sha1 after the last input:", hashlib.sha1(e.ram_all()).hexdigest())
e.close()

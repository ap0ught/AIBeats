"""EARLY track (2026-10-09): replay a climb piece from early_l8climb.py on the up14 snapshot and report where the toad is.
    python early_l8climb_verify.py logs/fix/early_l8climb_460.json   -> appends to logs/fix/early_l8climb_verify.txt"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
F = {"level": 0x10, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
j = json.load(open(sys.argv[1]))
lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_l8climb_verify.log", fields=F)
e.load("cap14_f12000")
for i in range(12000, j["from_frame"]):
    s = e.step(bt(lines[i]), 1)
base, lives0 = s.height | s.hh << 8, s.lives
minhp = 99
for b in j["inputs"]:
    s = e.step(bt(b), 1)
    minhp = min(minhp, s.hp)
bad = [b for b in j["inputs"] if ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b) or "Start" in b]
line = (f"{sys.argv[1]}: {len(j['inputs'])} inputs from up14 frame {j['from_frame']} -> frame {j['from_frame'] + len(j['inputs'])}: toad x {s.x} "
        f"+{(s.height | s.hh << 8) - base} px, z {s.z}, hp {s.hp} (lowest {minhp}), lives {s.lives} (start {lives0}); banned/Start presses {len(bad)}; "
        f"up14 needed {j.get('up14_frames')} frames for this height")
print(line)
open(LOGS_DIR / "fix" / "early_l8climb_verify.txt", "a", encoding="utf-8").write(line + "\n")
e.close()

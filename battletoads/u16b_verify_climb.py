"""u16b: independent replay of a climb piece (u16b_climb*.py result) from the bookmark of up14 frame 12488 (early_L8_p0).
    python u16b_verify_climb.py <climb json>   -> appends one line to logs/fix/u16b_verify_climb.txt
Reports the frame the arena floor is first stood on, the frame the arrival cutscene starts (animation 50) and the toad's x
there, whether the toad was flattened (animation 85/86), the control frame and x, lowest health, lives, banned presses."""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, banned, FIX
F = {"level": 0x10, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
for k in range(6):
    F[f"sc{k}"] = 0x5F4 + k
j = json.load(open(sys.argv[1]))
e = BizHawk(log_name="u16b_verify_climb.log", fields=F)
s = e.load("early_L8_p0")
base, lives0 = s.height | s.hh << 8, s.lives
minhp, arena, cut, flat = 99, None, None, False
for i, b in enumerate(j["inputs"]):
    s = e.step(bt(b), 1)
    minhp = min(minhp, s.hp)
    dh = (s.height | s.hh << 8) - base
    if arena is None and dh >= 4030 and s.z == 0:
        arena = i + 1
    if cut is None and s.anim == 50:
        cut = (i + 1, s.x)
    if s.anim in (85, 86):
        flat = True
sc = int("".join(str(s[f"sc{k}"] & 15) for k in range(6)))
nb = sum(1 for b in j["inputs"] if banned(b))
after = e.step((), 1)
line = (f"{sys.argv[1]}: {len(j['inputs'])} inputs from up14 frame 12488 -> up14-clock frame {12488 + len(j['inputs'])} (up14's control frame: 15790, "
        f"{15790 - 12488 - len(j['inputs'])} frames saved); arena floor first stood on at +{arena} (up14 +3135); cutscene starts at +{cut[0]} with the toad at x {cut[1]} "
        f"(up14 +3168 at x 118; the record's boss descent at about +2799); flattened {flat}; at the last input: toad x {s.x} +{(s.height | s.hh << 8) - base} px "
        f"anim {s.anim} hp {s.hp} (lowest {minhp}) lives {s.lives} (start {lives0}) score {sc}; next frame anim {after.anim}; "
        f"banned presses (Left+Right, Up+Down, Start) {nb}; Select frames {sum(1 for b in j['inputs'] if 'Select' in b)}; Down frames {sum(1 for b in j['inputs'] if 'Down' in b)}")
print(line, flush=True)
open(FIX / "u16b_verify_climb.txt", "a", encoding="utf-8").write(line + "\n")
e.close()

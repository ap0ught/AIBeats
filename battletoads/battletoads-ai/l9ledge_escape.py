"""From the 6406 ledge landing (reached via jump + Left steer + Right hold, ~113 f after L9c 7852): try to get off it
into the water below before the bug grabs (2026-10-07)."""
import json
from toads.emulator import BizHawk
l9 = [x.replace(",", "+") for x in json.load(open("logs/pbeam_L9c.json"))["inputs"]]
e = BizHawk(log_name="ledge_escape.log"); e.load("L9_at7800")
for b in l9[7800:7852]: e.step(tuple(v for v in b.split("+") if v), 1)
def rd():
    m = e.ram(0, 0x800); return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x3B5], m[0x51A], m[0x11], m[0x87] | m[0x88] << 8)
n = 0; land = None
for b, k in [(("Right",), 8), (("Right", "A"), 10), (("Left",), 30), ((), 30), (("Right",), 160)]:
    for i in range(k):
        e.step(b, 1); n += 1; s = rd()
        if s[2] == 0 and 6395 <= s[1] <= 6415 and s[0] >= 880: land = (n, s); break
    if land: break
print("landing", land, flush=True)
if not land: e.close(); raise SystemExit
e.save("L9_ledge6406b"); base = e.msave()
seqs = {"Right+A hold 16": [("Right", "A")] * 16 + [("Right",)] * 60, "A 1, Right": [("A",)] + [("Right",)] * 70, "Right+A 4, idle": [("Right", "A")] * 4 + [()] * 70,
        "Down+Right": [("Down", "Right")] * 70, "Down 4, Right": [("Down",)] * 4 + [("Right",)] * 70, "Right 2, Down+A": [("Right",)] * 2 + [("Down", "A")] * 8 + [()] * 60,
        "Left+A 6, Right": [("Left", "A")] * 6 + [("Right",)] * 70, "B, Right": [("B",)] + [()] * 12 + [("Right",)] * 60, "Up+A": [("Up", "A")] * 70, "idle": [()] * 70,
        "Right 1 frame then idle": [("Right",)] + [()] * 70, "Right+B": [("Right", "B")] + [("Right",)] * 70}
for name, seq in seqs.items():
    e.mload(base); out = []; esc = None
    for i, b in enumerate(seq):
        e.step(b, 1); s = rd()
        if s[3] in (98, 99) and esc is None: esc = ("SWIM", i + 1, s[0], s[1])
        if s[6] > 775 and esc is None: esc = ("SCROLL", i + 1, s[0], s[1], s[6])
        if i % 10 == 9: out.append((i + 1, s[0], s[1], s[2], s[3]))
        if s[4] < 47 or s[5] < 4: out.append(("HURT", i + 1, s[0], s[1], s[3])); break
    print(name, "->", esc, out[:7], flush=True)
e.close()

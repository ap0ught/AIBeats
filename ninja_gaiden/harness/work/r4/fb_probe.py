"""fireball probe: idle (or rows spec) from the 6-4b control; print enemy slots (id, x, y, pose, hp, xspd) per frame"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
from jq_play import parse  # noqa
rows = parse(sys.argv[1])
e = C.open_emu("r4_fb.log")
try:
    s0 = e.load("tmp/a56r2_64b_control")
    for i, r in enumerate(rows):
        s = e.step("+".join(r) if r else "", 1) if False else e.run([r])
        ram = e.ram(0x400, 0xA0)
        sl = []
        for k in range(8):
            if ram[k] and ram[0x98 + k - 0x0] if False else ram[k]:
                sl.append((k, ram[k], ram[0x60 + k], ram[0x80 + k], ram[0x38 + k], ram[0x90 + k], ram[0x50 + k] if ram[0x50+k] < 128 else ram[0x50+k]-256))
        r91 = e.ram(0x90, 3)
        if i % int(sys.argv[2] if len(sys.argv) > 2 else 1) == 0:
            print(i + 1, "R", s["x"], s["y"], "hp", s["hp"], "90-92", list(r91), sl)
finally:
    e.close()

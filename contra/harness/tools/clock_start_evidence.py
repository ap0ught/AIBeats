"""Clock START evidence: on which frame do the blue life medals first appear, in RAM, in OAM and in the picture?

    python tools/clock_start_evidence.py [core]

Plays the shortest opening (Select on frame 11, Start on frame 12, nothing else) from power-on with a per-frame
trace, finds the first frame whose RAM has SPRITE_LOAD_TYPE ($6A) != 0, then replays from power-on and, for the
frames around it, saves a screenshot, the PPU's OAM and the game's sprite buffer ($0200).
Writes shots/clock_start/*.png and logs/clock_start_evidence.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR, SHOTS_DIR  # noqa: E402

core = sys.argv[1] if len(sys.argv) > 1 else "NesHawk"
F = {"groutine": 0x18, "lroutine": 0x2C, "level": 0x30, "hud": 0x6A, "pstate": 0x90, "fc": 0x1A, "lives": 0x32,
     "ppumask": 0xFE, "ppuready": 0x20, "y": 0x31A, "x": 0x334, "spr": 0x300}
first = 11 if core == "NesHawk" else 10
OPEN = [()] * (first - 2) + [("Select",), ("Start",)] + [()] * 800


def medals(buf: bytes):
    """HUD medal entries in a 256-byte OAM image: tile $0A at Y=$10 (hud_sprites / sprite_medal_x_offset)."""
    out = []
    for i in range(0, 256, 4):
        y, tile, attr, x = buf[i:i + 4]
        if tile == 0x0A and y == 0x10:
            out.append({"slot": i // 4, "x": x, "attr": attr})
    return out


def blue_pixels(png: Path):
    """Count non-black pixels in the HUD medal area of a screenshot (x 16..68, y 16..32 in NES pixels)."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    w, h = im.size
    sx, sy = w / 256.0, h / (240.0 if h >= 240 else 224.0)
    top = 0 if h >= 240 else 8          # a 224-line picture has lines 8..231
    box = (int(16 * sx), int((17 - top) * sy), int(68 * sx), int((33 - top) * sy))
    crop = im.crop(box)
    px = list(crop.getdata())
    return sum(1 for p in px if p[2] > 150 and p[0] < 120), sum(1 for p in px if max(p) > 40), im.size


e = BizHawk(log_name=f"clock_start_{core}.log", fields=F, core=core)
try:
    e.trace(True)
    e.run(OPEN)
    tr = e.last_trace
finally:
    e.close()
n = next(s["frame"] for s in tr if s["hud"] != 0 and s["groutine"] == 5)
l4 = next(s["frame"] for s in tr if s["lroutine"] == 4 and s["groutine"] == 5)
g5 = next(s["frame"] for s in tr if s["groutine"] == 5)
ps = next(s["frame"] for s in tr if s["pstate"] == 1 and s["groutine"] == 5)
print(f"{core}: game routine 5 first at frame {g5}; $6A != 0 first at frame {n}; level routine 4 first at {l4}; "
      f"player state 1 first at {ps}")
for s in tr:
    if n - 3 <= s["frame"] <= n + 4:
        print("  ", s)

d = SHOTS_DIR / "clock_start"
d.mkdir(parents=True, exist_ok=True)
rows = []
e = BizHawk(log_name=f"clock_start_{core}_2.log", fields=F, core=core)
try:
    upto = n - 5
    e.run(OPEN[:upto - 1])                 # the bridge starts at frame 1
    assert e.state()["frame"] == upto
    for _ in range(11):
        s = e.step((), 1)
        f = s["frame"]
        png = e.screenshot(f"clock_start/{core}_f{f}")
        oam = e.oam()
        buf = e.ram(0x200, 256)
        blue, lit, size = blue_pixels(png)
        rows.append({"frame": f, "ram_6A": s["hud"], "lroutine": s["lroutine"], "lagged": s["lagged"],
                     "medals_in_ram_buffer_0200": medals(buf), "medals_in_ppu_oam": medals(oam),
                     "blue_pixels_in_hud_box": blue, "lit_pixels_in_hud_box": lit, "screenshot": png.name,
                     "size": size})
        print(f"frame {f}: $6A={s['hud']:3d} lroutine={s['lroutine']} lagged={s['lagged']} "
              f"buffer medals={len(medals(buf))} OAM medals={len(medals(oam))} blue px={blue} lit px={lit}")
finally:
    e.close()
out = {"core": core, "opening": f"Select on frame {first}, Start on frame {first + 1}", "first_frame_ram_6A_nonzero": n,
       "first_frame_level_routine_4": l4, "first_frame_player_state_1": ps, "frames": rows}
(LOGS_DIR / f"clock_start_evidence_{core}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

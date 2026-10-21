"""The search wall: N random attempts from one bookmark, filmed and tiled into one video.

    python youtube_wall.py <brute run> <bookmark> <cols> <rows> [frames]   -> video/wall_<run>.mp4

Each cell replays one attempt from logs/brute/<run>/aNNNN.json at 30 fps (every other frame), with a thin
status bar: attempt number, frames, and how it ended (health squares, died).
"""
import json, sys, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR, VIDEO_DIR

run, bm, cols, rows = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
frames = int(sys.argv[5]) if len(sys.argv) > 5 else 1500
n = cols * rows
atts = sorted((LOGS_DIR / "brute" / run).glob("a*.json"))[:n]
cap = SHOTS_DIR / "wall" / run
cap.mkdir(parents=True, exist_ok=True)
emu = BizHawk(log_name=f"wall_{run}.log")
meta = []
for p in atts:
    j = json.loads(p.read_text())
    d = cap / p.stem
    d.mkdir(exist_ok=True)
    if len(list(d.glob("*.png"))) >= frames // 2:
        meta.append(json.loads((d / "meta.json").read_text()))
        continue
    emu.load(bm)
    hp = []
    for i, b in enumerate(j["inputs"][:frames]):
        s = emu.step(tuple(x for x in b.split("+") if x), 1)
        if i % 2 == 0:
            shutil.copyfile(emu.screenshot(f"_wall_{run}"), d / f"{i // 2:04d}.png")
            hp.append(sum(1 for k in range(6) if s.get(f"hud{k}") == 244))
    m = {"attempt": p.stem, "hp": hp, "lives": s.get("lives", 0)}
    (d / "meta.json").write_text(json.dumps(m))
    meta.append(m)
    print(p.stem, "filmed", flush=True)
emu.close()

CW, CH = 256, 240
W, H = cols * CW, rows * CH
font = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 13)
out = VIDEO_DIR / f"wall_{run}.mp4"
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                        "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(out)],
                       stdin=subprocess.PIPE)
total = frames // 2
for t in range(total):
    im = Image.new("RGB", (W, H), (6, 8, 6))
    dr = ImageDraw.Draw(im)
    for k, m in enumerate(meta):
        d = cap / m["attempt"]
        f = d / f"{min(t, len(m['hp']) - 1):04d}.png"
        x, y = (k % cols) * CW, (k // cols) * CH
        if f.exists():
            im.paste(Image.open(f).convert("RGB"), (x, y))
        hp = m["hp"][min(t, len(m["hp"]) - 1)]
        dead = t >= len(m["hp"]) - 1 and m["lives"] < 3
        col = (235, 70, 70) if dead else (120, 220, 60)
        dr.rectangle((x, y + 224, x + CW, y + CH), fill=(10, 14, 10))
        dr.text((x + 4, y + 225), f"#{int(m['attempt'][1:])}  {'#' * hp}{'.' * (6 - hp)}  {'DEAD' if dead else ''}",
                font=font, fill=col)
    enc.stdin.write(im.tobytes())
enc.stdin.close()
enc.wait()
print("wrote", out)

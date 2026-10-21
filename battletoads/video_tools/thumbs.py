"""Three A/B thumbnails (1280x720 PNG, drawn at 1920x1080):
  A  "the record":  his surprised face + 12:23 beating the crossed-out 12:29 world record, over the Turbo Tunnel
  B  "the grid":    23 crashed attempts, the one that made it lit up (the original thumbnail, refreshed)
  C  "the boss":    the Dark Queen fight, big AI vs BATTLETOADS, 12 DAYS badge
-> out/thumb_A_record.png, out/thumb_B_grid.png, out/thumb_C_boss.png"""
from __future__ import annotations

import subprocess

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from style import *  # noqa: F401,F403
from fx import Camera, logo, scanlines
from outro import key_mask, SRC

LEAD = 6


def nes(row):
    return next(nes_frames(VIDEO / "up14.mkv", LEAD + row, 1))


def wip(row):
    return next(nes_frames(VIDEO / "fullrun_wip.mkv", 9 + row, 1))


def face(t=2.0, scale=1.0):
    """his cut-out from the outro clip, with a white rim for contrast"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(SRC), "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = Image.frombuffer("RGB", (W, H), raw).copy()
    a = key_mask(fr)
    box = a.point(lambda p: 255 if p > 40 else 0).getbbox()
    fr, a = fr.crop(box), a.crop(box)
    fr = ImageEnhance.Contrast(ImageEnhance.Brightness(fr).enhance(1.12)).enhance(1.12)
    if scale != 1.0:
        fr = fr.resize((int(fr.width * scale), int(fr.height * scale)), Image.LANCZOS)
        a = a.resize(fr.size, Image.LANCZOS)
    rim = a.filter(ImageFilter.MaxFilter(17))
    out = Image.new("RGBA", fr.size)
    out.paste((255, 255, 255, 255), (0, 0), rim)
    out.paste(fr, (0, 0), a)
    return out


def bg_game(nesfr, scale=8.0, cx=128, cy=120, dark=0.75, blur=0):
    im = Camera(scale, cx=cx, cy=cy).render(nesfr)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(im).enhance(dark)


def outline_text(d, xy, text, f, fill, stroke=10, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def thumb_a():
    im = bg_game(wip(13620), 7.0, 128, 120, 0.6, blur=2)
    d = ImageDraw.Draw(im)
    # the record, crossed out
    f_small = font("ROCKEB.TTF", 90)
    outline_text(d, (560, 230), "WORLD RECORD", font("ROCKEB.TTF", 60), (230, 230, 230), 8)
    outline_text(d, (560, 340), "12:29", f_small.font_variant(size=150), (200, 200, 200), 10)
    d.line((340, 370, 780, 310), fill=RED, width=26)
    d.line((340, 370, 780, 310), fill=(0, 0, 0), width=6)
    # the AI time, huge, gold
    t = logo("12:23", 300)
    im.paste(t, (560 - t.width // 2, 480), t)
    lg = logo("AI", 170, top=(200, 255, 140), bottom=(40, 160, 30), extrude=(10, 50, 10))
    im.paste(lg, (40, 30), lg)
    f = face(2.0, 0.92)
    im.paste(f, (W - f.width + 60, H - f.height), f)
    return im


def thumb_a2(row=41505, s_=7.0, cy_off=0):
    """the record thumbnail without a face: a big action moment on the left, the numbers on the right"""
    from ramview import Cap
    from fx import toad_box
    from shots import data_row
    cap = Cap("cap14")
    tb = toad_box(cap, data_row("cap14", row))
    tx, ty = ((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2) if tb else (128, 120)
    cam = Camera(s_, cx=tx + (W * 0.22) / s_, cy=ty + cy_off)
    im = ImageEnhance.Brightness(cam.render(nes(row))).enhance(0.95)
    shade = Image.new("L", (W, H))
    sd = ImageDraw.Draw(shade)
    for x in range(W):
        sd.line((x, 0, x, H), fill=int(max(0, 200 * (x - W * 0.42) / (W * 0.58))))
    im = Image.composite(Image.new("RGB", (W, H)), im, shade)
    d = ImageDraw.Draw(im)
    cx = 1440
    outline_text(d, (cx, 240), "WORLD RECORD", font("ROCKEB.TTF", 60), (230, 230, 230), 8)
    outline_text(d, (cx, 350), "12:29", font("ROCKEB.TTF", 150), (200, 200, 200), 10)
    d.line((cx - 220, 380, cx + 220, 320), fill=RED, width=26)
    d.line((cx - 220, 380, cx + 220, 320), fill=(0, 0, 0), width=6)
    t = logo("12:23", 290)
    im.paste(t, (cx - t.width // 2, 490), t)
    lg = logo("AI", 170, top=(200, 255, 140), bottom=(40, 160, 30), extrude=(10, 50, 10))
    im.paste(lg, (W - lg.width - 40, 30), lg)
    return im


def thumb_b():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2.6", "-i", str(CLIPS / "s01_montage.mp4"), "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    base = Image.frombuffer("RGB", (W, H), raw).copy()
    im = ImageEnhance.Brightness(base).enhance(0.7)
    tw, th = W // 6, H // 4
    t_ = 15
    sx, sy = (t_ % 6) * tw, (t_ // 6) * th
    tile = base.crop((sx, sy, sx + tw, sy + th)).resize((int(tw * 1.8), int(th * 1.8)), Image.NEAREST)
    cx, cy = sx + tw // 2 - tile.width // 2, sy + th // 2 - tile.height // 2 + 40
    glow = Image.new("RGB", (W, H))
    ImageDraw.Draw(glow).rectangle((cx - 25, cy - 25, cx + tile.width + 25, cy + tile.height + 25), fill=GOLD)
    im = ImageChops.add(im, glow.filter(ImageFilter.GaussianBlur(36)))
    im.paste(tile, (cx, cy))
    d = ImageDraw.Draw(im)
    d.rectangle((cx, cy, cx + tile.width, cy + tile.height), outline=GOLD, width=12)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, 0, W, 300), fill=(0, 0, 0, 205))
    im.paste(band, (0, 0), band)
    lg = logo("AI vs BATTLETOADS", 150)
    im.paste(lg, ((W - lg.width) // 2, 150 - lg.height // 2), lg)
    y = cy + tile.height + 55
    d.rectangle((W // 2 - 380, y - 46, W // 2 + 380, y + 46), fill=(0, 0, 0))
    outline_text(d, (W // 2, y), "23 CRASHED. 1 MADE IT.", font("arialbd.ttf", 64), GOLD, 4)
    return im


def thumb_c():
    im = bg_game(nes(46080), 6.0, 128, 125, 0.85)
    im = scanlines(im, 0.12)
    d = ImageDraw.Draw(im)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, H - 330, W, H), fill=(0, 0, 0, 210))
    im.paste(band, (0, 0), band)
    lg = logo("AI vs BATTLETOADS", 160)
    im.paste(lg, ((W - lg.width) // 2, H - 300), lg)
    d = ImageDraw.Draw(im)
    outline_text(d, (W // 2, H - 70), "IT TAUGHT ITSELF. 12 DAYS.", font("arialbd.ttf", 66), WHITE, 6)
    # corner badge
    d.rounded_rectangle((60, 50, 720, 190), 24, fill=RED, outline=(0, 0, 0), width=8)
    outline_text(d, (390, 120), "BEAT THE WR", font("ROCKEB.TTF", 72), WHITE, 6)
    return im


if __name__ == "__main__":
    for name, fn in (("thumb_A_record", lambda: thumb_a2(28951)), ("thumb_B_grid", thumb_b), ("thumb_C_boss", thumb_c)):
        fn().resize((1280, 720), Image.LANCZOS).save(OUT / f"{name}.png")
        print("wrote", OUT / f"{name}.png")

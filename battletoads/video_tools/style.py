"""Shared look for the Battletoads video: 1920x1080 at the NES frame rate, toad green + Battletoads gold,
chunky slanted 'logo' lettering for the slams, and helpers for shake/flash/ease."""
from __future__ import annotations
import math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1920, 1080
FPS = "150247/2500"
NES_FPS = 60.0988
FONTS = Path(r"C:\Windows\Fonts")
HERE = Path(__file__).resolve().parent
TOADS = HERE.parent
LOGS, VIDEO = TOADS / "logs", TOADS / "video"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
CLIPS = HERE / "clips"; CLIPS.mkdir(exist_ok=True)

BG = (8, 12, 10)
PANEL = (12, 18, 14)
GRID = (22, 32, 26)
DIM = (95, 112, 100)
TEXT = (215, 225, 215)
TOAD = (120, 220, 60)
GOLD = (255, 200, 40)
ORANGE = (255, 120, 20)
RED = (235, 60, 50)
CYAN = (60, 220, 255)
WHITE = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def mono(size, bold=False):
    return font("consolab.ttf" if bold else "consola.ttf", size)


def logo_text(text, size=150, top=(255, 236, 90), bottom=(255, 110, 10), outline=10, depth=14, shear=0.22,
              face="impact.ttf", extrude=(70, 25, 5)):
    """Battletoads-logo style lettering: slanted, vertical gold->orange gradient, a 3D extrusion and a thick black
    outline. Returns an RGBA image tightly cropped."""
    f = font(face, size)
    l, t, r, b = f.getbbox(text)
    tw, th = r - l, b - t
    pad = outline * 2 + depth + 20
    cw, ch = tw + pad * 2 + int(th * shear), th + pad * 2
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), text, font=f, fill=255)
    # shear to slant right
    mask = mask.transform(mask.size, Image.AFFINE, (1, shear, -shear * ch * 0.5, 0, 1, 0), Image.BICUBIC)
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # outline of the extruded shape
    ext = Image.new("L", (cw, ch), 0)
    for i in range(depth + 1):
        ext = ImageChops.lighter(ext, ImageChops.offset(mask, i // 2, i))
    big = ext.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    out.paste((0, 0, 0, 255), (0, 0), big)
    out.paste(extrude + (255,), (0, 0), ext)
    # gradient face
    grad = Image.new("RGBA", (cw, ch))
    gd = ImageDraw.Draw(grad)
    y0, y1 = pad, pad + th
    for y in range(ch):
        a = min(1, max(0, (y - y0) / max(1, y1 - y0)))
        a = a ** 1.3
        gd.line((0, y, cw, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * a) for i in range(3)) + (255,))
    out.paste(grad, (0, 0), mask)
    # thin highlight line along the top edge of the face
    hl = ImageChops.subtract(mask, ImageChops.offset(mask, 0, 3))
    out.paste((255, 255, 220, 255), (0, 0), hl.point(lambda v: v // 2))
    bbox = out.getbbox()
    return out.crop(bbox)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def ease_out_back(t, s=1.7):
    t = max(0.0, min(1.0, t)) - 1; return t * t * ((s + 1) * t + s) + 1


def nframes(sec):
    return max(1, int(round(sec * NES_FPS)))


class Writer:
    """pipe PIL frames into an x264 mp4 at the NES frame rate (no audio)"""
    def __init__(self, path, w=W, h=H, crf=17):
        self.path = Path(path)
        self.p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                                   "-r", FPS, "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                                   "-pix_fmt", "yuv420p", str(self.path)], stdin=subprocess.PIPE)
        self.n = 0

    def put(self, im):
        if im.mode != "RGB":
            im = im.convert("RGB")
        self.p.stdin.write(im.tobytes()); self.n += 1

    def close(self):
        self.p.stdin.close(); self.p.wait()
        return self.path


def nes_frames(src, start=0, count=None):
    """yield 256x224 RGB PIL frames from a raw NES capture, from frame index `start` (0-based, exact: decodes from 0)"""
    # every frame of the ffv1 captures is a keyframe, so an input seek lands exactly on frame `start`
    pre = ["-ss", f"{(start - 0.3) / NES_FPS:.5f}"] if start > 0 else []
    p = subprocess.Popen(["ffmpeg", "-v", "error"] + pre + ["-i", str(src), "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1 << 22)
    fb = 256 * 224 * 3
    n = 0
    while count is None or n < count:
        raw = p.stdout.read(fb)
        if len(raw) < fb:
            break
        yield Image.frombuffer("RGB", (256, 224), raw)
        n += 1
    p.kill()


def lead_in(src, n_inputs):
    """frames in the capture before input 1 (render_overlay skips these): capture frame = lead + input index"""
    total = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                "stream=nb_read_frames", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip())
    return max(0, total - n_inputs)

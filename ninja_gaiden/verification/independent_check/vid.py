"""Independent record-video frame extraction (local ffmpeg only). Timing only: never copy these frames into yt/.

Each output frame is labelled by its OWN presentation timestamp (ffmpeg showinfo, -copyts):
n = round(pts_time * 60). The container is CFR 60 with ms-rounded pts (steps of 16/17 ms), so
round(pts*60) is exact (|pts - n/60| <= 1 ms).
Usage:
  python vid.py png <n0> <n1> [x y w h [outw [tag]]]   -> work/verify/vid/<tag>f<n>.png
"""
import subprocess, sys, os, re, threading
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.normpath(os.path.join(HERE, "..", "..", "dl", "record_video", "v1890225973.mp4"))
OUT = os.path.join(HERE, "vid")
GAME = (600, 140, 1200, 900)   # game area in the 1920x1080 frame (4:3)
PTS = re.compile(r"pts_time:\s*([0-9.]+)")


def frames(n0, n1, crop=GAME, outw=None, margin=3):
    """yield (n, HxWx3 uint8) for video frames n0..n1 (labels from each frame's own pts)."""
    x, y, w, h = crop
    outw = outw or w
    outh = int(round(h * outw / w))
    vf = f"crop={w}:{h}:{x}:{y}" + (f",scale={outw}:{outh}:flags=area" if outw != w else "") + ",showinfo"
    t0 = max(0.0, (n0 - margin) / 60)
    count = n1 - n0 + 1 + 2 * margin
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "info", "-threads", "4", "-copyts", "-ss", f"{t0:.6f}",
           "-i", VIDEO, "-fps_mode", "passthrough", "-frames:v", str(count), "-vf", vf,
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pts = []
    ev = threading.Event()

    def rd():
        for line in p.stderr:
            m = PTS.search(line.decode("utf-8", "replace"))
            if m and "showinfo" in line.decode("utf-8", "replace"):
                pts.append(float(m.group(1)))
        ev.set()
    th = threading.Thread(target=rd, daemon=True)
    th.start()
    sz = outw * outh * 3
    seen = set()
    i = 0
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        t_wait = 0
        while len(pts) <= i and t_wait < 2000:
            ev.wait(0.005)
            t_wait += 1
        t = pts[i]
        i += 1
        n = int(round(t * 60))
        assert abs(t - n / 60) < 0.002, t
        assert n not in seen
        seen.add(n)
        if n0 <= n <= n1:
            yield n, np.frombuffer(b, np.uint8).reshape(outh, outw, 3)
    p.wait()

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "png":
        n0, n1 = int(sys.argv[2]), int(sys.argv[3])
        crop = tuple(map(int, sys.argv[4:8])) if len(sys.argv) >= 8 else GAME
        outw = int(sys.argv[8]) if len(sys.argv) >= 9 else None
        tag = sys.argv[9] if len(sys.argv) >= 10 else ""
        k = 0
        for n, a in frames(n0, n1, crop, outw):
            Image.fromarray(a).save(os.path.join(OUT, f"{tag}f{n}.png"))
            k += 1
        print("ok", k)

"""Which capture frame shows which emulated frame (2026-10-10).

BizHawk's A/V dump repeats one picture about every 7,996 frames to keep sound and picture together, so a capture of n
inputs holds a few frames more than n and a single offset cannot hold for the whole run: with the offset that is right
at the end, the picture early in the run is up to 5 frames ahead of the inputs. Someone counting frames on a video cut
with one offset would time the run 0.08 s long. This finds the repeats and gives the exact mapping.

    from capsync import Sync;  s = Sync("run1201");  s.cidx(k)   # 0-based capture frame of 1-based emulated frame k

Method: one pass over the capture (a hash and the mean brightness of every frame, cached in logs/<name>.sync.json). On a
lag frame (the trace's lag counter goes up) the game draws the same picture again; when that stops being true under the
current offset and is true under offset + 1 for three lag frames in a row, a repeat lies just before, and its exact
place is the last identical pair of capture frames there that is not a lag frame.

    python yt/capsync.py <name>        -> prints the repeats
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

YT = Path(__file__).resolve().parent
TOADS = YT.parent
LOGS, VIDEO = TOADS / "logs", TOADS / "video"


def scan(name):
    src = VIDEO / f"{name}.mkv"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1 << 22)
    fb = 256 * 224 * 3
    hs, dark = [], []
    while True:
        raw = p.stdout.read(fb)
        if len(raw) < fb:
            break
        hs.append(hashlib.md5(raw).hexdigest()[:12])
        dark.append(round(sum(raw[::97]) / len(raw[::97]), 1))      # a sparse sample is enough to tell black from picture
    p.wait()
    return hs, dark


def find_dups(hs, lag, n):
    """emulated frames k after which the capture shows frame k a second time.

    A lag frame k (the lag counter goes up) leaves the game no time to prepare the next picture, so picture k+1 equals
    picture k (true for about 9 in 10). With o repeats so far, frame k is capture frame k + o (one capture frame precedes
    input 1). The repeats come on a steady beat (about every 7,995 frames, measured on two captures), so: pick the first
    repeat d0 and the period P under which most lag frames show their repeated picture, then move each repeat to the real
    identical pair of capture frames nearest to it (within 20 frames)."""
    import bisect
    steps = len(hs) - n - 1
    if steps <= 0:
        return []
    lagk = [k for k in range(3, n) if lag.get(k, 0) != lag.get(k - 1, 0)]
    pre = []
    for o in range(steps + 1):
        acc, row = 0, [0]
        for k in lagk:
            acc += 1 if k + o + 1 < len(hs) and hs[k + o + 1] == hs[k + o] else 0
            row.append(acc)
        pre.append(row)

    def score(ds):
        tot, lo = 0, 0
        for o, d in enumerate(list(ds) + [n + 1]):
            hi = bisect.bisect_right(lagk, d)              # lag frames k <= d still use offset o
            tot += pre[o][hi] - pre[o][lo]
            lo = hi
        return tot

    best = (-1, None)
    for P in range(7975, 8016):
        for d0 in range(1000, 8200, 3):
            ds = [d0 + i * P for i in range(steps)]
            if ds[-1] >= n:
                continue
            sc = score(ds)
            if sc > best[0]:
                best = (sc, ds)
    dups = []
    for o, d in enumerate(best[1]):
        ident = [k for k in range(d - 20, d + 21) if hs[k + o] == hs[k + o + 1] and lag.get(k + 1, 0) == lag.get(k, 0)]
        dups.append(min(ident, key=lambda k: abs(k - d)) if ident else d)
    return dups


class Sync:
    def __init__(self, name, lag=None, n=None):
        p = LOGS / f"{name}.sync.json"
        if p.exists():
            d = json.loads(p.read_text())
        else:
            if lag is None:
                lag, n = {}, 0
                for ln in (LOGS / f"{name}.trace.txt").read_text().splitlines():
                    fr, _, st = ln.split("\t")
                    n = int(fr)
                    i = st.rfind("lag=")
                    lag[n] = int(st[i + 4:].split()[0]) if i >= 0 else 0
            sp = LOGS / f"{name}.scan.json"
            if sp.exists():
                sc = json.loads(sp.read_text())
                hs, dark = sc["hs"], sc["dark"]
            else:
                hs, dark = scan(name)
                sp.write_text(json.dumps({"hs": hs, "dark": dark, "n": n}))
            d = {"frames": len(hs), "inputs": n, "dups": find_dups(hs, lag, n), "dark": dark}
            p.write_text(json.dumps(d))
        self.frames, self.n, self.dups, self._dark = d["frames"], d["inputs"], d["dups"], d["dark"]
        self.first = self.frames - self.n - len(self.dups)     # capture frames before input 1

    def cidx(self, k):
        return k - 1 + self.first + sum(1 for kd in self.dups if kd < k)

    def dark(self, k):
        c = self.cidx(k)
        return self._dark[c] if 0 <= c < len(self._dark) else 255.0


if __name__ == "__main__":
    s = Sync(sys.argv[1])
    print(f"{sys.argv[1]}: {s.frames} capture frames for {s.n} inputs, {s.first} before input 1, repeats after emulated frames {s.dups}")

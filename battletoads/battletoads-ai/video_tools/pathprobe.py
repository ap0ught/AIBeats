"""Run many variants of one jump from a saved state and record the toad's path (screen sprite centre + camera x)
for the 'what the search tried' graphic. python yt/pathprobe.py -> yt/paths_l1.json"""
import sys, json
sys.path.insert(0, ".")
from toads.emulator import BizHawk
lines = [l for l in open("logs/up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
S, N = 2240, 72
e = BizHawk(log_name="pathprobe.log")
e.load("cap14_f2000")
for i in range(2000, S):
    e.step(bt(lines[i]), 1)
base = e.msave()

def toad_center():
    o = e.ram_domain("OAM", 0, 256)
    pts = [(o[i + 3], o[i] + 1) for i in range(4, 256, 4) if o[i] < 239 and 1 <= o[i + 1] < 0x20]
    if len(pts) < 3:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return ((min(xs) + max(xs) + 8) / 2, (min(ys) + max(ys) + 8) / 2)

def play(ins):
    e.mload(base)
    path = []
    for l in ins:
        e.step(bt(l), 1)
        c = toad_center()
        cam = e.ram(0x87)[0] + 256 * e.ram(0x88)[0]
        h = e.ram(0x439)[0] + 256 * e.ram(0x42A)[0]
        x = e.ram(0x3FD)[0] + 256 * e.ram(0x3EE)[0]
        lv = e.ram(0x10)[0]
        path.append((c[0] + cam if c else None, c[1] if c else None, h, x, lv))
    return path

real = lines[S:S + N]
out = [dict(kind="real", path=play(real))]
for a in range(2244, 2282, 2):
    for hold in (3, 6, 10, 16):
        for dirn in ("Right", "Right,Up", "Right,Down"):
            ins = []
            for j in range(N):
                f = S + j
                b = dirn
                if a <= f < a + hold:
                    b = b + ",A"
                ins.append(b)
            out.append(dict(kind="var", a=a, hold=hold, dir=dirn, path=play(ins)))
    print(a, flush=True)
json.dump(dict(S=S, N=N, variants=out), open("yt/paths_l1.json", "w"))
e.close()

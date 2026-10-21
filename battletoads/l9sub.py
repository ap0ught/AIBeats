"""Corridor: which x sub-pixel ($448) at the sync frame keeps the TAS's exact track? (2026-10-04) Debug pokes on a SNAPSHOT only (never in a run):
poke $448 (and optionally $466, the y accumulator) at ours 8403 = TAS 59565, replay the TAS inputs, report the exact-track length,
hurt and corridor exit."""
import json, re
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652
seg = json.load(open(LOGS_DIR / "pbeam_L9m.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475])
e = BizHawk(log_name="l9sub.log"); e.load(seg["bookmark"])
for b in ours[:8403]: e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave(); m = e.ram(0, 0x800); print("sync state: x sub", m[0x448], "y sub", m[0x466], flush=True)
t0 = 59565
def play():
    exact = t0; hurt = None; out = None
    for t in range(t0 + 1, 59990):
        b = legal(tas[t - ANCHOR]); e.step(b, 1); m = e.ram(0, 0x800); r = rows.get(t)
        if r and r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); m = e.ram(0, 0x800)
        s = st(m)
        if r and exact == t - 1 and (s[0], s[1]) == (r[1], r[2]): exact = t
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
        if s[0] >= 1115 and out is None: out = t
        if out and t > out + 30: break
    return exact, hurt, out
res = []
for xs in range(0, 256, 4):
    for ys in (None,):
        e.mload(base); e.poke(0x457, xs)
        exact, hurt, out = play(); res.append((exact - t0, xs, hurt, out))
        if exact - t0 > 12 or out: print(f"$457 {xs}: exact +{exact - t0}, hurt {hurt}, exit {out}", flush=True)
res.sort(reverse=True); print("best exact lengths:", res[:6], flush=True)
# with the best x sub-pixel, scan the y accumulator too
bx = res[0][1]
for ys in range(0, 256, 8):
    e.mload(base); e.poke(0x457, bx); e.poke(0x448, ys)
    exact, hurt, out = play()
    if exact - t0 > 12 or out: print(f"$457 {bx} $448 {ys}: exact +{exact - t0}, hurt {hurt}, exit {out}", flush=True)
e.close()

"""L12h walker finish probe: from w2h4_0 (toad riding the lower spring at 6454, walker 15 hp to the Right): walk Left n frames on the
spring, turn + kick Right; does the kick's hop come down on the spring again? Reports the kill frame, the toad's offset on the spring at
the kill, and when/where it stands afterwards."""
import sys
from l12h_lib import *
pn = sys.argv[1] if len(sys.argv) > 1 else "w2h4_0"
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_w6.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
res = []
for n in range(0, 22):
    for pat in (("Left",) * n, ("Left", "") + ("Left",) * max(n - 2, 0), ("",) * n):
        for turn in (("Right+B",), ("Right", "B"), ("Right", "Right+B"), ("B",)):
            e.mload(root); k = k0; seq = list(pat) + list(turn); run(e, seq); k += len(seq)
            kill = None; off = None; out = None
            for i in range(90):
                e.step((), 1); k += 1; seq.append(""); s = rd(e)
                if not alive(s): break
                f = foe(s)
                if kill is None and f and f[0][2] == 0: kill = k; off = dx(s["x"], spring(s))
                if kill and s["z"] == 0 and s["an"] in (1, 2, 3, 4, 5, 6, 7, 8):
                    out = (k, s["x"], s["H"], spring(s)); break
            if kill: res.append((out[2] if out else 0, kill, n, pat[:2], turn, off, out, seq))
res.sort(key=lambda r: (-(r[0] >= 4800), r[6][0] if r[6] else 9999))
for r in res[:20]: print("kill", r[1], "n", r[2], r[3], r[4], "offset at kill", r[5], "-> standing", r[6])
on = [r for r in res if r[0] >= 4800]
if on:
    b = min(on, key=lambda r: r[6][0])
    save_piece("w6", p["base"], p["base_k"], p["inputs"] + b[7], kill=b[1], board=b[6][0])
    e.load(p["base"]); run(e, p["inputs"] + b[7]); e.save("L12h_w6"); print("saved w6: kill", b[1], "standing on the spring at", b[6])
e.close()

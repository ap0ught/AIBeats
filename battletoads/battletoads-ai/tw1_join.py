"""TOWER1: find a short standing input sequence at the end of a piece that puts the toad in the state of an old-run
frame (x, height, standing, speed 0, facing, camera), with an even $0B difference.  Breadth-first over {'', Left, Right}.
    python tw1_join.py <piece> <old k> <out piece> [maxlen=12]"""
import sys
from tw1_lib import *
src, kold, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; maxlen = int(sys.argv[4]) if len(sys.argv) > 4 else 12
buf = open(FIX / "tw1_a.ram", "rb").read()
old = rdm(buf[kold * 2048:(kold + 1) * 2048]); mo = buf[kold * 2048:(kold + 1) * 2048]
print("old", kold, fmt(kold, "", old)[:130], "an", old["an"], "face", old["face"])
p = load_piece(src)
e = BizHawk(log_name="tw1_join.log"); e.load(p["base"]); run(e, p["inputs"])
s = rd(e); print("new", fmt(p["base_k"] + len(p["inputs"]), "", s)[:130], "an", s["an"], "face", s["face"])
front = [(e.msave(), [])]; best = None; seen = set()
for d in range(1, maxlen + 1):
    nxt = []
    for sid, path in front:
        for b in ("", "Left", "Right"):
            e.mload(sid); e.step(bt(b), 1); m = e.ram(0, 0x800); s = rdm(m)
            key = (s["x"], s["sub"], s["spd"], s["an"], s["face"], s["z"], s["H"], m[0x29], m[0x2A], m[0x2B], m[0x2C])
            if key in seen and False: continue
            ok = (s["x"] == old["x"] and s["H"] == old["H"] and s["z"] == 0 and s["spd"] == 0 and s["face"] == old["face"] and s["an"] == old["an"])
            if ok:
                dc = s["cam"] - old["cam"]; par = (s["t"] - old["t"]) & 1
                print(f"len {d} cam diff {dc} parity {'even' if not par else 'ODD'} sub {s['sub']}/{old['sub']}: {','.join(x or '-' for x in path + [b])}", flush=True)
                if dc == 0 and not par and best is None: best = path + [b]
            k2 = (d, s["x"], s["sub"], s["spd"], s["an"], s["face"], s["cam"])
            if k2 in seen: continue
            seen.add(k2); nxt.append((e.msave(), path + [b]))
        e.mfree(sid)
    front = nxt
    print("len", d, "states", len(front), flush=True)
    if best: break
if best:
    save_piece(out, p["base"], p["base_k"], p["inputs"] + [norm(b) for b in best], rn=None, parent=src, join_old=kold)
    e.load(p["base"]); run(e, p["inputs"] + best); e.save(f"tw1_{out}_end")
    m = e.ram(0, 0x800)
    d = [(a, m[a], mo[a]) for a in list(range(0x3B5, 0x5B0)) if m[a] != mo[a]]
    print("saved", out, "k end", p["base_k"] + len(p["inputs"]) + len(best), "object-table bytes that differ from the old frame:", " ".join(f"${a:03X}:{x:02x}/{y:02x}" for a, x, y in d))
e.close()

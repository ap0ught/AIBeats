"""TOWER1: build a piece from another piece by appending stretches open-loop, and list what happens.

    python tw1_seq.py <piece> <out piece> <op> [<op> ...]
ops:   old:a:b        the old run's (A12r) inputs with index a..b-1
       tas:a:b        the 1-player TAS's inputs of rows a..b (Left+Right / Up+Down stripped)
       in:N*Btn,...   explicit inputs
       sel:k          add Select to the k-th input from the end of what was appended so far (dice), k >= 1
       cmp:r          print our end state next to the old run's state after its input r (and the object tables' difference)
       rn:r           record that the piece now stands for row r (old or TAS, whatever the next tool is told)
Events printed: landings, hits, enemy spawns / gone, health loss, level byte change. The piece is always saved
(logs/fix/tw1_<out>.json, bookmark tw1_<out>_end)."""
import sys
from tw1_lib import *

src, out, ops = sys.argv[1], sys.argv[2], sys.argv[3:]
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
p = load_piece(src)
e = BizHawk(log_name=f"tw1_seq_{out}.log"); e.load(p["base"]); run(e, p["inputs"])
k = p["base_k"] + len(p["inputs"]); add = []; rn = p.get("rn")
prev = rd(e); print("start", fmt(k, "", prev)[:140])
ev = []

def give(b, tag):
    global prev, k
    e.step(bt(b), 1); k += 1; add.append(norm(b)); s = rd(e)
    en0 = {d[4]: d for d in prev["objs"] if d[0] in (0x5c, 0x62)}; en1 = {d[4]: d for d in s["objs"] if d[0] in (0x5c, 0x62)}
    if prev["z"] != 0 and s["z"] == 0: ev.append(f"{k}[{tag}]:land({s['x']},{s['H']})c{s['cam']}")
    for q, d in en1.items():
        if q not in en0: ev.append(f"{k}[{tag}]:SPAWN{d[0]:02x}({d[1]},{d[2]},hp{d[3]})toad({s['x']},{s['H']})")
        elif d[3] < en0[q][3]: ev.append(f"{k}[{tag}]:HIT{en0[q][3]}->{d[3]}toad({s['x']},{s['H']})en({d[1]},{d[2]})")
    for q, d in en0.items():
        if q not in en1: ev.append(f"{k}[{tag}]:GONE{d[0]:02x}")
    if s["faces"] != prev["faces"]: ev.append(f"{k}[{tag}]:FACE{'+' if s['faces'] else '-'}c{s['cam']}")
    if s["an"] in (94, 95, 96) and prev["an"] not in (94, 95, 96): ev.append(f"{k}[{tag}]:POLE({s['x']},{s['H']})")
    if s["an"] not in (94, 95, 96) and prev["an"] in (94, 95, 96): ev.append(f"{k}[{tag}]:OFFPOLE")
    if s["hp"] < prev["hp"]: ev.append(f"{k}[{tag}]:HURT{s['hp']}")
    if s["lvl"] != prev["lvl"]: ev.append(f"{k}[{tag}]:LEVEL{s['lvl']}")
    prev = s

for op in ops:
    kind, _, rest = op.partition(":")
    if kind == "old":
        a, b = (int(v) for v in rest.split(":"))
        for i in range(a, b): give(A[i], f"o{i}")
        rn = b
    elif kind == "tas":
        a, b = (int(v) for v in rest.split(":"))
        for r in range(a, b + 1):
            v = set(bt(tasin(r)))
            if "Left" in v and "Right" in v: v -= {"Left", "Right"}
            if "Up" in v and "Down" in v: v -= {"Up", "Down"}
            v.discard("Start")
            give("+".join(sorted(v, key=ORDER.index)), f"t{r}")
        rn = b + 1
    elif kind == "in":
        for part in rest.split(","):
            n, b = part.split("*")
            for _ in range(int(n)): give(b, "in")
    elif kind == "land":                                       # land:Btn  = hold Btn until the toad stands on something (max 60)
        for _ in range(60):
            if prev["z"] == 0: break
            give(rest, "land")
    elif kind == "sel":
        # re-run with Select on that frame: rebuild from the piece
        idx = len(add) - int(rest)
        seq = list(add); seq[idx] = norm(seq[idx] + "+Select")
        e.load(p["base"]); run(e, p["inputs"]); k = p["base_k"] + len(p["inputs"]); add = []; ev.append(f"[Select put on appended input {idx}; replayed]")
        prev = rd(e)
        for b in seq: give(b, "re")
    elif kind == "cmp":
        r = int(rest); mo = buf[(r + 1) * 2048:(r + 2) * 2048]; o = rdm(mo); m = e.ram(0, 0x800)
        d = [(a, m[a], mo[a]) for a in range(0x3B5, 0x5B0) if m[a] != mo[a]]
        print(f"cmp old row {r}: ours x={prev['x']} H={prev['H']} z={prev['z']} an={prev['an']} spd={prev['spd']} sub={prev['sub']} cam={prev['cam']} t={prev['t']} f={prev['face']} | "
              f"old x={o['x']} H={o['H']} z={o['z']} an={o['an']} spd={o['spd']} sub={o['sub']} cam={o['cam']} t={o['t']} f={o['face']} | parity {'even' if not (prev['t'] - o['t']) & 1 else 'ODD'} | "
              f"G={r + 1 - k}")
        print("   table bytes that differ:", " ".join(f"${a:03X}:{x:02x}/{y:02x}" for a, x, y in d)[:600])
    elif kind == "rn":
        rn = int(rest)
print("events:", " ".join(ev))
print("end", fmt(k, "", prev)[:150], "| hp", prev["hp"], "lives", prev["lives"])
assert not any(banned(b) for b in add)
save_piece(out, p["base"], p["base_k"], p["inputs"] + add, rn=rn, parent=src)
e.save(f"tw1_{out}_end")
e.close()

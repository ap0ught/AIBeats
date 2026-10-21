"""TOWER1: the cam-4458 Hornhead with a ground kick first (750) and the big boot (5,000), from piece st2 cut before the
TAS's air kick. Stage 1 = fly on with Right, land, one release frame, Right+B (hit 18 frames after the cut).
Stage 2 scan: wait d, tap/gap, run n frames toward the Hornhead, dir+B (the boot) -> kill (+5000). Saves the piece
with the earliest kill, then idles until the toad stands free.   python tw1_e2b.py <out>"""
import sys
from tw1_lib import *
out = sys.argv[1]
p = load_piece("st2"); ins = p["inputs"]
k = p["base_k"]; cut = None
for i, b in enumerate(ins):
    if k >= 1520 and "B" in bt(b): cut = i; break
    k += 1
e = BizHawk(log_name="tw1_e2b.log"); e.load(p["base"]); run(e, ins[:cut])
def sc(m): return int("".join(str(m[0x5F4 + i] & 15) for i in range(6)))
def horn(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x5c: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q])
s1 = []
n = 0
while True:
    mm = e.ram(0, 0x800)
    if mm[0x475] == 0 and n > 0: break
    e.step(bt("Right"), 1); s1.append("Right"); n += 1
for b in ["", "Right+B"]: e.step(bt(b), 1); s1.append(b)
sc0 = sc(e.ram(0, 0x800)); j = 0
while sc(e.ram(0, 0x800)) == sc0 and j < 30: e.step((), 1); s1.append(""); j += 1
mm = e.ram(0, 0x800); print("hit 1 after", len(s1), "frames: +", sc(mm) - sc0, "toad", mm[0x3FD] | mm[0x3EE] << 8, "horn", horn(mm))
root = e.msave()
# the Hornhead's path if the toad just stands
path = []
for j in range(90):
    e.step((), 1); mm = e.ram(0, 0x800); path.append((j + 1, mm[0x3FD] | mm[0x3EE] << 8, mm[0x3B5], horn(mm), mm[0x51A]))
print("idle after the hit (frame, toad x, anim, Hornhead, toad hp):")
for q in path[::3]: print("  ", q)
res = []
for d in range(0, 80, 1):
    for D in ("Left",):
      for stut in (0, 1, 2):
        for n in range(1, 20):
            e.mload(root)
            seq = [""] * d + [D, ""] + [D, ""] * stut + [D] * n + [D + "+B"]
            base = sc(e.ram(0, 0x800)); kill = None
            for j, b in enumerate(seq + [""] * 45):
                e.step(bt(b), 1); mm = e.ram(0, 0x800)
                if mm[0x51A] < 47: break
                h = horn(mm)
                if h and h[2] == 0 and sc(mm) - base == 5000: kill = j + 1; break
            if kill: res.append((kill, d, D, n, stut))
res.sort()
print(len(res), "boots kill; best:", res[:10])
if res:
    kill, d, D, n, stut = res[0]
    e.mload(root); seq = [""] * d + [D, ""] + [D, ""] * stut + [D] * n + [D + "+B"]
    seq += [""] * (kill - len(seq))
    run(e, seq)
    # idle until the toad stands free (anim 1 on the ground) - the body may still fly
    j = 0
    while True:
        mm = e.ram(0, 0x800)
        if mm[0x475] == 0 and mm[0x3B5] == 1: break
        e.step((), 1); seq.append(""); j += 1
        if j > 120: break
    s = rdm(mm); full = ins[:cut] + s1 + seq
    kk = p["base_k"] + len(full)
    print(f"kill {kill} frames after hit 1; toad free at k={kk}: x={s['x']} H={s['H']} facing {s['face']} cam={s['cam']} t={s['t']} score {sc(mm)} horn {horn(mm)}")
    save_piece(out, p["base"], p["base_k"], [norm(b) for b in full], rn=None, parent="st2")
    e.save(f"tw1_{out}_end")
e.close()

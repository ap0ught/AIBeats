"""L12h: run an explicit input script from a base and print the track.
    python l12h_try.py <base bookmark> <base k> <prefix piece or -> <script> [every]
script = comma-separated runs "N*Buttons" (e.g. "32*,25*A,3*Right+A"); prefix '-' = none, 'G:a' = L12g inputs [base k:a]"""
import sys
from l12h_lib import *
bm, k0, pre, script = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]; every = int(sys.argv[5]) if len(sys.argv) > 5 else 1
e = BizHawk(log_name="fix_l12h_try.log"); e.load(bm); k = k0
if pre.startswith("G:"):
    G = seg("L12g"); a = int(pre[2:]); run(e, G[k0:a]); k = a
elif pre != "-":
    p = load_piece(pre); run(e, p["inputs"]); k = p["base_k"] + len(p["inputs"])
seq = []
for part in script.split(","):
    n, b = part.split("*"); seq += [b] * int(n)
for i, b in enumerate(seq):
    e.step(bt(b), 1); k += 1; s = rd(e)
    if i % every == 0 or not alive(s):
        print(k, f"{b:9s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} sub={s['sub']} cam={s['cam']} hp={s['hp']} f{s['faces']}w{s['wind']} |", " ".join(f"{d[0]:02x}:{d[1]},{d[2]}" for d in s["objs"] if d[0] in (0x36, 0x34, 0x5c, 0x62, 0x5f)), flush=True)
    if not alive(s): print("DEAD"); break
e.close()

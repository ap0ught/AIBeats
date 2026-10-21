"""TOWER1: run an explicit input script from an A12r frame and print the track.
    python tw1_try.py <k0> <script> [every]     script = comma-separated runs "N*Buttons" (e.g. "32*,25*A,3*Right+A")
    k0 may be 'P:<piece>' to start at the end of a tw1 piece (logs/fix/tw1_<piece>.json)."""
import sys
from tw1_lib import *
src, script = sys.argv[1], sys.argv[2]; every = int(sys.argv[3]) if len(sys.argv) > 3 else 1
A = seg("A12r")
e = BizHawk(log_name="tw1_try.log")
if src.startswith("P:"):
    p = load_piece(src[2:]); e.load(p["base"]); run(e, p["inputs"]); k = p["base_k"] + len(p["inputs"])
else:
    k0 = int(src); b0 = (k0 // 250) * 250
    e.load(f"tw1_a_f{b0}"); run(e, A[b0:k0]); k = k0
seq = []
for part in script.split(","):
    n, b = part.split("*"); seq += [b] * int(n)
s = rd(e); print(fmt(k, "(start)", s))
for i, b in enumerate(seq):
    e.step(bt(b), 1); k += 1; s = rd(e)
    if i % every == 0 or not alive(s):
        print(fmt(k, b, s), flush=True)
    if not alive(s): print("DEAD"); break
e.close()

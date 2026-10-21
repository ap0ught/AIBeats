"""TOWER1: append an explicit input script to a piece -> new piece standing for TAS row <rn-1>.
    python tw1_append.py <piece> <script 'N*Btn,...'> <rn> <out>"""
import sys
from tw1_lib import *
p = load_piece(sys.argv[1]); script, rn, out = sys.argv[2], int(sys.argv[3]), sys.argv[4]
seq = []
for part in script.split(","):
    n, b = part.split("*"); seq += [norm(b)] * int(n)
assert not any(banned(b) for b in seq)
e = BizHawk(log_name="tw1_append.log"); e.load(p["base"]); run(e, p["inputs"] + seq)
s = rd(e); t = rdm(tasrow(rn - 1))
print("piece end k", p["base_k"] + len(p["inputs"]) + len(seq), fmt(0, "", s)[:120])
print("TAS row", rn - 1, f"x={t['x']} H={t['H']} z={t['z']} an={t['an']} spd={t['spd']} cam={t['cam']} t={t['t']}", "| t parity diff", (s["t"] - t["t"]) & 1)
save_piece(out, p["base"], p["base_k"], p["inputs"] + seq, rn=rn, parent=sys.argv[1])
e.close()

"""L12h: replay a piece from its base and print the track for frames a..b (optionally side by side with the TAS rows at f = k + off).
    python l12h_show.py <piece> <a> <b> [tasoff]"""
import sys
from l12h_lib import *
p = load_piece(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3]); toff = int(sys.argv[4]) if len(sys.argv) > 4 else None
T = tas() if toff is not None else None
e = BizHawk(log_name="fix_l12h_show.log"); e.load(p["base"]); k = p["base_k"]
for inp in p["inputs"]:
    e.step(bt(inp), 1); k += 1
    if a <= k <= b:
        s = rd(e)
        line = f"{k} {inp or '-':9s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} cam={s['cam']} t={s['t']} f{s['faces']}w{s['wind']} | " + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in s["objs"] if d[0] in (0x36, 0x34, 0x5c, 0x62))
        if T is not None and (k + toff) in T:
            t = T[k + toff]; line += f"  || TAS {k + toff} {t['p']:6s} x={t['x']} h={t['h']} z={t['z']} an={t['an']} cam={t['camy']} " + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in t["objs"] if d[0] in (0x36, 0x34, 0x5c, 0x62))
        print(line)
    if k > b: break
print("piece length", len(p["inputs"]), "ends at", p["base_k"] + len(p["inputs"]))
e.close()

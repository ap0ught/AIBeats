"""TOWER1: replay a tw1 piece and print ours vs the TAS rows side by side for a window.
    python tw1_show.py <piece> <our k from> <our k to> [tas offset = k - r]"""
import sys
from tw1_lib import *
p = load_piece(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3]); off = int(sys.argv[4]) if len(sys.argv) > 4 else None
e = BizHawk(log_name="tw1_show.log"); e.load(p["base"]); k = p["base_k"]
for i, inp in enumerate(p["inputs"]):
    e.step(bt(inp), 1); k += 1
    if a <= k <= b:
        s = rd(e)
        line = f"{k} {inp:12s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} sub={s['sub']} cam={s['cam']} t={s['t']} rng={s['rng']} |" + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in s["objs"] if d[0] in (0x5c, 0x62, 0x36))
        if off is not None:
            t = rdm(tasrow(k - off))
            line += f"  || TAS {k - off} {tasin(k - off):10s} x={t['x']} H={t['H']} z={t['z']} an={t['an']} spd={t['spd']} sub={t['sub']} rng={t['rng']} |" + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in t["objs"] if d[0] in (0x5c, 0x62, 0x36))
        print(line)
    if k > b: break
e.close()

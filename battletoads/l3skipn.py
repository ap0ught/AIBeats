"""Tunnel skip from the new gauntlet arrival L3n_f4: depth to 218, 12-frame run-in, TAS roll-back taps, then vary the
dive frame (nleft) and an idle offset before TAS #5093's post-respawn inputs; keep the first that spawns 0x7F and
ends the level. Writes logs/pbeam_L3skipn.json (bookmark L3n_f4) and L3skipn_end."""
import json, sys
from toads.emulator import BizHawk
from skip3_tas import tas_seq
from l3skip import conv
rows = {}
for ln in open("tas/ram_skip_1p.txt"):
    f, b, _ = ln.split(); rows[int(f[1:])] = b
post = [conv(rows[f]) for f in range(14852, 15320)]
e = BizHawk(log_name="l3skipn.log")
found = None
for nleft in range(24, 44, 2):
    for pidle in range(0, 44, 4):
        e.load("L3n_f4"); ins = []
        for _ in range(30):
            m = e.ram(0, 0x800)
            if abs(m[0x41B] - 218) <= 1: break
            b = "Down" if m[0x41B] < 218 else "Up"; e.step((b,), 1); ins.append(b)
        ok = False
        for b in tas_seq(12, nleft=nleft):
            m = e.ram(0, 0x800)
            if (m[0xB7] | m[0xB8] << 8) < 0x800: ok = True; break
            e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
        if not ok: continue
        for _ in range(pidle): e.step((), 1); ins.append("")
        spawn = None
        for k, b in enumerate(post):
            m = e.ram(0, 0x800)
            if spawn is None and 0x7F in m[0x3C1:0x3D0]: spawn = len(ins)
            if m[0x10] != 3: break
            e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
        lvl = e.byte(0x10)
        print("nleft", nleft, "pidle", pidle, "0x7F at", spawn, "level", lvl, "len", len(ins), flush=True)
        if spawn and lvl != 3 and (found is None or len(ins) < len(found)): found = ins; break
    if found: break
if found:
    json.dump({"bookmark": "L3n_f4", "inputs": found, "note": json.load(open("logs/pbeam_L3skip.json"))["note"]}, open("logs/pbeam_L3skipn.json", "w"))
    e.load("L3n_f4")
    for b in found: e.step(tuple(v for v in b.split("+") if v), 1)
    e.save("L3skipn_end"); print("saved pbeam_L3skipn", len(found), "frames")
else: print("no skip found")
e.close()

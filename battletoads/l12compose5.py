"""Compose the whole new Level 12 (2026-10-04 evening): the chain to the old flagpole drop (pbeam_L12y4 part 1, 6142 frames to old 6705),
old[6705:6773], our fight-9 kill (knowledge/l12_f9_kill0.json), the walk to the standing spot (l12_walk7100.json), the old-route walk
to the top Hornhead's spawn (ow_o2.json[:459], old 7342), our kill + return (fight_h10.json, joins old 7597), the old-route walk to the
level end (ow_o3.json), the old remainder. Replayed from L12_start to verify; -> logs/pbeam_L12v.json (one part: L12_start)."""
import json, os, sys
from toads.emulator import BizHawk, LOGS_DIR
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
y4 = json.load(open(LOGS_DIR / "pbeam_L12y4.json")); n1 = y4["parts"][0]["n"]; part1 = [x.replace(",", "+") for x in y4["inputs"][:n1]]
f9 = json.load(open("knowledge/fight_f9b.json"))["inputs"]                # the better fight 9: returns to the old route at j in 7024..7100
o2 = json.load(open("knowledge/ow_o2c_spawn.json"))["inputs"]                      # the shorter 7100 walk, to the top Hornhead's spawn (old 7342)
h10 = json.load(open("knowledge/fight_h12.json")); assert h10["a"] == 7342
o3 = json.load(open("knowledge/ow_o3c.json")); assert o3["bookmark"] == "F_h12_end"
pole = json.load(open("knowledge/l12_pole4.json")); assert pole["bookmark"] == "OW_o3c_8429"
o3["inputs"] = o3["inputs"][:pole["n_o3"]]                     # o3b up to its old-8429 landing; the pole piece continues from there
pole_ins = pole["inputs"]
o5 = json.load(open("knowledge/ow_o5d.json")); assert o5["bookmark"] == "PL4_hang"
tailfrom = o5["old_at"]
ins = part1 + old[6705:6773] + f9 + o2 + h10["inputs"] + o3["inputs"] + pole_ins + o5["inputs"] + old[tailfrom:]
print("composed", len(ins), "frames (old L12w", len(old), "); o3 reaches old", tailfrom, flush=True)
e = BizHawk(log_name="l12compose3.log"); e.load("L12_start")
end = None
for i, b in enumerate(ins):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if m[0x11] < 4 and end is None: print("LIFE LOST at", i, flush=True); end = ("death", i); break
    if m[0x10] != 5 and end is None: end = ("level", i); print("level byte", m[0x10], "at", i, flush=True); break
m = e.ram(0, 0x800); print("end:", end, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, "lvl", m[0x10], "hp", m[0x51A], "lives", m[0x11], "objs", [hex(m[0x3C1 + q]) for q in range(2, 15) if m[0x3C1 + q]], flush=True)
if end and end[0] == "level":
    e.save("L12v_end"); json.dump({"bookmark": "L12_start", "inputs": ins[:end[1] + 1], "parts": [{"bookmark": "L12_start", "n": end[1] + 1}], "note": w.get("note", "")}, open(LOGS_DIR / "pbeam_L12v.json", "w"))
    print("saved pbeam_L12v.json", end[1] + 1, "frames", flush=True)
e.close()

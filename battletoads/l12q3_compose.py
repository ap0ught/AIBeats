"""Compose L12q3 (2026-10-07): old[:6184] + piece_L12q2 (-> old 7003) + q2_jump (-> old 7071) + OW_q2walk2 (-> old 9247) + old[9247:];
replay from L11r_end0, find the Level-13 set-down, save L12q3_end0, write logs/pbeam_L12q3.json."""
import json
from toads.emulator import BizHawk, LOGS_DIR
old = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L12r.json"))["inputs"]]
piece = json.load(open("knowledge/piece_L12q2.json")); jump = json.load(open("knowledge/q2_jump.json")); walk = json.load(open("knowledge/ow_q2walk2.json"))
assert piece["a"] == 6184 and piece["b"] == 7003 and jump["jump_old"] == 7071 and walk["old_at"] == 9247
ins = old[:6184] + list(piece["inputs"]) + list(jump["inputs"]) + list(walk["inputs"]) + old[9247:]
print("composed", len(ins), "inputs (old", len(old), "); saves", len(old) - len(ins), flush=True)
e = BizHawk(log_name="l12q3_compose.log"); e.load("L11r_end0")
setdown = None; lv13 = None
for i, b in enumerate(ins):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if m[0x10] == 13 and lv13 is None: lv13 = i + 1; print("level byte 13 at input", lv13, flush=True)
    if m[0x10] == 13 and m[0x4B1] == 32 and (m[0x3FD] | m[0x3EE] << 8) == 28 and m[0x439] == 144 and setdown is None:
        setdown = i + 1; print("set down in Armageddon at input", setdown, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "hp", m[0x51A], "lives", m[0x11], flush=True)
        e.save("L12q3_end0"); break
m = e.ram(0, 0x800)
print("end: level", m[0x10], "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "st", m[0x4B1], "lives", m[0x11], "hp", m[0x51A], flush=True)
if setdown:
    seg = ins[:setdown]
    json.dump({"bookmark": "L11r_end0", "inputs": seg, "note": json.load(open(LOGS_DIR / "pbeam_L12r.json")).get("note", ""), "slack": 0}, open(LOGS_DIR / "pbeam_L12q3.json", "w"))
    print("saved logs/pbeam_L12q3.json:", len(seg), "frames (L12r 9420; saves", 9420 - len(seg), ")", flush=True)
else:
    e.save("L12q3_endX"); print("no set-down found; bookmark L12q3_endX at the end", flush=True)
e.close()

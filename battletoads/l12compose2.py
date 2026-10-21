"""Compose the rebuilt Level 12 (2026-10-04): part 1 (logs/pbeam_L12y.json parts[0] = the chain to the record's
3856 landing) + the pole piece + the l12chain3 follow sections (knowledge/l4s_L12_u*.json, in PLAN order) + the
level-end wait and the Start into Armageddon as l12.py does it. One continuous replay from L12_start.
    python l12compose2.py -> logs/pbeam_L12v.json {bookmark: L12_start, inputs}, bookmark L12v_end; prints the end"""
import json, re, sys
from toads.emulator import BizHawk, LOGS_DIR
y = json.load(open(LOGS_DIR / "pbeam_L12y.json")); part1 = y["inputs"][:y["parts"][0]["n"]]
pole = json.load(open("knowledge/l12_pole.json"))["inputs"]
secs = [l for l in open("l12chain3.py") if l.strip().startswith("PLAN") or l.strip().startswith("(")]
import l12chain3_plan as plan   # noqa (the PLAN list, see below)
ins = list(part1) + list(pole)
for extra in ("knowledge/l12_u1.json", "knowledge/l12_col.json", "knowledge/l12_f8_kill0.json", "knowledge/l12_lap.json", "knowledge/ww_w1.json", "knowledge/l12_ww2.json"):   # follow section 1 (+ TAS to 4391), the column climb
    ins += json.load(open(extra))["inputs"]
for i0, i1, foe in plan.PLAN:
    if i0 < 4500: continue
    bm = f"L12_u{i0}" + ("k" if foe else "")
    try: sec = json.load(open(f"knowledge/l4s_{bm}.json"))
    except FileNotFoundError: print("missing section", bm, "- stopping there"); break
    sec = sec["inputs"] if isinstance(sec, dict) else sec
    ins += [""] * 2 + [s.replace(",", "+") for s in sec]      # l12.py: 2 idle frames before every section (the search root)
e = BizHawk(log_name="compose2.log"); e.load("L12_start")
for b in ins: e.step(tuple(v for v in b.split("+") if v), 1)
m = e.ram(0, 0x800); print("after the sections:", len(ins), "frames; toad", (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475]), "level", m[0x10], "lives", m[0x11])
# the level end: idle until the level byte changes (as l12.py), then Start into Armageddon, idle until placement
n0 = len(ins)
for _ in range(2000):
    if e.byte(0x10) != 5: break
    e.step((), 1); ins.append("")
print("level byte left 5 after", len(ins) - n0, "idle frames")
for _ in range(150):
    m = e.ram(0, 0x800)
    if m[0x10] != 5 and m[0x51A] == 47 and m[0x3B5] == 0: break
    e.step(("Start",), 2); ins += ["Start", "Start"]; e.step((), 18); ins += [""] * 18
e.save("L12v_end"); m = e.ram(0, 0x800)
json.dump({"bookmark": "L12_start", "inputs": ins, "note": y.get("note", "")}, open(LOGS_DIR / "pbeam_L12v.json", "w"))
print("L12v:", len(ins), "frames (L12w 10254); end level", m[0x10], "toad", (m[0x3FD] | m[0x3EE] << 8, m[0x439]))
e.close()

"""Compose the new Terra Tubes (2026-10-06): L9c up to index 7852, the bug-free descent (knowledge/l9_bug.json, 120), the entry-matched
crossing (l9_cross_60b.json: 60 idle + 214), the corridor piece (l4s_L9X_corrb.json, 2 idle first), the old-route walk from the old
index given in knowledge/l9_corr_join.json (ow_o9e.json), then the old remainder. Verified from L8c_end0 to the level end.
    -> logs/pbeam_L9t.json (bookmark L8c_end0)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); old = [x.replace(",", "+") for x in seg["inputs"]]
bug = json.load(open("knowledge/l9_bug.json"))["inputs"]; cross = json.load(open("knowledge/l9_cross_60b.json"))["inputs"]
corr = json.load(open("knowledge/l4s_L9X_corrb.json")); corr = corr["inputs"] if isinstance(corr, dict) else corr
o9 = json.load(open("knowledge/ow_o9e.json")); tailfrom = o9["old_at"]
ins = old[:7852] + bug + cross + [""] * 2 + corr + o9["inputs"] + old[tailfrom:]
print("composed", len(ins), "frames (L9c", len(old), ")", flush=True)
e = BizHawk(log_name="l9compose.log"); e.load(seg["bookmark"]); end = None
for i, b in enumerate(ins):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if m[0x11] < 3 and end is None: print("LIFE LOST at", i, flush=True); end = ("death", i); break
    if m[0x10] != 11 and i > 9000: end = ("level", i); print("level byte", m[0x10], "at", i, flush=True); break
m = e.ram(0, 0x800); print("end:", end, "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "lvl", m[0x10], "lives", m[0x11], flush=True)
if end and end[0] == "level":
    # the old segment ended at the Rat Race placement with its own page-skip tail: reuse it after the byte change
    k = next(i for i, b in enumerate(old) if i > 9000 and False) if False else None
    e.save("L9t_end_raw"); json.dump({"bookmark": seg["bookmark"], "inputs": ins[:end[1] + 1], "raw_end": True, "note": seg.get("note", "")}, open(LOGS_DIR / "pbeam_L9t_raw.json", "w"))
    print("saved pbeam_L9t_raw.json", end[1] + 1, "(the page-skip tail is added next)", flush=True)
e.close()

"""Level 12 tail, part 2 (2026-10-04): from OW_o3b's inputs up to the old-8429 landing (the circling platform), scan the wait before the old
inputs (negative = drop the old's leading idles) for the spring launch that hangs on the last pole at (288,4944); then walk the old
route on from the hang.  -> bookmarks OW_o3b_8429, PL3_hang; knowledge/l12_pole3.json {bookmark OW_o3b_8429}, ow_o5c.json"""
import json, re, subprocess, sys
from toads.emulator import BizHawk, LOGS_DIR
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
o3 = json.load(open("knowledge/ow_o3b.json")); ins = o3["inputs"]
n = int(re.search(r"old landing 8429 reached.*?; (\d+) frames", open("logs/l12tail2.txt").read()).group(1))
print("o3b reaches old 8429 after", n, "of its", len(ins), "frames", flush=True)
def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l12tail2b.log"); e.load("F_h11_end")
for b in ins[:n]: e.step(tuple(v for v in b.split("+") if v), 1)
print("at 8429:", toad(e.ram(0, 0x800)), flush=True); e.save("OW_o3b_8429"); base = e.msave(); found = None
j = 8429
lead = 0
while old[j + lead] == "": lead += 1
print("leading idle frames at 8429:", lead, flush=True)
for wv in list(range(-lead, 0, 1)) + list(range(0, 262, 1)):
    if wv < 0 and any(old[s] for s in range(j, j - wv)): continue
    e.mload(base); e.step((), max(wv, 0)); hang = None
    for s in range(j - min(wv, 0), 8900):
        e.step(tuple(v for v in old[s].split("+") if v), 1); m = e.ram(0, 0x800)
        if m[0x11] < 4: break
        if m[0x3B5] == 95: hang = (s + 1, toad(m)); break
    if hang or wv % 10 == 0: print("wait", wv, "->", hang, flush=True)
    if hang and abs(hang[1][0] - 288) <= 3 and abs(hang[1][1] - 4944) <= 3:
        found = wv; e.save("PL3_hang"); json.dump({"bookmark": "OW_o3b_8429", "n_o3b": n, "inputs": [""] * max(wv, 0) + old[j - min(wv, 0):hang[0]], "old_at": hang[0]}, open("knowledge/l12_pole3.json", "w"))
        print("POLE HANG with wait", wv, "at old", hang[0], hang[1], flush=True); break
e.close()
if found is None: print("NO POLE HANG FOUND", flush=True); sys.exit(1)
hj = json.load(open("knowledge/l12_pole3.json"))["old_at"]
subprocess.run([sys.executable, "-u", "oldwalk.py", "PL3_hang", str(hj), "10234", "o5c"], stdout=sys.stdout, stderr=subprocess.STDOUT)
print("tail2b done", flush=True)

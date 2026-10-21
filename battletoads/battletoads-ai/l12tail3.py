"""Level 12 tail on the better fight 9 (2026-10-04 night): waits for fightbeam f9b (joins the old route at j in 7024..7100), then:
F_f9b_end -> oldwalk to 7539 (o2c; stops at the top Hornhead's spawn state at old 7342 = bookmark OW_o2c_spawn) -> fightbeam h12 from it
-> F_h12_end -> oldwalk o3c to 10234 (sticks at the circling platform 8429) -> pole wait scan (PL4_hang) -> oldwalk o5d -> l12compose5.py.
Log: logs/l12tail3.txt"""
import json, os, re, subprocess, sys, time
from toads.emulator import BizHawk, LOGS_DIR
def wait_for(logf, line):
    while not (os.path.exists(logf) and line in open(logf).read()): time.sleep(30)
def run(args, env=None):
    print(">>", " ".join(args), flush=True)
    subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT, env=dict(os.environ, **(env or {})))
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x3B5])
wait_for("logs/fightbeam_f9b.txt", "saved knowledge/fight_f9b.json")
p = json.load(open("knowledge/fight_f9b.json")); print("fight f9b:", len(p["inputs"]), "frames, joins old", p["b"], "(old 6773 ->", p["b"] - 6773, ")", flush=True)
e = BizHawk(log_name="l12tail3.log"); e.load("PJ_6773")
for b in p["inputs"]: e.step(tuple(v for v in b.split("+") if v), 1)
e.save("F_f9b_end"); e.close()
run(["oldwalk.py", "F_f9b_end", str(p["b"]), "7539", "o2c"])
o2 = json.load(open("knowledge/ow_o2c.json"))
e = BizHawk(log_name="l12tail3b.log"); e.load("F_f9b_end"); k = None
for i, b in enumerate(o2["inputs"]):
    e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
    if any(m[0x3C1 + q] == 0x62 for q in range(2, 15)): k = i + 1; break
print("top Hornhead spawns at o2c frame", k, "toad", toad(e.ram(0, 0x800)), flush=True); e.save("OW_o2c_spawn"); e.close()
json.dump({"bookmark": "F_f9b_end", "inputs": o2["inputs"][:k], "old_at": 7342}, open("knowledge/ow_o2c_spawn.json", "w"))
run(["fightbeam.py", "L12w", "7342", "7588-7700", "62", "h12"], {"FB_START": "OW_o2c_spawn", "FB_CAMTOL": "1", "FB_WIDTH": "4", "FB_WAIT": "90", "FB_WAIT1": "260", "FB_RETDEPTH": "60"})
h = json.load(open("knowledge/fight_h12.json")); print("fight h12:", len(h["inputs"]), "joins old", h["b"], flush=True)
e = BizHawk(log_name="l12tail3c.log"); e.load("OW_o2c_spawn")
for b in h["inputs"]: e.step(tuple(v for v in b.split("+") if v), 1)
e.save("F_h12_end"); e.close()
run(["oldwalk.py", "F_h12_end", str(h["b"]), "10234", "o3c"])
o3 = json.load(open("knowledge/ow_o3c.json")); j = o3["old_at"]; print("o3c stops at old", j, flush=True)
txt = open("logs/l12tail3.txt").read()
n = int(re.search(r"old landing 8429 reached.*?; (\d+) frames", txt).group(1)) if "old landing 8429 reached" in txt else None
if j >= 10208 or n is None: print("unexpected stop", j, n, flush=True); sys.exit(1)
e = BizHawk(log_name="l12tail3d.log"); e.load("F_h12_end")
for b in o3["inputs"][:n]: e.step(tuple(v for v in b.split("+") if v), 1)
e.save("OW_o3c_8429"); base = e.msave(); found = None; j = 8429; lead = 0
while old[j + lead] == "": lead += 1
for wv in list(range(-lead, 0, 1)) + list(range(0, 262, 1)):
    e.mload(base); e.step((), max(wv, 0)); hang = None
    for s in range(j - min(wv, 0), 8900):
        e.step(tuple(v for v in old[s].split("+") if v), 1); m = e.ram(0, 0x800)
        if m[0x11] < 4: break
        if m[0x3B5] == 95: hang = (s + 1, toad(m)); break
    if hang and abs(hang[1][0] - 288) <= 3 and abs(hang[1][1] - 4944) <= 3:
        found = wv; e.save("PL4_hang"); json.dump({"bookmark": "OW_o3c_8429", "n_o3": n, "inputs": [""] * max(wv, 0) + old[j - min(wv, 0):hang[0]], "old_at": hang[0]}, open("knowledge/l12_pole4.json", "w"))
        print("POLE HANG with wait", wv, "at old", hang[0], flush=True); break
e.close()
if found is None: print("NO POLE HANG", flush=True); sys.exit(1)
run(["oldwalk.py", "PL4_hang", str(json.load(open("knowledge/l12_pole4.json"))["old_at"]), "10234", "o5d"])
run(["l12compose5.py"])
print("tail3 done", flush=True)

"""Level 12 tail on the shorter 7100 walk (2026-10-04 evening): waits for the top-Hornhead fight from OW_o2b_spawn (fightbeam h11), then
runs the chain: F_h11_end -> oldwalk to the level end; where that sticks at the circling platform (old 8429 -> 8711) do the
pole wait scan (drop 2.. of the old's idle frames so the spring launch flies to the last pole) and walk on from the hang.
    python l12tail2.py  -> knowledge/ow_o3b.json, l12_pole3.json, ow_o5c.json; then l12compose4.py composes."""
import json, os, re, subprocess, sys, time
from toads.emulator import BizHawk, LOGS_DIR
while not os.path.exists("knowledge/fight_h11.json") or "saved knowledge/fight_h11.json" not in open("logs/fightbeam_h11.txt").read():
    time.sleep(30)
p = json.load(open("knowledge/fight_h11.json")); print("fight h11:", len(p["inputs"]), "frames, joins old", p["b"], flush=True)
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
e = BizHawk(log_name="l12tail2.log"); e.load("OW_o2b_spawn")
for b in p["inputs"]: e.step(tuple(v for v in b.split("+") if v), 1)
e.save("F_h11_end"); e.close()
def run(args):
    print(">>", " ".join(args), flush=True); subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT)
run(["oldwalk.py", "F_h11_end", str(p["b"]), "10234", "o3b"])
o3 = json.load(open("knowledge/ow_o3b.json")); j = o3["old_at"]; print("o3b stops at old", j, flush=True)
if j < 10208:
    # the pole: from the OW_o3b state at old j (expected 8429) scan the wait (negative = drop the old's leading idles) for the hang on the last pole
    def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x3B5])
    e = BizHawk(log_name="l12tail2b.log"); e.load("OW_o3b"); base = e.msave(); found = None
    lead = 0
    while old[j + lead] == "": lead += 1
    for wv in list(range(-(lead - lead % 2), 0, 2)) + list(range(0, 80, 1)):
        e.mload(base); e.step((), max(wv, 0)); hang = None
        for s in range(j - min(wv, 0), j + 460):
            e.step(tuple(v for v in old[s].split("+") if v), 1); m = e.ram(0, 0x800)
            if m[0x11] < 4: break
            if m[0x3B5] == 95: hang = (s + 1, toad(m)); break
        if hang and abs(hang[1][0] - 288) <= 3 and abs(hang[1][1] - 4944) <= 3:
            found = wv; e.save("PL3_hang"); json.dump({"bookmark": "OW_o3b", "inputs": [""] * max(wv, 0) + old[j - min(wv, 0):hang[0]], "old_at": hang[0]}, open("knowledge/l12_pole3.json", "w"))
            print("pole hang with wait", wv, "at old", hang[0], hang[1], flush=True); break
    e.close()
    if found is None: print("NO POLE HANG FOUND", flush=True); sys.exit(1)
    hj = json.load(open("knowledge/l12_pole3.json"))["old_at"]
    run(["oldwalk.py", "PL3_hang", str(hj), "10234", "o5c"])
print("tail2 done", flush=True)

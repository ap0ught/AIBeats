"""Level 4's tail from the two faster pieces (2026-10-03): old[:3860] + W1 + W2b, then the checkpoint-7 closed loop
(l4cp7b.py) and the lift/warp search (l4s.py l4warp) re-run from the new arrival, then the Start mash into Karnath.
    python l4rebuild.py   -> logs/pbeam_L4w.json (bookmark L3skipu_end_r)"""
import json, subprocess, sys, os
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
old = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L4n3.json"))["inputs"]]
w1 = json.load(open("knowledge/short_L4w1.json")); w2 = json.load(open("knowledge/short_L4w2.json"))
assert w1["a"] == 3860 and w2["a"] == w1["b"], (w1["a"], w1["b"], w2["a"])
ins = old[:3860] + list(w1["inputs"]) + list(w2["inputs"])
e = BizHawk(log_name="l4rebuild.log"); e.load("L3skipu_end_r")
for x in ins: e.step(tuple(v for v in x.split("+") if v), 1)
m = e.ram(0, 0x800); print("arrival at cp7:", len(ins), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "cp", m[0x585], flush=True)
e.save("L4w_plats"); e.close()
if not (PROJECT / "knowledge" / "l4_cp7w_inputs.json").exists():
    subprocess.run([sys.executable, "l4cp7b.py", "L4w_plats"], cwd=PROJECT, stdout=open(LOGS_DIR / "l4cp7w.txt", "w"), stderr=subprocess.STDOUT)
    os.replace(PROJECT / "knowledge" / "l4_cp7b_inputs.json", PROJECT / "knowledge" / "l4_cp7w_inputs.json")
    os.replace(PROJECT / "knowledge" / "l4_cp7b_inputs.bak.json", PROJECT / "knowledge" / "l4_cp7b_inputs.json")
cp7 = json.load(open("knowledge/l4_cp7w_inputs.json")); print("cp7:", len(cp7), "frames (old 669)", flush=True)
if not (PROJECT / "knowledge" / "l4s_L4w_cp7b.json").exists():
    subprocess.run([sys.executable, "l4s.py", "L4w_cp7b", "770", "-125", "400", "l4warp"], cwd=PROJECT, stdout=open(LOGS_DIR / "l4s_L4w_cp7b.txt", "w"), stderr=subprocess.STDOUT)
warp = json.load(open("knowledge/l4s_L4w_cp7b.json")); print("warp:", len(warp), "frames (old 410)", flush=True)
ins += cp7 + [""] * 2 + warp
e = BizHawk(log_name="l4rebuild.log"); e.load("L3skipu_end_r")
for x in ins: e.step(tuple(v for v in x.split("+") if v), 1)
m = e.ram(0, 0x800)
assert (m[0x23], m[0x24]) == (0x0D, 0xE5), "warp not engaged"
for _ in range(80):
    m = e.ram(0, 0x800)
    if m[0x10] == 8 and m[0x51A] == 47: break
    for b in ["Start"] * 2 + [""] * 18:
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
for _ in range(30): e.step((), 1); ins.append("")
m = e.ram(0, 0x800); print("Karnath:", len(ins), "frames (old 5499); lvl", m[0x10], "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], flush=True)
e.save("L4w_end"); e.close()
json.dump({"bookmark": "L3skipu_end_r", "inputs": ins, "note": json.load(open(LOGS_DIR / "pbeam_L4n3.json")).get("note", "")}, open(LOGS_DIR / "pbeam_L4w.json", "w"))

"""Build the respawn states (pointer in RAM) for each working dive timing from L3n_f4 and run an ENDOBJ (0x7F) beam
search from each; the first solved one becomes logs/pbeam_L3skipn.json."""
import json, os, subprocess
from toads.emulator import BizHawk
from skip3_tas import tas_seq
e = BizHawk(log_name="l3skipn.log")
pre = {}
for nleft in range(32, 44, 2):
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
    if ok:
        m = e.ram(0, 0x800); print("nleft", nleft, "respawn: 0B", m[0x0B], "0C", m[0x0C], "toad", m[0x3FD]|m[0x3EE]<<8, m[0x41B], "len", len(ins), flush=True)
        e.save(f"L3n_resp{nleft}"); pre[nleft] = ins
e.close()
env = dict(os.environ, L4S_ENDOBJ="7F", L4S_LVL="3", L4S_HPMIN="15", L4S_MACRO="4")
for nleft, ins in pre.items():
    r = subprocess.run(["python", "l4s.py", f"L3n_resp{nleft}", "0", "0", "300", "reach"], env=env, capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if "GOAL" in l or "solved" in l or "died" in l or "unsolved" in l]
    print("nleft", nleft, tail[-2:], flush=True)
    if any("GOAL" in l for l in tail):
        sol = json.load(open(f"knowledge/l4s_L3n_resp{nleft}.json"))
        full = ins + ["", ""] + sol
        e = BizHawk(log_name="l3skipn.log"); e.load("L3n_f4")
        for b in full: e.step(tuple(v for v in b.split("+") if v), 1)
        for _ in range(200):
            if e.byte(0x10) != 3: break
            e.step((), 1); full.append("")
        print("level after:", e.byte(0x10), "total", len(full), flush=True)
        if e.byte(0x10) != 3:
            json.dump({"bookmark": "L3n_f4", "inputs": full, "note": json.load(open("logs/pbeam_L3skip.json"))["note"]}, open("logs/pbeam_L3skipn.json", "w"))
            e.save("L3skipn_end"); print("saved pbeam_L3skipn", flush=True); e.close(); break
        e.close()

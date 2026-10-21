"""Terra Tubes corridor by repair-and-walk (2026-10-06): from a bookmark at old index j, walk the old route (oldwalk2); where it sticks before
landing jN, run a short height-dominant beam (l9cross.py MODE=down, XTOL 3) from the stuck bookmark to the old's landing state at jN, then
walk on from there. Repeats until the old route's end or a failed repair. Pieces: knowledge/l9chain_<k>.json; the final bookmark L9CH_end."""
import json, os, re, subprocess, sys
from toads.emulator import BizHawk, LOGS_DIR
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); old = [x.replace(",", "+") for x in seg["inputs"]]
bm, j = sys.argv[1], int(sys.argv[2]); pieces = []; k = 0
def run(args, env=None, log=None):
    f = open(log, "w") if log else None
    subprocess.run([sys.executable, "-u"] + args, stdout=f or sys.stdout, stderr=subprocess.STDOUT, env=dict(os.environ, **(env or {})))
    if f: f.close()
e = BizHawk(log_name="l9chain.log")
while k < 30:
    out = f"ch{k}"; run(["oldwalk2.py", "L9c", seg["bookmark"], "0", bm, str(j), str(len(old)), out], log=f"logs/oldwalk_{out}.txt")
    w = json.load(open(f"knowledge/ow_{out}.json")); txt = open(f"logs/oldwalk_{out}.txt").read()
    pieces.append({"bookmark": bm, "inputs": w["inputs"], "old_from": j, "old_to": w["old_at"]}); print(f"walk {k}: {len(w['inputs'])} frames, old {j} -> {w['old_at']}", flush=True)
    j = w["old_at"]; bm = f"OW_{out}"
    m = re.search(r"STUCK: no wait reaches old landing (\d+)", txt)
    if not m: print("walked to the end", flush=True); break
    jn = int(m.group(1))
    e.load(seg["bookmark"])
    for b in old[:jn]: e.step(tuple(v for v in b.split("+") if v), 1)
    r = e.ram(0, 0x800); gx, gh, ghh = r[0x3FD] | r[0x3EE] << 8, r[0x439], r[0x42A]
    print(f"repair {k}: to old {jn} landing ({gx},{gh},{ghh})", flush=True)
    run(["l9cross.py"], env={"MODE": "down", "ROOT": bm, "GX": str(gx), "GH": str(gh), "GHH": str(ghh), "HPMIN": "31", "W": "400", "STEPS": "80", "XTOL": "3", "OUT": f"rep{k}"}, log=f"logs/l9cross_rep{k}.txt")
    pj = f"knowledge/l9_cross_0rep{k}.json"
    if not os.path.exists(pj): print("repair failed at", jn, flush=True); break
    p = json.load(open(pj)); pieces.append({"bookmark": bm, "inputs": p["inputs"], "old_from": j, "old_to": jn, "repair": True}); print(f"   repaired in {len(p['inputs'])} frames", flush=True)
    bm, j = f"L9X_corrrep{k}", jn; k += 1
e.close()
json.dump(pieces, open("knowledge/l9chain_pieces.json", "w")); print("chain done; last old index", j, "pieces", len(pieces), flush=True)

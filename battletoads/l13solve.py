"""Armageddon re-searched on a new route (2026-10-03): the queen's moves are random, so the old fight never re-fits.
Three l4s.py 'ctr' sections like the first time (hit counter $586 to 180, to 240, then her object gone), then idle
through the ending until the level byte leaves 13.
    python l13solve.py <entry bookmark> <idle frames first> <out>   -> logs/pbeam_<out>.json (bookmark = entry)"""
import json
import os
import subprocess
import sys

from toads.emulator import BizHawk, LOGS_DIR, PROJECT

entry, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
e = BizHawk(log_name=f"l13solve_{out}.log")
e.load(entry)
ins = [""] * k
e.step((), k)
secs = [("f1", {"L4S_CTRGOAL": "180"}), ("f2", {"L4S_CTRGOAL": "240"}), ("f3", {"L4S_CTRGOAL": "999", "L4S_FOEGONE": "1"})]
for name, extra in secs:
    bm = f"{out}_{name}"
    e.save(bm)
    js = PROJECT / "knowledge" / f"l4s_{bm}.json"
    if not js.exists():
        env = dict(os.environ, L4S_CTR="586", L4S_LVL="13", L4S_FOEID="0x7e", L4S_AIRB="1", L4S_STEPS="500", L4S_SAFE="20", **extra)
        with open(LOGS_DIR / f"l4s_{bm}.txt", "w") as f:
            subprocess.run([sys.executable, "l4s.py", bm, "0", "0", os.environ.get("L13_WIDTH", "400"), "ctr"], cwd=PROJECT, env=env, stdout=f, stderr=subprocess.STDOUT)
        if not js.exists():
            print(name, "unsolved; see logs/l4s_" + bm + ".txt", flush=True)
            e.close()
            sys.exit(1)
    sec = json.loads(js.read_text())
    e.load(bm)
    e.step((), 2)
    ins += [""] * 2
    for b in sec:
        e.step(tuple(v for v in b.split("+") if v), 1)
        ins.append(b)
    m = e.ram(0, 0x800)
    print(f"{name}: {len(sec)} frames -> input {len(ins)}, counter {m[0x586]}, hp {m[0x51A]}, queen {[m[0x51A + s] for s in range(2, 15) if m[0x3C1 + s] == 0x7E]}", flush=True)
for _ in range(2500):
    if e.byte(0x10) != 13:
        break
    e.step((), 1)
    ins.append("")
m = e.ram(0, 0x800)
print(f"level byte left 13 at input {len(ins)} (old segment 2680); level {m[0x10]}", flush=True)
e.save(out + "_end")
json.dump({"bookmark": entry, "inputs": ins, "note": "ARMAGEDDON: the Dark Queen - 21 hits (RAM $586 counts 12 per hit; the 21st kills), no damage taken, "
           "then the ending plays by itself.||" f"{len(ins)} frames"}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
e.close()

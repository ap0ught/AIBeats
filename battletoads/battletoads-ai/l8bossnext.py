"""Continue a boss search from the best line of a previous one: replay knowledge/l4s_<bm>_best.json (or the solved
json) from <bm>, save the endpoint as <bm>2 and start a new boss search there.   python l8bossnext.py <bm> [width]"""
import json, os, subprocess, sys
from toads.emulator import BizHawk, PROJECT
bm = sys.argv[1]; width = sys.argv[2] if len(sys.argv) > 2 else "600"
src = PROJECT / "knowledge" / f"l4s_{bm}_best.json"
ins = json.loads(src.read_text())
e = BizHawk(log_name=f"l8bossnext_{bm}.log"); e.load(bm); e.step((), 2)
for s in ins:
    e.step(tuple(b for b in s.split("+") if b), 1)
r = e.ram_all()
print(f"{bm}: {len(ins)} frames, score {r[0x5F4]}{r[0x5F5]}{r[0x5F6]}000, toad {r[0x3FD] + 256 * r[0x3EE]} hp {r[0x51A]}, boss",
      [(r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x7d], flush=True)
e.save(f"{bm}2"); e.close()
env = dict(os.environ, L4S_LVL="7", L4S_SAFE="30", L4S_STEPS=os.environ.get("L4S_STEPS", "300"))
with open(PROJECT / "logs" / f"l4s_{bm}2.txt", "w") as f:
    subprocess.run([sys.executable, "l4s.py", f"{bm}2", "0", "0", width, "boss"], cwd=PROJECT, env=env, stdout=f, stderr=subprocess.STDOUT)
print((PROJECT / "logs" / f"l4s_{bm}2.txt").read_text().splitlines()[-1][:160])

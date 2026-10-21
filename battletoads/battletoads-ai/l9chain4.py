"""Terra Tubes chain with a bob-wait at x 22 right after the wall jump (safe, not absorbed by later descents):
   python l9chain4.py <W frames> <suffix>
   sections: L9_j<sfx> (bob wait) -> L9_s1<sfx> -> L9_s2<sfx> (band) -> L9_s3<sfx> (follow 375-700) -> L9_s4<sfx> (follow 700-1130)"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from toads.emulator import BizHawk
P = Path(__file__).parent
W, sfx = int(sys.argv[1]), sys.argv[2]
j = f"L9_j{sfx}"; s1 = f"L9_s1{sfx}"; s2 = f"L9_s2{sfx}"; s3 = f"L9_s3{sfx}"; s4 = f"L9_s4{sfx}"
ins = ["A" if k % 4 == 0 else "" for k in range(W)]
(P / "knowledge" / f"l4s_{j}.json").write_text(json.dumps(ins))
e = BizHawk(log_name=f"chain4_{sfx}.log"); e.load("L9_s1cut_solved"); e.step((), 2)      # past the wall, in the water at x 22
for s in ins:
    e.step(tuple(b for b in s.split("+") if b), 1)
r = e.ram_all(); print(f"{j}: after the bob wait x {r[0x3FD] + 256 * r[0x3EE]} raw h {r[0x439]} an {r[0x3B5]} hp {r[0x51A]}", flush=True)
e.save(f"{j}_solved"); e.close()
shutil.copy(P / "states" / "L9_s1cut_solved.State", P / "states" / f"{j}.State")
def hroot(secs):
    out = subprocess.run([sys.executable, "l9.py", *secs], cwd=P, capture_output=True, text=True).stdout
    return int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
def search(bm, prev, args, extra):
    shutil.copy(P / "states" / f"{prev}_solved.State", P / "states" / f"{bm}.State")
    env = dict(os.environ, L4S_LVL="11", L4S_SAFE="20", L4S_ACTS="swim", **extra)
    with open(P / "logs" / f"l4s_{bm}.txt", "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, *args], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = (P / "logs" / f"l4s_{bm}.txt").read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved"))][-1:], flush=True)
    return "unsolved" not in txt
h = hroot(["L9_s1cut", j]); print(f"{j}: H {h}", flush=True)
if not search(s1, j, ["40", str(-590 - h), "600", "reach_down_left_w"], {"L4S_STEPS": "120"}): sys.exit()
h = hroot(["L9_s1cut", j, s1])
if not search(s2, s1, ["180", str(-650 - h), "400", "reach_band_w"], {"L4S_STEPS": "120"}): sys.exit()
h = hroot(["L9_s1cut", j, s1, s2])
if not search(s3, s2, ["0", "0", "400", "follow"], {"L4S_STEPS": "100", "L4S_FOLLOW": "375,700", "L4S_HROOT": str(h)}): sys.exit()
h = hroot(["L9_s1cut", j, s1, s2, s3])
search(s4, s3, ["0", "0", "400", "follow"], {"L4S_STEPS": "160", "L4S_FOLLOW": "700,1130", "L4S_HROOT": str(h)})

"""One Terra Tubes chain with a given pocket wait: python l9chain3.py <wait frames> <suffix>
   sections: L9_s1 -> L9_w<suffix> (idle) -> L9_s2<suffix> (band to the tube's water line) -> L9_s3<suffix> (follow 375-700) -> L9_s4<suffix> (follow 700-1130)"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from toads.emulator import BizHawk
P = Path(__file__).parent
wait, sfx = int(sys.argv[1]), sys.argv[2]
w = f"L9_w{sfx}"; s2 = f"L9_s2{sfx}"; s3 = f"L9_s3{sfx}"; s4 = f"L9_s4{sfx}"
(P / "knowledge" / f"l4s_{w}.json").write_text(json.dumps([""] * wait))
e = BizHawk(log_name=f"chain3_{sfx}.log"); e.load("L9_s1_solved"); e.step((), 2); e.step((), wait); e.save(f"{w}_solved"); e.close()
shutil.copy(P / "states" / "L9_s1_solved.State", P / "states" / f"{w}.State")
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
h = hroot(["L9_s1", w]); print(f"{w}: {wait} idle frames, H {h}", flush=True)
if not search(s2, w, ["180", str(-650 - h), "400", "reach_band_w"], {"L4S_STEPS": "120"}): sys.exit()
h = hroot(["L9_s1", w, s2])
if not search(s3, s2, ["0", "0", "400", "follow"], {"L4S_STEPS": "100", "L4S_FOLLOW": "375,700", "L4S_HROOT": str(h)}): sys.exit()
h = hroot(["L9_s1", w, s2, s3])
search(s4, s3, ["0", "0", "400", "follow"], {"L4S_STEPS": "160", "L4S_FOLLOW": "700,1130", "L4S_HROOT": str(h)})

"""Final climb section to the Robo-Manus arena floor (world H 4126): wait for section 6 of a chain, measure the
exact height after six sections with l8.py, then search the remaining climb.   python l8final.py <prefix>"""
import os, re, subprocess, sys, time, shutil
from pathlib import Path
P = Path(__file__).parent; pre = sys.argv[1]
log6 = P / "logs" / f"l4s_L8_{pre}6.txt"
while not any(w in log6.read_text() for w in ("solved", "unsolved")):
    time.sleep(20)
assert "unsolved" not in log6.read_text(), "section 6 unsolved"
secs = [f"L8_{pre}{i}" for i in range(1, 7)]
out = subprocess.run([sys.executable, "l8.py", *secs], cwd=P, capture_output=True, text=True).stdout
H = int(re.search(r"segment \d+ frames.*? H (\d+)", out).group(1))
print("H after six sections:", H, "-> final climb", 4126 - H, flush=True)
shutil.copy(P / "states" / f"L8_{pre}6_solved.State", P / "states" / f"L8_{pre}7.State")
env = dict(os.environ, L4S_LVL="7", L4S_SAFE="30", L4S_STEPS="150", L4S_ACTS="climb")
with open(P / "logs" / f"l4s_L8_{pre}7.txt", "w") as f:
    subprocess.run([sys.executable, "l4s.py", f"L8_{pre}7", "0", str(4126 - H), "600", "climb"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
print((P / "logs" / f"l4s_L8_{pre}7.txt").read_text().splitlines()[-1][:150], flush=True)

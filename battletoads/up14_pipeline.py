"""Waits for the queens L13y0 / L13y1 (behind L12g); keeps the valid shorter one (f2 counter >= 240, hp 47 throughout),
assembles up13, checks the run really finishes, then builds the text and renders (2026-10-07)."""
import json, os, re, subprocess, sys, time
from toads.emulator import LOGS_DIR
names = ["L13y0", "L13y1"]
def status(n):
    log = f"logs/l13solve_{n}.txt"
    if not os.path.exists(log): return None
    s = open(log).read()
    if "unsolved" in s: return "bad"
    if "level byte left" not in s: return None
    f2 = re.search(r"f2: .* counter (\d+), hp (\d+)", s); f3 = re.search(r"f3: .* hp (\d+)", s)
    ok = f2 and int(f2.group(1)) >= 240 and int(f2.group(2)) == 47 and f3 and int(f3.group(1)) == 47 and re.search(r"level (254|255)", s)
    return "ok" if ok else "bad"
while True:
    st = {n: status(n) for n in names}
    if all(v is not None for v in st.values()) or any(v == "ok" for v in st.values()) and time.time() > 0 and all(v is not None for v in st.values()): break
    time.sleep(60)
good = [n for n in names if st[n] == "ok"]
print("queen status", st, flush=True)
if not good: print("no valid queen", flush=True); sys.exit(1)
best = min(good, key=lambda n: len(json.load(open(LOGS_DIR / f"pbeam_{n}.json"))["inputs"]))
print("using", best, len(json.load(open(LOGS_DIR / f"pbeam_{best}.json"))["inputs"]), flush=True)
def run(args):
    print(">>", " ".join(args), flush=True); p = subprocess.run([sys.executable, "-u"] + args, capture_output=True, text=True); print(p.stdout[-3000:], flush=True); return p
p = run(["assemble.py", "up14", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12g", best])
if p.returncode or "level=13" in p.stdout.split("end state")[-1][:80] or "MATCH" not in p.stdout: print("ASSEMBLY NOT A FINISH", flush=True); sys.exit(1)
print("ASSEMBLED", flush=True)
run(["video_text2.py", "up14"]); run(["render_overlay.py", "up14"]); print("PIPELINE DONE", flush=True)

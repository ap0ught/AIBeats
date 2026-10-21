"""u16b: fight json -> built Level 8 segment -> merge scan, in one go.   python u16b_auto.py <climb json> <fight tag> <segment tag>
Runs u16b_build.py and u16b_sync.py; prints the two result lines.  Segment names: B8_<segtag>_raw / B8_<segtag>."""
import json, subprocess, sys
from toads.emulator import LOGS_DIR
climb, ftag, stag = sys.argv[1], sys.argv[2], sys.argv[3]
raw, out = f"B8_{stag}_raw", f"B8_{stag}"
with open(LOGS_DIR / "fix" / f"u16b_build_{raw}.txt", "w") as f:
    rc = subprocess.run([sys.executable, "u16b_build.py", climb, str(LOGS_DIR / "fix" / f"u16b_fight_{ftag}.json"), raw, "300", "A"], stdout=f, stderr=subprocess.STDOUT).returncode
print(open(LOGS_DIR / "fix" / f"u16b_build_{raw}.txt").read().strip().splitlines()[-1][:160], flush=True)
if rc:
    sys.exit(1)
j = json.load(open(LOGS_DIR / f"pbeam_{raw}.json"))
T0 = j["kill_frame"] - 12483
with open(LOGS_DIR / "fix" / f"u16b_sync_{out}.txt", "w") as f:
    subprocess.run([sys.executable, "u16b_sync.py", raw, "L9heli_c2", str(T0), "11", out], stdout=f, stderr=subprocess.STDOUT)
for l in open(LOGS_DIR / "fix" / f"u16b_sync_{out}.txt"):
    if l.startswith(("variants", "segment length", "wrote", "NO in-sync", raw)):
        print(l.strip()[:700], flush=True)

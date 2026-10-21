"""Save the Level 10 entry of a finished Level 9 line as bookmark L9heli_<tag>_end0 (the state after its last input) and compare it with
the old run's bookmark L9c_end0.   python l9heli_fix_endbm.py <tag> <root index>"""
import json, sys
from l9heli_fix_lib import *
TAG, root = sys.argv[1], int(sys.argv[2])
R = cap(); ins = up14_inputs()
new = json.load(open(LOGS_DIR / f"pbeam_L9heli_{TAG}.json"))["inputs"]
e = BizHawk(log_name=f"l9heli_fix_endbm_{TAG}.log")
goto(e, OFF + root, ins, check=True)
for b in new[root:]: e.step(bt(b), 1)
m = e.ram(0, 0x800); e.save(f"L9heli_{TAG}_end0")
e.load("L9c_end0"); o = e.ram(0, 0x800); ref = bytes(R[OFF + 9987 - 1])
print("new end vs cap14 row:", sum(1 for a in range(0x800) if m[a] != ref[a]), "bytes differ; old bookmark L9c_end0 vs cap14 row:", sum(1 for a in range(0x800) if o[a] != ref[a]), flush=True)
e.close()

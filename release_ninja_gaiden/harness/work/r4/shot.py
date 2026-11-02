"""screenshot a state after optional rows: python work/r4/shot.py <state> <name> [rows file] [n]"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa
e = C.open_emu("r4_shot.log")
try:
    s = e.load(sys.argv[1])
    if len(sys.argv) > 3:
        rows = list(read_inputs(P / sys.argv[3]))[:int(sys.argv[4])]
        s = e.run(rows)
    print(s["frame"], s["x"], s["y"], e.screenshot(sys.argv[2]))
finally:
    e.close()

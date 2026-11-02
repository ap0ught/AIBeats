"""collect per-frame data around swings for hit-rule fitting: python work/r4/jq_swdata.py <rows file|plan json> <out jsonl>"""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa
src = sys.argv[1]
if src.endswith(".json"):
    import jqrows
    want, _ = jqrows.plan_rows(json.loads(Path(src).read_text())["steps"])
else:
    want = list(read_inputs(P / src))
hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
en = C.Enforcer(hist)
rr = [en.emit(r, retry=0) for r in want]
e = C.open_emu("r4_swdata.log")
out = open(P / sys.argv[2], "a")
try:
    s0 = e.load("tmp/a56r2_64b_control")
    prev = None
    for i, r in enumerate(rr):
        e.run([r])
        ram = e.ram(0, 0x800)
        d = dict(row=i + 1, rx=ram[0x86] + ram[0x85] / 256, ry=ram[0x8A], a83=ram[0x83], f84=ram[0x84], r90=ram[0x90],
                 r91=ram[0x91], r92=ram[0x92], jx=ram[0x467] + ram[0x45F] / 256, jy=ram[0x487], bhp=ram[0x497], hp=ram[0x65],
                 pose7=ram[0x43F], src=src)
        out.write(json.dumps(d) + "\n")
finally:
    out.close(); e.close()

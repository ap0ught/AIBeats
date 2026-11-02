"""fireball calibration data: play rows (plan json or spec), dump per row Ryu x/xsub/y and slots 5,6 full motion bytes."""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa
from jq_play import parse  # noqa
src = sys.argv[1]
if src.endswith(".json"):
    import jqrows
    want, _ = jqrows.plan_rows(json.loads(Path(src).read_text())["steps"])
else:
    want = parse(src)
hist = list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
en = C.Enforcer(hist)
rr = [en.emit(r, retry=0) for r in want]
e = C.open_emu("r4_fbdata.log")
out = open(P / sys.argv[2], "w")
try:
    e.load("tmp/a56r2_64b_control")
    for i, r in enumerate(rr):
        e.run([r])
        ram = e.ram(0, 0x800)
        d = dict(row=i + 1, rx=ram[0x86], rxs=ram[0x85], ry=ram[0x8A], hp=ram[0x65], f84=ram[0x84], a83=ram[0x83],
                 jx=ram[0x467], jxs=ram[0x45F], jt=ram[0x40F])
        for k in (5, 6):
            d[f"f{k}"] = [ram[0x400 + k], ram[0x460 + k], ram[0x458 + k], ram[0x450 + k], ram[0x448 + k],
                          ram[0x480 + k], ram[0x478 + k], ram[0x470 + k], ram[0x468 + k], ram[0x498 + k], ram[0x438 + k]]
        out.write(json.dumps(d) + "\n")
finally:
    out.close(); e.close()

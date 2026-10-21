"""Check the offline UFO model against a calibration dump (tools/s5b_cal.py)."""
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s5_ufo_sim import replay, plan  # noqa: E402

lines = Path(sys.argv[1]).read_text().splitlines()
rec = []
for l in lines:
    m = re.match(r"k=(\d+) fc=(\d+) y=(\d+) sub=(\d+) vy=(\d+) jmp=(\d+) x=(\d+) aim=(\d+) hp=(-?\d+) st=(-?\d+) row=(\S*) lagged=(\d) B=(\[.*?\]) E=", l)
    if m:
        rec.append(dict(k=int(m[1]), y=int(m[3]), sub=int(m[4]), x=int(m[7]), hp=int(m[9]), st=int(m[10]), row=m[11].split("+"),
                        B=ast.literal_eval(m[13])))
k0 = rec[0]["k"] - 1
P = [r["k"] for i, r in enumerate(rec) if "B" in r["row"] and (i == 0 or "B" not in rec[i - 1]["row"])]
J = [r["k"] for i, r in enumerate(rec) if "A" in r["row"] and (i == 0 or "A" not in rec[i - 1]["row"])]
th = next(r["k"] for r in rec if r["st"] >= 0 and not (r["st"] & 0x80))
acc = [(0x80, 0x80)] * 10
seen = set()
for r in rec:
    for b in r["B"]:
        if b[0] not in seen and b[1] == 1:
            seen.add(b[0])
            acc[b[0]] = (b[3], b[5])
x = rec[0]["x"]
print("k0", k0, "th", th, "P", P, "J", J, "x", x, "acc", acc)
out = replay(k0, rec[0]["y"] * 256 + rec[0]["sub"], x, acc, th, 128, 48, P, J, rec[-1]["k"])
bad = 0
for (k, y, hp), r in zip(out, rec):
    if (y, hp) != (r["y"], r["hp"]):
        bad += 1
        if bad <= 12:
            print("MISMATCH k", k, "sim y,hp", y, hp, "emu", r["y"], r["hp"])
print("frames", len(out), "mismatches", bad, "sim kill", next((k for k, y, hp in out if hp == 0), None), "emu kill", rec[-1]["k"])
if len(sys.argv) > 2:
    import time
    for ka in [int(v) for v in sys.argv[2].split(",")]:
        t0 = time.time()
        res = plan(k0, rec[0]["y"] * 256 + rec[0]["sub"], x, acc, th, 128, 48, th - ka, width=int(sys.argv[3]))
        print("lead", ka, "->", None if res is None else (res[0] - th, res[1], res[2]), f"{time.time() - t0:.1f} s")

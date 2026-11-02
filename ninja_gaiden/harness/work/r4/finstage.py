"""Round 4: finish a non-boss stage from rows: play rows from the start state; if the next stage loads inside them,
cut at the load frame; else continue with a56_beam's to_next_stage (stage-end walk / cinematic Start skip), then
a56_solve.finalize (open-loop replay, logs/a56_<stage>_<tag>.inputs.txt + .json, chain states).
    python work/r4/finstage.py <stage idx> <start state> <rows file|logs/r4 name> <tag> [--hist file]"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages"))
sys.path.insert(0, str(P))
import a56_common as C  # noqa: E402
import a56_solve as S  # noqa: E402
from a56_beam import StageBeam  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

a = sys.argv[1:]
hist = None
if "--hist" in a:
    i = a.index("--hist"); hist = a[i + 1]; del a[i:i + 2]
stage, start, rowsf, tag = int(a[0]), a[1], a[2], a[3]
if not (P / rowsf).exists():
    rowsf = f"logs/r4/{rowsf}.inputs.txt"
h = list(read_inputs(P / hist))[-1800:] if hist else []
en = C.Enforcer(h)
rows = [en.emit(r, retry=0) for r in read_inputs(P / rowsf)]
e = C.open_emu(f"r4_finstage_{tag}.log")
try:
    e.tick(TICKS)
    s0 = e.load(start)
    tr = C.play_trace(e, rows)
    cut = next((i for i, t in enumerate(tr) if t["stage"] != stage), None)
    if cut is not None:
        rows = rows[:cut + 1]
        print("load inside the rows at", tr[cut]["frame"], flush=True)
    else:
        en = C.Enforcer(h)
        rows = [en.emit(r, retry=0) for r in rows]
        e.load(start)
        e.run(rows)
        fake = StageBeam.__new__(StageBeam)
        fake.e, fake.stage, fake._cs_seen = e, stage, False
        done, extra = fake.to_next_stage(en)
        rows = rows + extra
        print("to_next_stage ->", done, "extra rows", len(extra), flush=True)
    rep = S.finalize(e, stage, start, rows, tag, {"from": rowsf})
    print(rep)
finally:
    e.close()

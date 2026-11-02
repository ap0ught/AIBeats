"""Finish a boss-planner result: rows up to the kill -> + tally / cutscene skip (one 2-frame Start, retried every 5
frames) up to the next stage's load (6-5: END seen), legal through the Enforcer; then a56_solve.finalize (open-loop
replay, logs/a56_<name>_<tag>.inputs.txt/.json/.ref.json, chain states).

    python work/a56r2/finish.py <stage idx> <start state> <rows file> <tag> [--hist file] [--pre-blank n]
           [--lead file]   (rows played BEFORE <rows file> from the start state, e.g. 151 blank load rows)
"""
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


def opt(a, n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v) if d is not None else v
    return d


def main():
    a = sys.argv[1:]
    hist = opt(a, "--hist", None)
    pre_blank = opt(a, "--pre-blank", 0)
    lead = opt(a, "--lead-blank", 0)
    stage, start, rowsf, tag = int(a[0]), a[1], a[2], a[3]
    h = (list(read_inputs(P / hist))[-1700:] if hist else []) + [()] * pre_blank
    en = C.Enforcer(h)
    rows = [en.emit(r, retry=0) for r in [()] * lead + list(read_inputs(P / rowsf))]
    e = C.open_emu(f"a56r2_finish_{tag}.log")
    try:
        e.tick(TICKS)
        e.load(start)
        e.run(rows)
        fake = StageBeam.__new__(StageBeam)
        fake.e, fake.stage, fake._cs_seen = e, stage, False
        done, extra = fake.finish_boss(en)
        rows = rows + extra
        rep = S.finalize(e, stage, start, rows, tag, {"from": rowsf, "lead_blank": lead})
        print(rep)
    finally:
        e.close()


if __name__ == "__main__":
    main()

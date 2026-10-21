"""Open-loop replay of finished stage 3 / stage 8 segments on a FRESH emulator, with the END by contra/clock.py.

    python tools/s8_verify_p2.py s3:<state>:<seg name> ... s8:<state>:<seg name> ...   (seg name under logs/, no extension)
Optional 4th field: a prior inputs file whose rows are checked together with the segment (press rules across the cut).
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, TR  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, check_rows, read_inputs, write_inputs  # noqa: E402
from contra import clock  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

fields = dict(TR)
fields.update(clock.FIELDS)
with Engine(1, tag="s8", fields=fields) as eng:
    for spec in sys.argv[1:]:
        parts = spec.split(":")
        stage, state, name = parts[0], parts[1], parts[2]
        prior = read_inputs(LOGS_DIR / parts[3])[-12:] if len(parts) > 3 else []
        rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / f"{name}.seg.json").read_text())["rows"]]
        tr = eng.sim(eng.root(state), rows + [()] * 3)
        L = next(s["frame"] for s in tr if s["lroutine"] == 4)
        deaths = sum(1 for k in range(1, len(tr)) if tr[k]["death"] & 1 and not tr[k - 1]["death"] & 1)
        lag = sum(1 for s in tr[:len(rows)] if s["lagged"])
        bad = check_rows(rows, prior)
        both = LOGS_DIR / f"{name}.withprior.inputs.txt"
        if prior:
            write_inputs(both, list(prior) + rows, "prior+segment")
        if stage == "s8":
            en = clock.end_frame(tr)
            print(f"{name}: rows {len(rows)}, L frame {L}, END by clock.py: {en}; frames L to END "
                  f"{None if en is None else en['ram'] - L}; deaths {deaths}; lag {lag}; weapon ${tr[-1]['weapon']:02x}; "
                  f"rule violations (with prior {len(prior)} rows) {len(bad)}")
        else:
            k = next((i for i, s in enumerate(tr) if s["level"] == 3 and s["lroutine"] == 4), None)
            print(f"{name}: rows {len(rows)}, L frame {L}, stage 4's first frame at trace index {k} "
                  f"(expected {len(rows)}); deaths {deaths}; lag {lag}; weapon ${tr[min(len(tr) - 1, len(rows))]['weapon']:02x}; "
                  f"rule violations (with prior {len(prior)} rows) {len(bad)}")

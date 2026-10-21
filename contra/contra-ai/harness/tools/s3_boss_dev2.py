"""Save a state 70 rows before the mouth opens (development aid).  python tools/s3_boss_dev2.py <climb name>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Pad, LOGS_DIR  # noqa: E402
from contra.stages.s3s8_engine import Engine, Ck  # noqa: E402
from contra.stages import s3_boss  # noqa: E402
from contra.stages.s8 import run_phase  # noqa: E402

name = sys.argv[1]
j = json.loads((LOGS_DIR / f"{name}_climb.rows.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
eng = Engine(3, tag=name.replace("/", "_"))
try:
    ck0 = Ck(f"{name}_climb_end", len(rows), rows, Pad.from_rows(rows))
    ck, info = s3_boss.trigger_jump(eng, ck0, 0x13)
    ck, ov = run_phase(eng, ck, s3_boss.mouth_open, 0x13, name="B-wait", stall_ok=lambda s: True, base=(), fire=False,
                       cand_fn=s3_boss.survive_cands, progress=lambda s: 0, H=300)
    m_open = ck.i - 1
    c2, _ = eng.commit(ck0, ck.rows[ck0.i:m_open - 70], keep=f"{name}_m70")
    (LOGS_DIR / f"{name}_m70.rows.json").write_text(json.dumps({"rows": ["+".join(r) for r in c2.rows], "m_open": m_open}))
    print("saved", f"{name}_m70", "m_open", m_open, "rows", c2.i)
finally:
    eng.close()

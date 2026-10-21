"""Timing of emulator operations + development states for the stage 8 bosses (from the best run's rows).

    python tools/s8_timing.py
Writes states/s8/dev_g437 (80 rows before the guardian), dev_g560, dev_h2749 (80 rows before the boss scroll).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, TR  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / "s8/best.seg.json").read_text())["rows"]]
with Engine(1, tag="s8") as eng:
    e = eng.emus[0]
    root = eng.root("dbg/s8_pre")
    t = time.time()
    ck, _ = eng.commit(root, rows[:437], keep="s8/dev_g437")
    print("437 rows + save", round(time.time() - t, 2))
    ck2, _ = eng.commit(ck, rows[437:560], keep="s8/dev_g560")
    ck3, _ = eng.commit(ck2, rows[560:2749], keep="s8/dev_h2749")
    t = time.time()
    for _ in range(20):
        e.load("s8/dev_g560")
    print("file load", (time.time() - t) / 20)
    t = time.time()
    for _ in range(20):
        e.save("s8/tmp/timing")
    print("file save", (time.time() - t) / 20)
    t = time.time()
    ids = [e.msave() for _ in range(20)]
    print("msave", (time.time() - t) / 20)
    t = time.time()
    for i in ids:
        e.mload(i)
    print("mload", (time.time() - t) / 20)
    for i in ids:
        e.mfree(i)
    t = time.time()
    for _ in range(20):
        e.run(rows[560:566])
    print("run 6 frames (trace)", (time.time() - t) / 20)
    t = time.time()
    e.run(rows[566:766])
    print("run 200 frames (trace)", (time.time() - t))
    t = time.time()
    for _ in range(20):
        e.ram_all()
    print("ram_all", (time.time() - t) / 20)

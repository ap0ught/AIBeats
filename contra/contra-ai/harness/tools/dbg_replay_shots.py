"""DEBUG: replay rows saved by dbg_to_heart.py (same pokes) and take screenshots at given row indexes."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / "dbg_to_heart.rows.json").read_text())]
marks = sorted(int(x) for x in sys.argv[1].split(","))
with BizHawk(log_name="dbg_shots.log", fields={"x": 0x334, "y": 0x31A, "screen": 0x64, "scroll": 0x65, "pstate": 0x90}) as e:
    e.load("dbg/s8_pre")
    for i, r in enumerate(rows[:marks[-1]]):
        e.poke(0xB0, 0x80)
        s = e.step(r, 1)
        if i + 1 in marks:
            e.screenshot(f"probe/s8dbg_i{i + 1}")
            print(i + 1, s)

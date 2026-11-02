"""Run a python snippet against one emulator: python tools/probe.py <snippet.py> [state]
The snippet sees `e` (BizHawk, loaded with [state] if given), np, shot(name), zp(lo,hi)."""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, load_fields

if __name__ == "__main__":
    code = Path(sys.argv[1]).read_text(encoding="utf-8")
    e = BizHawk(log_name="probe.log")
    try:
        if len(sys.argv) > 2:
            e.load(sys.argv[2])
        def shot(n): return e.screenshot(n)
        def zp(lo=0, hi=0x100): return ' '.join(f'{b:02x}' for b in e.ram(lo, hi - lo))
        exec(compile(code, sys.argv[1], "exec"), {"e": e, "np": np, "shot": shot, "zp": zp, "__name__": "__probe__"})
    finally:
        e.close()

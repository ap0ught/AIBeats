"""Fourth one-off patch for rule v2: the budget's windows as a parameter of both solvers.

    solve(..., windows=WINDOWS)      and on the command line      --windows 600:109,1800:246
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "contra" / "stages"


def patch(name, reps):
    p = root / name
    s = p.read_text(encoding="utf-8")
    for a, b in reps:
        assert s.count(a) == 1, (name, a[:70], s.count(a))
        s = s.replace(a, b)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(s, encoding="utf-8")
    tmp.replace(p)
    print(name, "patched")


CLI_OLD = '''        hist = read_inputs(a[i + 1])
        del a[i:i + 2]
'''
CLI_NEW = '''        hist = read_inputs(a[i + 1])
        del a[i:i + 2]
    win = WINDOWS
    if "--windows" in a:                 # the press budget, e.g. --windows 600:109,1800:246 (rule v2, the default)
        i = a.index("--windows")
        win = tuple((int(x.split(":")[0]), int(x.split(":")[1])) for x in a[i + 1].split(",") if x)
        del a[i:i + 2]
'''
patch("s1.py", [
    ('''from .s1_common import Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, fire, log, press_report, save_seg
''', '''from .s1_common import (Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, WINDOWS, fire, log, press_report,
                        save_seg)
'''),
    ('''def solve(start="s1/pre_w0", out="w0", n=3, history=None, width=8, refine=0):
''', '''def solve(start="s1/pre_w0", out="w0", n=3, history=None, width=8, refine=0, windows=WINDOWS):
    """history = the real rows before the solver's first row (at least the last HISTORY_ROWS of them): the press
    budget counts them. windows = the budget's ((rows, most presses), ...), rule v2 by default."""
'''),
    ('''        g.load_file(start, pad=Pad.from_rows(history) if history else None)
        f_pre = g.r.frame
''', '''        g.load_file(start, pad=Pad.from_rows(history, windows))
        info["windows"] = [list(x) for x in windows]
        f_pre = g.r.frame
'''),
    ('''        pr = press_report(g.rows, history)
        log(f"run phase: ok={ok}''', '''        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        log(f"run phase: ok={ok}'''),
    ('''        pr = press_report(g.rows, history)
        info["presses"] = pr
''', '''        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        info["presses"] = pr
'''),
    (CLI_OLD, CLI_NEW),
    ('''    solve(a[0] if a else "s1/pre_w0", a[1] if len(a) > 1 else "w0", history=hist)
''', '''    solve(a[0] if a else "s1/pre_w0", a[1] if len(a) > 1 else "w0", history=hist, windows=win)
'''),
])
patch("s5.py", [
    ('''from .s1_common import Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, fire, log, press_report, save_seg
''', '''from .s1_common import (Farm, Fights, Game, HISTORY_ROWS, HOLD, Pad, Ram, WINDOWS, fire, log, press_report,
                        save_seg)
'''),
    ('''def solve(start="dbg/s5_pre", out="d0", n=3, history=None, width=8, parity=True):
''', '''def solve(start="dbg/s5_pre", out="d0", n=3, history=None, width=8, parity=True, windows=WINDOWS):
    """history = the real rows before the solver's first row (at least the last HISTORY_ROWS of them): the press
    budget counts them. windows = the budget's ((rows, most presses), ...), rule v2 by default."""
'''),
    ('''        g.load_file(start, pad=Pad.from_rows(history) if history else None)
        lag_pre = g.r.lagc
''', '''        g.load_file(start, pad=Pad.from_rows(history, windows))
        info["windows"] = [list(x) for x in windows]
        lag_pre = g.r.lagc
'''),
    ('''        pr = press_report(g.rows, history)
        info["presses"] = pr
''', '''        pr = press_report(g.rows, history, windows=windows or WINDOWS)
        info["presses"] = pr
'''),
    (CLI_OLD, CLI_NEW),
    ('''    solve(a[0] if a else "dbg/s5_pre", a[1] if len(a) > 1 else "d0", history=hist)
''', '''    solve(a[0] if a else "dbg/s5_pre", a[1] if len(a) > 1 else "d0", history=hist, windows=win)
'''),
])

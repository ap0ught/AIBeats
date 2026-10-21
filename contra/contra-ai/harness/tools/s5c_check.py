"""Rule v2 check of a solved stage segment together with the press history before it.

    python tools/s5c_check.py <stage 1|5> <seg name, e.g. c1_v3> [--history <inputs.txt>]

Writes logs/s<stage>/<name>_v2check.inputs.txt = the last 2,000 history rows (if any) + the segment's rows and
runs   python check_inputs.py <that file> --windows 600:109,1800:246 --json logs/s<stage>/<name>_v2check.json
on it: this is the check that must PASS (2,000 rows cover the longest window, so every window that ends inside
the segment is counted exactly as in the whole run).
With a history it also checks the WHOLE history + segment and prints where its violations are: a history taken
from the first complete run (rule v1) breaks rule v2 in its own stages 1 (and 5, 8); what matters here is that
no violation lies on a frame of the new segment.
Prints the presses of the segment alone and the highest count in any 600 / 1,800 rows that end inside it.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_inputs  # noqa: E402
from contra.emulator import LOGS_DIR, PROJECT  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages.s1_common import WINDOWS, press_report  # noqa: E402

TAIL = 2000


def main():
    a = sys.argv[1:]
    hist = []
    hname = ""
    if "--history" in a:
        i = a.index("--history")
        hname = a[i + 1]
        hist = [tuple(r) for r in read_inputs(hname)]
        del a[i:i + 2]
    stage, name = a[0], a[1]
    seg = json.loads((LOGS_DIR / f"s{stage}" / f"{name}.seg.json").read_text(encoding="utf-8"))
    rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
    for b in ("B", "A", "Up", "Down", "Left", "Right"):
        pr = press_report(rows, hist, b)
        print(f"   {b:5s}: {pr['presses']:4d} presses in the segment; most in any 600 rows {pr['most_600']:3d} (limit 109), "
              f"in any 1800 rows {pr['most_1800']:3d} (limit 246), history counted")
    if hist:
        rep = check_inputs.check(hist + rows, windows=WINDOWS)
        n0 = len(hist)
        inside = outside = 0
        last_out = 0
        for rname, r in rep["rules"].items():
            if not r["violations"]:
                continue
            print(f"   whole history + segment ({len(hist) + len(rows)} rows): {rname}: {r['violations']} violations {r.get('by_button', '')}")
        # where: recount the window violations by frame
        from contra.stages.s1_common import press_starts
        for b in check_inputs.BUTTONS:
            st = press_starts(hist + rows, b)
            for wf, wmax in WINDOWS:
                j = 0
                for i in range(len(st)):
                    while st[i] - st[j] >= wf:
                        j += 1
                    if i - j + 1 > wmax:
                        if st[i] >= n0:
                            inside += 1
                        else:
                            outside += 1
                            last_out = max(last_out, st[i])
        print(f"   window violations on rows of the history: {outside} (last on history row {last_out} of {n0}); "
              f"on rows of the new segment: {inside}")
        (LOGS_DIR / f"s{stage}" / f"{name}_v2check_whole.json").write_text(json.dumps(
            {"rows": len(hist) + len(rows), "history_rows": n0, "pass_whole": rep["pass"], "rules": rep["rules"],
             "window_violations_in_history": outside, "last_history_row_with_violation": last_out,
             "window_violations_in_segment": inside}, indent=1), encoding="utf-8")
    out = LOGS_DIR / f"s{stage}" / f"{name}_v2check.inputs.txt"
    cut = max(0, len(hist) - TAIL)
    while cut > 2 and (hist[cut] or hist[cut - 1] or hist[cut - 2]):      # do not cut through a press or a release
        cut -= 1
    h2 = hist[cut:] if cut > 2 else hist
    write_inputs(out, h2 + rows, f"rule v2 check: last {len(h2)} history rows ({hname or 'none'}) + stage {stage} segment {name} ({len(rows)} rows)")
    jout = LOGS_DIR / f"s{stage}" / f"{name}_v2check.json"
    rc = subprocess.call([sys.executable, str(PROJECT / "check_inputs.py"), str(out), "--windows", "600:109,1800:246",
                          "--json", str(jout)])
    print(f"check_inputs --windows 600:109,1800:246 on the last {len(h2)} history rows + the segment: exit code {rc} (0 = PASS)")
    sys.exit(rc)


if __name__ == "__main__":
    main()

"""Independent input-rule checker (verifier's own code; does not import check_inputs.py or ng/).

Rules (knowledge/project_rules.md, owner-approved 2026-10-19; board: no L+R, no turbo; NES general doc: no U+D):
  R1 controller 1 only: every token is one of Up Down Left Right Select Start B A
  R2 never Left+Right, never Up+Down on one frame
  R3 per button: a new press (rising edge) at most once every 5 frames (start-to-start >= 5)
  R4 per button: every press held >= 2 frames (a press still held at the last row is reported, not failed)
  R5 per button: released >= 2 frames between two presses
  R6 per button: <= 109 press starts in any 600-frame span, <= 246 in any 1,800-frame span
Usage: python vrules.py <inputs.txt> [--json out.json]
"""
import json, sys
from collections import Counter

BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
PERIOD, HOLD, RELEASE = 5, 2, 2
WINDOWS = ((600, 109), (1800, 246))


def read(path):
    rows, bad = [], []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            if line.startswith("#"):
                continue
            s = line.strip()
            toks = [t for t in s.replace(",", "+").split("+") if t] if s else []
            for t in toks:
                if t not in BUTTONS:
                    bad.append((len(rows) + 1, t))
            rows.append(frozenset(toks))
    return rows, bad


def runs(rows, b):
    out, st = [], None
    for i, r in enumerate(rows, 1):
        if b in r and st is None:
            st = i
        elif b not in r and st is not None:
            out.append((st, i - st)); st = None
    if st is not None:
        out.append((st, len(rows) - st + 1, "open"))
    return out


def check(path, upto=None):
    rows, bad = read(path)
    if upto:
        rows = rows[:upto]
    v = {"R1_bad_tokens": bad, "R2_LR": [], "R2_UD": [], "R3_period": [], "R4_hold": [], "R5_release": [],
         "R6_windows": [], "info": {}}
    for i, r in enumerate(rows, 1):
        if "Left" in r and "Right" in r:
            v["R2_LR"].append(i)
        if "Up" in r and "Down" in r:
            v["R2_UD"].append(i)
    open_runs = []
    stats = {}
    for b in BUTTONS:
        rr = runs(rows, b)
        starts = [x[0] for x in rr]
        for k, x in enumerate(rr):
            if len(x) == 3:
                open_runs.append((b, x[0], x[1]))
            elif x[1] < HOLD:
                v["R4_hold"].append((x[0], b, x[1]))
            if k:
                p = rr[k - 1]
                if x[0] - p[0] < PERIOD:
                    v["R3_period"].append((x[0], b, x[0] - p[0]))
                if x[0] - (p[0] + p[1]) < RELEASE:
                    v["R5_release"].append((x[0], b, x[0] - (p[0] + p[1])))
        worst = {}
        for span, cap in WINDOWS:
            j, best, at = 0, 0, None
            for i2 in range(len(starts)):
                while starts[i2] - starts[j] >= span:
                    j += 1
                c = i2 - j + 1
                if c > best:
                    best, at = c, starts[j]
            worst[span] = (best, at)
            if best > cap:
                v["R6_windows"].append((b, span, best, cap, at))
        gaps = Counter(min(x[0] - rr[k - 1][0], 99) for k, x in enumerate(rr) if k)
        stats[b] = {"presses": len(rr), "min_start_to_start": min(gaps) if gaps else None,
                    "min_hold": min((x[1] for x in rr if len(x) == 2), default=None),
                    "max_per_600": worst[600][0], "max_per_1800": worst[1800][0]}
    allstarts = sorted(x[0] for b in BUTTONS for x in runs(rows, b))
    v["info"] = {"rows": len(rows), "per_button": stats, "open_at_end": open_runs,
                 "total_presses": len(allstarts)}
    fails = [k for k in v if k.startswith("R") and v[k]]
    v["verdict"] = "PASS" if not fails else "FAIL: " + ", ".join(fails)
    return v


if __name__ == "__main__":
    r = check(sys.argv[1])
    if "--json" in sys.argv:
        json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=list)
    print(sys.argv[1], r["info"]["rows"], "rows; verdict", r["verdict"])
    for b, s in r["info"]["per_button"].items():
        print(f"  {b:6s} {s}")
    print("  open at end:", r["info"]["open_at_end"])
    for k in r:
        if k.startswith("R") and r[k]:
            print("  VIOLATION", k, r[k][:20], "..." if len(r[k]) > 20 else "")

"""Is an input list something a person could physically play, under this project's own constraints?

    python check_inputs.py <logs/x.inputs.txt> [--period 5] [--hold 2] [--release 2] [--buttons B,A,...] [--json out.json]

Rules checked (exit code 1 if any fails):
  1. controller 1 only        - the file format has one controller; every token must be one of its 8 buttons
  2. no opposite directions   - never Left+Right, never Up+Down on the same frame
  3. press rate (per button)  - a new press of the same button at most once every `period` frames (default 5 =
                                12 presses per second at 60 fps), every press held at least `hold` frames
                                (default 2), every gap between two presses of the same button at least `release`
                                frames (default 2). Applied to every button, or to --buttons only.
The cap is a parameter on purpose: the project has not fixed it yet (defaults = the day-1 working value).
Also printed, for information: presses per button, the fastest 1-second window per button, hold-length histogram.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


def read_rows(path):
    rows, bad = [], []
    for n, l in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if l.startswith("#"):
            continue
        toks = tuple(x for x in l.strip().replace(",", "+").split("+") if x)
        for t in toks:
            if t not in BUTTONS:
                bad.append((n, t))
        rows.append(toks)
    return rows, bad


def presses(rows, b):
    """[(first frame, length)] for every press of button b; frames are 1-based row numbers."""
    out, start = [], None
    for i, r in enumerate(rows):
        h = b in r
        if h and start is None:
            start = i
        elif not h and start is not None:
            out.append((start + 1, i - start))
            start = None
    if start is not None:
        out.append((start + 1, len(rows) - start))
    return out


def check(rows, period=5, hold=2, release=2, buttons=BUTTONS, bad_tokens=(), windows=()):
    # windows: sustained caps, ((frames, max_presses), ...): at most max_presses new presses of one button whose
    # start frames lie within any span of `frames` frames (rule v2: 600:109 and 1800:246, the record holder's
    # own heard rates over 10 and 30 seconds; see knowledge/record_mash_rate.md)
    n = len(rows)
    rep = {"frames": n, "params": {"period": period, "hold": hold, "release": release, "buttons": list(buttons),
                                   "windows": [list(w) for w in windows]},
           "rules": {}, "stats": {}}
    v_win = {w: [] for w in windows}
    rep["rules"]["controller_1_only"] = {"violations": len(bad_tokens), "first": [list(x) for x in bad_tokens[:10]]}
    lr = [i + 1 for i, r in enumerate(rows) if "Left" in r and "Right" in r]
    ud = [i + 1 for i, r in enumerate(rows) if "Up" in r and "Down" in r]
    rep["rules"]["no_left_right"] = {"violations": len(lr), "first": lr[:10]}
    rep["rules"]["no_up_down"] = {"violations": len(ud), "first": ud[:10]}
    v_period, v_hold, v_rel = [], [], []
    for b in BUTTONS:
        ps = presses(rows, b)
        starts = [s for s, _ in ps]
        # fastest one-second window (60 frames)
        best, j = 0, 0
        for i in range(len(starts)):
            while starts[i] - starts[j] >= 60:
                j += 1
            best = max(best, i - j + 1)
        hist = {}
        for _, l in ps:
            k = str(l) if l < 8 else "8+"
            hist[k] = hist.get(k, 0) + 1
        gaps = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
        rep["stats"][b] = {"presses": len(ps), "frames_held": sum(l for _, l in ps),
                           "max_presses_in_60_frames": best, "min_frames_between_press_starts": min(gaps) if gaps else None,
                           "hold_length_histogram": dict(sorted(hist.items()))}
        if b not in buttons:
            continue
        for w in windows:
            wf, wmax = w
            j, most = 0, 0
            for i in range(len(starts)):
                while starts[i] - starts[j] >= wf:
                    j += 1
                c = i - j + 1
                most = max(most, c)
                if c > wmax:
                    v_win[w].append((starts[i], b, c))
            rep["stats"][b][f"max_presses_in_{wf}_frames"] = most
        for i, (s, l) in enumerate(ps):
            last = s + l - 1 == n                                  # still held when the file ends: not a short press
            if l < hold and not last:
                v_hold.append((s, b, l))
            if i + 1 < len(ps):
                s2 = ps[i + 1][0]
                if s2 - s < period:
                    v_period.append((s2, b, s2 - s))
                if s2 - (s + l) < release:
                    v_rel.append((s2, b, s2 - (s + l)))
    for name, v in (("press_period", v_period), ("min_hold", v_hold), ("min_release", v_rel)):
        v.sort()
        per = {}
        for _, b, _ in v:
            per[b] = per.get(b, 0) + 1
        rep["rules"][name] = {"violations": len(v), "by_button": per, "first": [list(x) for x in v[:10]]}
    for (wf, wmax), v in v_win.items():
        v.sort()
        per = {}
        for _, b, _ in v:
            per[b] = per.get(b, 0) + 1
        rep["rules"][f"max_{wmax}_in_{wf}_frames"] = {"violations": len(v), "by_button": per,
                                                      "first": [list(x) for x in v[:10]]}
    rep["pass"] = all(r["violations"] == 0 for r in rep["rules"].values())
    return rep


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return type(default)(v)
        return default
    period, hold, release = opt("--period", 5), opt("--hold", 2), opt("--release", 2)
    btn = opt("--buttons", ",".join(BUTTONS)).split(",")
    jout = opt("--json", "")
    wspec = opt("--windows", "600:109,1800:246")   # rule v2 default; --windows none switches it off
    windows = tuple((int(a), int(c)) for a, c in (x.split(":") for x in wspec.split(",") if x and x != "none"))
    rows, bad = read_rows(args[0])
    rep = check(rows, period, hold, release, btn, bad, windows)
    print(f"{args[0]}: {rep['frames']} frames; cap: one press per {period} frames, hold >= {hold}, release >= {release}; "
          f"buttons {','.join(btn)}")
    for name, r in rep["rules"].items():
        extra = f"  by button {r['by_button']}" if r.get("by_button") else ""
        print(f"  {'ok  ' if r['violations'] == 0 else 'FAIL'} {name:18s} violations {r['violations']:6d}{extra}"
              + (f"  first {r['first'][:5]}" if r["violations"] else ""))
    for b, s in rep["stats"].items():
        if s["presses"]:
            print(f"  {b:6s} presses {s['presses']:5d}  held {s['frames_held']:6d} f  fastest second {s['max_presses_in_60_frames']:2d} presses"
                  f"  min start-to-start {s['min_frames_between_press_starts']}  holds {s['hold_length_histogram']}")
    print("RESULT:", "PASS" if rep["pass"] else "FAIL")
    if jout:
        Path(jout).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()

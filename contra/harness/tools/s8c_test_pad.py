"""Offline test of the press budget (contra/stages/s3s8_lib.Pad) against check_inputs.py. No emulator.

    python tools/s8c_test_pad.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Pad, check_rows  # noqa: E402
import check_inputs  # noqa: E402

ok = True
# 1. mashing every button as fast as the Pad allows must pass check_inputs with the same windows, and reach them
for W in (((600, 109), (1800, 246)), ((100, 7), (300, 15)), ()):
    p = Pad(W)
    rows = []
    rng = random.Random(1)
    for i in range(7000):
        want = {"Right"}
        if p.down["B"]:
            if p.t - p.start["B"] < 2:
                want.add("B")
        elif p.can_press("B") and rng.random() < 0.95:
            want.add("B")
        if rng.random() < 0.3:
            want.add("Up")
        if rng.random() < 0.1:
            want.add("A")
        r = p.fix(want)
        p.push(r)
        rows.append(r)
    rep = check_inputs.check(rows, windows=W)
    mx = [rep["stats"]["B"].get(f"max_presses_in_{w}_frames") for w, _ in W]
    print(W, "PASS" if rep["pass"] else "FAIL", "B presses", rep["stats"]["B"]["presses"], "max per window", mx,
          "check_rows violations", len(check_rows(rows, (), W)))
    ok &= rep["pass"] and len(check_rows(rows, (), W)) == 0
    if W:
        ok &= mx[-1] == W[-1][1]          # the long window is reached exactly
    # across a cut: the second half checked with the first as prior, and with a 1 press too many
    ok &= len(check_rows(rows[3500:], rows[:3500], W)) == 0

# 2. wait_press() agrees with stepping can_press()
rng = random.Random(2)
p = Pad(((100, 7), (300, 15)))
for i in range(3000):
    w = p.wait_press("B")
    q = p.copy()
    k = 0
    while q.down["B"] or not q.can_press("B"):
        q.push(())
        k += 1
    if k != w:
        print("wait_press mismatch at", i, k, w)
        ok = False
        break
    r = p.fix(("B",) if rng.random() < 0.5 else ())
    p.push(r)

# 3. reserve: mash before a planned fight, then mash in the fight: the fight gets its presses at full rate
p = Pad()
p.reserve = ((2000, 2320, 64, "B"),)
rows = []
for i in range(2400):
    want = set()
    if p.down["B"]:
        if p.t - p.start["B"] < 2:
            want.add("B")
    elif p.can_press("B"):
        want.add("B")
    r = p.fix(want)
    p.push(r)
    rows.append(r)
st = [i for i, r in enumerate(rows) if "B" in r and (i == 0 or "B" not in rows[i - 1])]
infight = [s for s in st if 2000 <= s <= 2320]
gaps = [b - a for a, b in zip(infight, infight[1:])]
print("reserve: presses before the fight", len([s for s in st if s < 2000]), "in the fight", len(infight),
      "largest gap in the fight", max(gaps))
ok &= len(infight) >= 64 and max(gaps) == 5
print("ALL OK" if ok else "SOMETHING FAILED")

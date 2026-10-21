"""Own check of a route's end events (2026-10-10): replay logs/<route>.inputs.txt from power-on, record every level-byte
change and the landing, then idle 60 frames past the last input and save screenshots around both 13 -> 254 cuts.

    python up15_shots.py <route>     -> logs/fix/<route>_ends.txt, shots/<route>_end_*.png
"""
import hashlib
import sys

from toads.emulator import BizHawk, LOGS_DIR

route = sys.argv[1]
lines = [l for l in (LOGS_DIR / f"{route}.inputs.txt").read_text().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
bad = [(i + 1, l) for i, l in enumerate(lines)
       if ("Left" in bt(l) and "Right" in bt(l)) or ("Up" in bt(l) and "Down" in bt(l)) or ("Start" in bt(l) and i + 1 > 1180)]
e = BizHawk(log_name=f"{route}_shots.log")
out = []
prev_lv, prev_an, landing, cuts = None, None, None, []
want = {}
for i, l in enumerate(lines + [""] * 60):
    s = e.step(bt(l), 1)
    f = i + 1
    if landing is None and s.level == 1 and prev_an == 5 and s.anim == 4:
        landing = f
        e.screenshot(f"{route}_end_landing_{f}")
    if s.level != prev_lv:
        out.append(f"{f}\tlevel byte {prev_lv} -> {s.level}")
        if prev_lv == 13 and s.level == 254:
            cuts.append(f)
            for d in ((0, 12, 30) if len(cuts) == 1 else (0, 12, 20, 40)):
                want[f + d] = f"{route}_end_cut{len(cuts)}_{f}_plus{d}"
    if f in want:
        e.screenshot(want[f])
    if f == len(lines):
        sha = hashlib.sha1(e.ram_all()).hexdigest()
    prev_lv, prev_an = s.level, s.anim
e.close()
t = (cuts[1] - landing) / 60.0988 if len(cuts) > 1 and landing else None
out.append(f"inputs {len(lines)}, banned presses {len(bad)} {bad[:5]}")
out.append(f"landing {landing}, cuts 13->254 {cuts}, sha1 after the last input {sha}")
if t:
    out.append(f"time landing -> second cut: {cuts[1] - landing} frames = {t:.3f} s = {int(t // 60)}:{t % 60:05.2f}; record 749.25 s; "
               f"{'UNDER' if t < 749.25 else 'NOT under'} by {abs(749.25 - t):.2f} s")
(LOGS_DIR / "fix" / f"{route}_ends.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))

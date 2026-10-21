"""EARLY track (2026-10-09): how is Robo-Manus's fight spent in up14?  Replay from cap14_f15000 and log every hit (score
digits $5F4-$5F9), the toad's animation at the hit and the boss's position.   -> logs/fix/early_l8boss.txt"""
from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name="early_l8boss.log")
e.load("cap14_f15000")
out = []
prev = None
first_boss = None
last_anim = None
for i in range(15000, 17330):
    e.step(bt(lines[i]), 1)
    f = i + 1
    m = e.ram_all()
    score = "".join(str(m[0x5F4 + k] & 15) for k in range(6))
    ids = [m[0x3C1 + q] for q in range(15)]
    boss = next((q for q in range(15) if ids[q] == 0x7D), None)
    if boss is not None and first_boss is None:
        first_boss = f
        out.append(f"{f} boss 0x7d appears in slot {boss}")
    tx, th, an, st = m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x3B5], m[0x4B1]
    if an != last_anim and f > 15700 and f < 16900:
        out.append(f"   {f} toad anim {last_anim}->{an} x {tx} h {th} in {lines[i]!r}" + (f" boss x {m[0x3FD + boss] | m[0x3EE + boss] << 8} h {m[0x439 + boss]} anim {m[0x3B5 + boss]}" if boss is not None else ""))
        last_anim = an
    if score != prev:
        bx = (m[0x3FD + boss] | m[0x3EE + boss] << 8, m[0x439 + boss], m[0x3B5 + boss]) if boss is not None else None
        out.append(f"{f} SCORE {prev} -> {score} toad x {tx} h {th} anim {an} boss {bx} level {m[0x10]} timer {m[0x0B]}")
        prev = score
e.close()
open(LOGS_DIR / "fix" / "early_l8boss.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(l for l in out if "SCORE" in l or "appears" in l))

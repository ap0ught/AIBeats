"""Final builder's copy of chain A's u16a_verify.py (log names changed only).
Chain A: a third, independent power-on replay of a route's input file (not assemble.py's code path).

    python u16a_verify.py <route>          reads logs/<route>.inputs.txt  ->  logs/fix/u17f_verify_<route>.txt
Reports: the landing frame ($3B5 5 -> 4 in level 1), every level-byte change with lives / health / score there, both
level-byte 13 -> 254 changes (Queen's speech, T. Bird), the run time from landing to the second one, the RAM SHA-1 after
the last input, and whether the last input is the T. Bird cut frame."""
import hashlib
import sys

from u16a_lib import *

route = sys.argv[1]
lines = [l.rstrip("\n") for l in open(LOGS_DIR / f"{route}.inputs.txt") if not l.startswith("#")]
out = open(FIX / f"u17f_verify_{route}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.write(s + "\n"); out.flush()


e = BizHawk(log_name=f"u17f_verify_{route}.log")
land, prev_an, prev_lv, cuts, changes = None, None, None, [], []
for n, l in enumerate(lines, 1):
    e.step(bt(l), 1)
    m = e.ram(0x10, 2)                                      # level byte, lives
    lv = m[0]
    an = e.byte(0x3B5)
    if land is None and lv == 1 and prev_an == 5 and an == 4:
        land = n
    if prev_lv is not None and lv != prev_lv:
        if lv not in (254, 255) or prev_lv not in (254, 255):
            t = toad(e.ram(0, 0x800))
            changes.append((n, prev_lv, lv, t["lives"], t["hp"], t["score"]))
        if prev_lv == 13 and lv == 254:
            cuts.append(n)
    prev_an, prev_lv = an, lv
h = hashlib.sha1(e.ram(0, 0x800)).hexdigest()
e.close()
log(f"{route}: {len(lines)} inputs replayed from power-on; landing {land}")
for c in changes:
    log(f"  frame {c[0]}: level byte {c[1]} -> {c[2]}; lives {c[3]} health {c[4]} score {c[5]}")
if len(cuts) >= 2 and land:
    run = (cuts[1] - land) / 60.0988
    log(f"{route}: Queen's speech cut {cuts[0]}, T. Bird cut {cuts[1]} ({'the last input' if cuts[1] == len(lines) else 'NOT the last input'}); "
        f"run = {cuts[1] - land} frames = {int(run // 60)}:{run % 60:05.2f}; record 12:29.25 needs the cut on 47102 or earlier: "
        f"{'UNDER' if cuts[1] <= 47102 and land == 2074 else 'NOT under'} by {47103 - cuts[1]} frames; RAM sha1 {h[:8]}")
else:
    log(f"{route}: NOT FINISHED (13 -> 254 changes at {cuts}); RAM sha1 {h[:8]}")

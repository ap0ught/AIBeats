"""The Buzzball's last kick (2026-10-03): from the checkpoint after hit 12 the ball goes off left, comes back low and
hits the standing toad. Scan: wait w1, jump (A held j frames, with an optional direction), land, wait w2, dir+B.
    python l11finish.py  -> logs/pbeam_L11b.json, bookmark L12_start_b"""
import json
import itertools
from toads.emulator import BizHawk, LOGS_DIR
from l11fight import boss, Line

ck = json.load(open("knowledge/l11fight_ck.json"))[0]
e = BizHawk(log_name="l11finish.log")
e.load("L11_start")
L = Line(e)
for b in ck:
    m = L.st(b)
hp0, lives0 = m[0x51A], m[0x11]
base = e.msave()
best = None
# a hit from the ball costs health, not time: the level ends after the kill and the next starts with full health
for w1, lead, kd in itertools.product(range(0, 330, 2), ("", "D", "DD", "J"), ("Right", "Left")):
    e.mload(base)
    L.ins = list(ck)
    m = L.st("", w1)
    if m[0x11] != lives0 or boss(m) is None:
        continue
    if lead == "D":
        L.st(kd); L.st(""); L.st(kd, 3)
    elif lead == "DD":
        L.st(kd); L.st(""); L.st(kd, 8)
    elif lead == "J":
        L.st(kd + "+A", 6)
    m = L.st(kd + "+B")
    got = None
    for _ in range(40):
        bs = boss(m)
        if m[0x11] != lives0:
            break
        if bs is None or bs[2] == 0:
            got = len(L.ins)
            break
        m = L.st("")
    if got and (best is None or got < best[0]):
        best = (got, list(L.ins), (w1, lead, kd))
        print("kill at input", got, best[2], flush=True)
if not best:
    print("no kill found")
    e.close()
    raise SystemExit(1)
e.mload(base)
L.ins = list(ck)
for b in best[1][len(ck):]:
    L.st(b)
print("Buzzball dead at input", len(L.ins), "(old 6710)", flush=True)
for _ in range(1200):
    if e.byte(0x10) != 10:
        break
    L.st("")
for _ in range(150):
    m = e.ram(0, 0x800)
    if m[0x10] == 5 and m[0x51A] == 47:
        break
    L.st("Start", 2)
    L.st("", 18)
for _ in range(400):
    m = e.ram(0, 0x800)
    if m[0x10] == 5 and (m[0x3FD] | m[0x3EE] << 8) == 136 and m[0x439] == 30 and m[0x51A] == 47:
        break
    L.st("")
e.save("L12_start_b")
print("The Revolution start at", len(L.ins), "lives", m[0x11], "(old 7406)", flush=True)
json.dump({"bookmark": "L11_start", "inputs": L.ins,
           "note": "CLINGER-WINGER: the unicycle maze with the Buzzball behind - turning at every arrow (no Up+Down presses). "
                   "The Buzzball is pinned in the corner: a kick every ~40 frames.||" f"{len(L.ins)} frames"},
          open(LOGS_DIR / "pbeam_L11b.json", "w"))
e.close()

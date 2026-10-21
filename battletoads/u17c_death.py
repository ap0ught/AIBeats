"""Track C probe: how long Robo-Manus's death takes behind each stored fight on one climb (kill -> level byte leaves 7, no input).
    python u17c_death.py <climb json> <fight json> [<fight json> ...]   -> logs/fix/u17c_death.txt (appended)"""
import json
import sys

from u17c_lib import *
from early_l8fight import boss, score, F

cj = json.load(open(sys.argv[1]))
log = Log("u17c_death.txt")
e = BizHawk(log_name="u17c_death.log", fields=F)
s = e.load("early_L8_p0")
for b in cj["inputs"]:
    s = e.step(bt(b), 1)
root = e.msave()
for p in sys.argv[2:]:
    fj = json.load(open(p))
    e.mload(root)
    pre = None
    for b in fj["inputs"]:
        pre = s
        s = e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    bpre = boss(pre)
    dead = [(q, m[0x3FD + q], m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x46]
    kill_t = m[0x0B]
    info = f"{p.split('fight_')[-1]}: kill at +{len(fj['inputs'])} attack {fj['attacks'][-1]} $0B {kill_t} toad x {s.x} h {s.height} z {s.z} anim {s.anim}; boss before the blow {bpre}; dead body {dead}"
    left = None
    gone = None
    for k in range(1, 700):
        s = e.step((), 1)
        if gone is None:
            m = e.ram(0, 0x800)
            if not any(m[0x3C1 + q] in (0x46, 0x7D) for q in range(1, 15)):
                gone = k
        if s.level != 7:
            left = k
            break
    log(f"{info}; body gone after {gone}; level byte leaves 7 after {left} -> kill + death {len(fj['inputs']) + (left or 0)}")
e.close()

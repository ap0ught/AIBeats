"""From L4_tas_16770, replay TAS #5093's Level 4 inputs with each banned frame replaced by a legal substitute, and
report how long the toad (x, h) and the objects stay with the TAS (ignoring the walk-plane y the TAS shifts)."""
import sys, itertools
from toads.emulator import BizHawk
from l4tas import load_tas, conv

def banned(b): return (b[0] != "." and b[1] != ".") or (b[2] != "." and b[3] != ".")
def fx(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)
def objs(m): return [(m[0x3C1 + s], m[0x3FD + s] | m[0x3EE + s] << 8, m[0x439 + s]) for s in range(2, 10)]

def run(e, rows, sub, f0=16771, f1=17742, verbose=False):
    e.load("L4_tas_16770")
    first_bad = None; first_obj = None
    for f in range(f0, f1):
        b = rows[f][0]
        if banned(b):
            b2 = sub(f, b)
        else:
            b2 = conv(b)
        e.step(b2, 1)
        m = e.ram(0, 0x800); t = rows[f][1]
        if first_bad is None and fx(m) != fx(t): first_bad = (f, fx(m), fx(t))
        if first_obj is None and objs(m) != objs(t): first_obj = (f, objs(m)[:4], objs(t)[:4])
        if first_bad and first_obj: break
    return first_bad, first_obj

if __name__ == "__main__":
    rows = load_tas()
    e = BizHawk(log_name="l4sub.log")
    for name, sub in (("none", lambda f, b: ()), ("right", lambda f, b: ("Right",)), ("left", lambda f, b: ("Left",)),
                      ("keepR", lambda f, b: ("Right",) + (("Down",) if b[2] != "." else ())),
                      ("drop-lr", lambda f, b: tuple(n for n, c in zip(["Right","Left","Down","Up","Start","Select","B","A"], b) if c != "." and n not in ("Right","Left")))):
        print(name, run(e, rows, sub), flush=True)
    e.close()

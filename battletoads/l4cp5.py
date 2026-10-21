"""Checkpoint 5 from L4n_near5 (TAS #5093's recipe): kill the snowman at x 244 (one hit), stand on its snowball pile
(x~219, h 180) facing left, press B every ~30 frames (each press throws a snowball into the barrier, the next one is
picked up by itself); four throws break the 31-HP barrier."""
import json
from toads.emulator import BizHawk

def objs(m, oid): return [(s, m[0x3FD+s]|m[0x3EE+s]<<8, m[0x439+s], m[0x51A+s]) for s in range(2,15) if m[0x3C1+s] == oid]
def tx(m): return m[0x3FD] | m[0x3EE] << 8

def run(e, k_walk, atk, gap):
    e.load("L4n_near5"); ins = []
    def st(b):
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b); return e.ram(0, 0x800)
    for _ in range(k_walk): m = st("Right")
    for _ in range(2): m = st(atk)
    for _ in range(40):
        m = st("")
        sm = [o for o in objs(m, 0x33) if o[1] < 400]
        if not sm or sm[0][3] == 0: break
    else:
        return None
    # onto the pile, facing left: walk to x<=222 (taps like the TAS), then B cycles
    for _ in range(120):
        m = e.ram(0, 0x800)
        if tx(m) <= 222 and m[0x475] == 0: break
        st("Left" if len(ins) % 2 == 0 else "")
    for _ in range(12):
        m = e.ram(0, 0x800)
        if m[0x585] >= 5: break
        st("B")
        for _ in range(gap): 
            m = st("")
            if m[0x585] >= 5: break
    return ins if e.byte(0x585) >= 5 else None

if __name__ == "__main__":
    e = BizHawk(log_name="l4cp5.log")
    best = None
    for k in range(0, 44, 2):
        for atk in ("B", "Right+B", "Left+B"):
            for gap in (29, 31):
                r = run(e, k, atk, gap)
                if r and (best is None or len(r) < len(best)):
                    best = r; print("k", k, atk, "gap", gap, "cp5 after", len(r), flush=True)
                    json.dump(best, open("knowledge/l4s_L4n_near5_cp5.json", "w"))
    print("best", len(best) if best else None)
    e.close()

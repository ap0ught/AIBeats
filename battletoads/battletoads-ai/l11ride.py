"""Clinger-Winger unicycle controller: follow the TAS's segment list (knowledge/l11_segments.json) legally - hold
the current segment's direction, switch to the next one within D px of the upcoming corner.
    python l11ride.py [D...]   -> reports how far each D gets; the best run's inputs -> knowledge/l11_ride_D.json"""
import json, sys
from toads.emulator import BizHawk, PROJECT
SEGS = json.loads((PROJECT / "knowledge" / "l11_segments.json").read_text())

def pos(r):
    return r[0x3FD] + 256 * r[0x3EE], (r[0x89] + 256 * r[0x8A] + 32768) % 65536 - 32768

def ride(e, D, maxf=6000):
    ins = []; s = 0; prev = pos(e.ram_all()); pre = True
    for k in range(maxf):
        r = e.ram_all(); x, cy = pos(r); an = r[0x3B5]
        if pre and an in (100, 101, 102, 103):
            pre = False
        dx, dy = x - prev[0], cy - prev[1]; prev = (x, cy)
        d = None
        if abs(dx) > abs(dy): d = "Right" if dx > 0 else "Left"
        elif abs(dy) > abs(dx): d = "Up" if dy < 0 else "Down"
        if s + 1 < len(SEGS) and d == SEGS[s + 1][1] and abs(x - SEGS[s + 1][2]) + abs(cy - SEGS[s + 1][3]) <= 24:
            s += 1                                              # turned onto the next segment (near its corner, moving its way)
        btn = (SEGS[s][1],)
        if s + 1 < len(SEGS):
            _, nd, nx, ncy = SEGS[s + 1]
            if abs(x - nx) + abs(cy - ncy) <= D:
                btn = (nd,)
        if pre:
            btn = ("Right",)
        e.step(btn, 1); ins.append("+".join(btn))
        r = e.ram_all()
        if r[0x51A] < 47:
            return ins, ("HURT", k, pos(r), s)
        if not pre and r[0x3B5] not in (100, 101, 102, 103) and s >= len(SEGS) - 1:
            return ins, ("OFF UNICYCLE", k, pos(r), s)
    return ins, ("timeout", pos(e.ram_all()), s)

if __name__ == "__main__":
    e = BizHawk(log_name="l11ride.log")
    for D in [int(v) for v in sys.argv[1:]] or [8, 16, 24, 32]:
        e.load("L11_start"); e.step((), 2)
        ins, out = ride(e, D)
        print("D", D, "->", out, len(ins), "frames", flush=True)
        (PROJECT / "knowledge" / f"l11_ride_{D}.json").write_text(json.dumps(ins))
    e.close()

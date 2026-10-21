"""Level 4 damage boost, the record's way (run 95.3-99.3 of the WR video): at the pit's edge walk back left, then
DASH right so the shaft's ice ball (4 px/frame along the floor) catches the toad at full speed right at the edge.
The knock-down arc then carries it out over the spike pit; it lies on the spikes (invulnerable), gets up, dashes
right and sinks through them. Further right than the walk-in version, so the camera is further right when the next
screen's wall ejection happens.

    python l4air.py            # scan from bookmark L4r_edge; saves knowledge/l4_air_boost.json + bookmark L4r_mid
"""
import itertools
import json

from toads.emulator import BizHawk
from l4eject import tx, h16


def main():
    e = BizHawk(log_name="l4fall.log")
    e.load("L4r_edge")
    root = e.msave()
    m = e.ram(0, 0x800)
    lives0, hp0 = m[0x11], m[0x51A]
    best = None
    for nl, w, bk, b3 in itertools.product(range(4, 28, 2), (0, 2, 4, 6, 8, 10), ("", "Right"), ("Right", "", "Left")):
        e.mload(root)
        seq = []
        hit = None
        out = ("none",)
        xs = []
        up = None
        lie = None
        wrapk = camw = xw = None
        dash0 = 28 + nl + w
        upk = 0
        for k in range(520):
            m = e.ram(0, 0x800)
            if hit is None and m[0x51A] < hp0:
                hit = (k, tx(m), m[0x565])
            if hit is not None:
                if up is None and k > hit[0] + 30 and m[0x3B5] not in (48, 19, 20, 21):
                    up = (k, tx(m), hex(h16(m)), m[0x87] | m[0x88] << 8)
                if up is None:
                    b = bk
                    if m[0x3B5] == 48 and lie is None:
                        lie = (k, tx(m), hex(h16(m)))
                else:
                    b = ("Right", "")[upk] if upk < 2 else ("Right" if wrapk is None else b3)
                    upk += 1
            elif k < 28:
                b = ""
            elif k < 28 + nl:
                b = "Left"
            elif k < dash0:
                b = ""
            else:
                b = ("Right", "")[k - dash0] if k - dash0 < 2 else "Right"
            e.step(tuple(v for v in b.split("+") if v), 1)
            seq.append(b)
            m2 = e.ram(0, 0x800)
            if hit is not None and wrapk is None and h16(m2) < 0x1900:
                wrapk, camw, xw = k, m[0x87] | m[0x88] << 8, tx(m)
            if wrapk is not None and len(xs) < 10:
                xs.append(tx(m2))
            m = m2
            if m[0x11] < lives0 or m[0x51A] == 0:
                out = ("dead", len(seq), tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)
                break
            if wrapk is not None and m[0x475] == 0 and k > wrapk + 9:
                out = ("LAND", len(seq), tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, "hp", m[0x51A])
                break
        print((nl, w, bk, b3), "hit", hit, "lie", lie, "up", up, "wrap", wrapk, xw, camw, xs, out, flush=True)
        if out[0] == "LAND" and out[3] == "0x185e" and 330 < out[2] < 520 and (best is None or out[1] < best[0]):
            best = (out[1], list(seq))
            json.dump(best[1], open("knowledge/l4_air_boost.json", "w"))
            e.save("L4r_mid")
            print("  SAVED L4r_mid", out, flush=True)
    e.close()


if __name__ == "__main__":
    main()

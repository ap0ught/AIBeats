"""Level 4 damage boost: after the ice ball's knock-down at the pit's edge (knowledge/l4_boost_up.json from
L4r_edge), DASH into the spike pit (tap Right, gap, hold Right) so the toad falls with 3 px/frame of drift and the
camera scrolls with it; the wall ejection then leaves it at x 384 on screen and it lands between the two pillars
(h $185e) like the record's run.

    python l4dash.py   -> knowledge/l4_dash_boost.json (inputs from L4r_edge), bookmark L4r_mid
"""
import itertools
import json

from toads.emulator import BizHawk
from l4eject import tx, h16


def main():
    e = BizHawk(log_name="l4fall.log")
    e.load("L4r_edge")
    lives0 = e.byte(0x11)
    seq0 = json.load(open("knowledge/l4_boost_up.json"))
    for b in seq0:
        e.step((b,) if b else (), 1)
    U = e.msave()
    seen = set()
    best = None
    for w, gap, nr, b2, n2, b3 in itertools.product((0, 1, 2, 4), (1, 2, 3), (6, 12, 20, 28, 36, 60), ("", "Left"), (6, 14, 60), ("", "Right", "Left")):
        plan = [""] * w + ["Right"] + [""] * gap + ["Right"] * nr + [b2] * n2 + [b3] * 200
        e.mload(U)
        xs = []
        out = ("none",)
        wrapk = None
        for k, b in enumerate(plan):
            e.step((b,) if b else (), 1)
            m = e.ram(0, 0x800)
            if wrapk is None and h16(m) < 0x1900:
                wrapk = k
                camw = m[0x87] | m[0x88] << 8
            if wrapk is not None and k < wrapk + 8:
                xs.append(tx(m))
            if m[0x51A] == 0 or m[0x11] < lives0:
                out = ("dead", k, tx(m), hex(h16(m)))
                break
            if wrapk is not None and k > wrapk + 8 and m[0x475] == 0:
                out = ("LAND", k, tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, "hp", m[0x51A])
                break
        key = (tuple(xs), out[0], out[2:4])
        if key not in seen:
            seen.add(key)
            print((w, gap, nr, b2, n2, b3), "wrap", wrapk, wrapk and camw, xs, out, flush=True)
        if out[0] == "LAND" and out[3] == "0x185e" and 330 < out[2] < 520 and (best is None or out[1] < best[0]):
            best = (out[1], seq0 + plan[:out[1] + 1])
            json.dump(best[1], open("knowledge/l4_dash_boost.json", "w"))
            e.save("L4r_mid")
            print("  SAVED L4r_mid", out, flush=True)
    e.close()


if __name__ == "__main__":
    main()

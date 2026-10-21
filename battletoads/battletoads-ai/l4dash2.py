"""Level 4 damage boost, the pass through the rock layer under the spike pit. After the knock-down at the pit's
edge (knowledge/l4_boost_up.json from L4r_edge) the toad dashes into the pit (tap Right, gap, hold Right). When its
height wraps into the next screen ($18ff) it is inside rock and is pushed right one 64-px column per frame; this
breadth-first search over the pad (nothing / Left / Right per frame) around that moment looks for a line that
leaves the layer at column 384 or 448 with the camera still on the toad, so it lands between the pillars ($185e).

    python l4dash2.py   -> knowledge/l4_dash_boost.json (inputs from L4r_edge), bookmark L4r_mid
"""
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
    pre = ["Right", ""] + ["Right"] * 60
    n = 0
    for b in pre:                                           # dash until 3 frames before the wrap
        s = e.msave()
        e.step((b,) if b else (), 4)
        w = h16(e.ram(0, 0x800)) < 0x1900
        e.mload(s)
        e.mfree(s)
        if w:
            break
        e.step((b,) if b else (), 1)
        n += 1
    seq1 = seq0 + pre[:n]
    m = e.ram(0, 0x800)
    print("search root: frame", len(seq1), "toad", tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, flush=True)
    layer = [(e.msave(), [])]
    seen = set()
    done = []
    for depth in range(16):
        nxt = []
        for sid, path in layer:
            for b in ("", "Left", "Right"):
                e.mload(sid)
                e.step((b,) if b else (), 1)
                m = e.ram(0, 0x800)
                if m[0x51A] == 0 or m[0x11] < lives0:
                    continue
                k = (tx(m), h16(m), m[0x448], m[0x457], m[0x466], m[0x4C0], m[0x4CF], m[0x87], m[0x4A2], m[0x565])
                if k in seen:
                    continue
                seen.add(k)
                nxt.append((e.msave(), path + [b]))
        for sid, _ in layer:
            e.mfree(sid)
        layer = nxt
        xs = sorted({(tx(e_m), ) for e_m in []})
        print("depth", depth, "states", len(layer), flush=True)
        if len(layer) > 1500:
            break
    # play every leaf out with each of the three pads held
    best = None
    outs = {}
    for sid, path in layer:
        for b in ("", "Left", "Right"):
            e.mload(sid)
            out = None
            tail = []
            for k in range(120):
                e.step((b,) if b else (), 1)
                tail.append(b)
                m = e.ram(0, 0x800)
                if m[0x51A] == 0 or m[0x11] < lives0:
                    out = ("dead", tx(m), hex(h16(m)))
                    break
                if m[0x475] == 0:
                    out = ("LAND", tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)
                    break
            if out is None:
                out = ("air", tx(m), hex(h16(m)))
            key = (out[0], out[1] // 16, out[2])
            if key not in outs:
                outs[key] = (path, b)
                print(out, "path", path, "then", repr(b), flush=True)
            if out[0] == "LAND" and out[2] == "0x185e" and 330 < out[1] < 520:
                total = seq1 + path + tail
                if best is None or len(total) < len(best):
                    best = total
                    json.dump(best, open("knowledge/l4_dash_boost.json", "w"))
                    e.save("L4r_mid")
                    print("  SAVED L4r_mid", out, len(total), flush=True)
    e.close()


if __name__ == "__main__":
    main()

"""Level 3 on the TAS's line all the way to the bikes (2026-10-02). TAS #5093's inputs from the placement (TAS frame
13155), with its two banned Left+Right frames (13920, 14352: an instant dash+jump) replaced by the legal
tap / gap / hold, i.e. one inserted frame each. Reports every rat hit and how the toad's track compares with the
TAS's (shifted by the inserted frames).

    python l3tas2.py [variant]  -> knowledge/l3_tasline.json (inputs from the placement), bookmark L3t_bikes
"""
import json
import sys

from toads.emulator import BizHawk
from l4tas import conv
import l3tas


YFIX = True


def main(variant):
    rows = l3tas.load("tas/ram_l3_1p.txt")
    e = BizHawk(log_name="l3tas.log")
    e.load("L1route_end")
    pre = []
    for k in range(700):
        b = "B" if k % 2 == 0 else ""
        e.step((b,) if b else (), 1)
        pre.append(b)
        if l3tas.placed(e.ram(0, 0x800)):
            break
    ins = []
    shift = 0
    prev = {}
    lives0 = e.byte(0x11)
    f = 13156
    last = max(rows)
    while f <= min(last, 14700):
        b = rows[f][0]
        seq = [conv(b)]
        if l3tas.banned(b):
            keep = tuple(x for x in seq[0] if x not in ("Left", "Right"))
            nxt = conv(rows[f + 1][0])
            d = tuple(x for x in nxt if x in ("Left", "Right"))
            if variant == "gap":
                seq = [tuple(x for x in keep if x != "A"), d + keep]          # gap frame, then direction + A (one frame late)
            elif variant == "dash":
                seq = [(), d, d + keep]                                       # gap, direction (the dash engages), direction + A
            elif variant.startswith("wait"):                                  # idle n (the boot's recovery blocks a dash), tap, gap, direction + A
                n = [int(v) for v in variant[4:].split(",")]
                n = n[min(shift and 1, len(n) - 1)] if len(n) > 1 else n[0]
                seq = [()] * n + [d, (), d + keep]
            elif variant == "dash1":
                seq = [(), d + keep]
            elif variant == "noA":
                seq = [(), d + keep]
            elif variant == "A":
                seq = [keep]
            elif variant == "dirA":
                seq = [d + keep]
            shift += len(seq) - 1
        for btn in seq:
            if YFIX and shift and len(seq) == 1 and btn and rows[f - 1][0] == b == rows[f + 1][0] and "Up" not in btn and "Down" not in btn and "B" not in btn:
                m = e.ram(0, 0x800)                                           # steer the depth back onto the TAS's line while it just holds a direction
                dy = m[0x41B] - rows[f][1][0x41B]
                if m[0x475] != 0 or m[0x439] != 64 or any(m[0x3C1 + q] in (0x47, 0xC7) and m[0x51A + q] > 0 for q in range(2, 15)):
                    dy = 0                                                    # ...but only on the ground and never during a fight
                if abs(dy) >= 2:
                    btn = btn + (("Up",) if dy > 0 else ("Down",))
            e.step(btn, 1)
            ins.append("+".join(btn))
            m = e.ram(0, 0x800)
            rats = {s: (m[0x3FD + s] | m[0x3EE + s] << 8, m[0x51A + s]) for s in range(2, 15) if m[0x3C1 + s] in (0x47, 0xC7)}
            for s, (x, hp) in rats.items():
                if s in prev and prev[s][1] != hp:
                    print(f"input {len(ins)} (TAS f{f}): rat at {x} hp {prev[s][1]} -> {hp}", flush=True)
            prev = rats
        tm = rows[f][1]
        if f % 60 == 0 or l3tas.banned(b):
            print(f"TAS f{f} {b} | ours x {m[0x3FD] | m[0x3EE] << 8} y {m[0x41B]} h {m[0x439]} anim {m[0x3B5]} hp {m[0x51A]} cam {m[0x87] | m[0x88] << 8}"
                  f" | TAS x {tm[0x3FD] | tm[0x3EE] << 8} y {tm[0x41B]} h {tm[0x439]} anim {tm[0x3B5]} cam {tm[0x87] | tm[0x88] << 8} | shift {shift}", flush=True)
        if any(m[0x3C1 + s] == 0x18 for s in range(1, 15)) and (m[0x3FD] | m[0x3EE] << 8) >= 1677:
            print("bikes: input", len(ins), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x41B], "hp", m[0x51A], "lives", m[0x11], "timers", m[0x0B], m[0x0C])
            break
        if m[0x11] < lives0 or m[0x51A] == 0:
            print("died at input", len(ins))
            break
        f += 1
    json.dump(ins, open(f"knowledge/l3_tasline_{variant}.json", "w"))
    e.save(f"L3t_bikes_{variant}")
    print("variant", variant, "pre", len(pre), "inputs", len(ins), "total", len(pre) + len(ins))
    e.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "gap")

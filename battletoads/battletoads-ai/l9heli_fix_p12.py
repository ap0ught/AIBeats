"""Probe 12: on which frames does the corridor mine test for the toad?  For frame-counter offsets d = 0..7 ($0B += d at the start):
 old route from L9c 8279 (mine in slot 4) and our join state T' (mine in slot 7): the old index at which the mine's trigger flag $4FC
 first becomes 128, the toad's x then, and where the toad's track first leaves the old run's."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p12.log")
for bm in ("L9heli_8279", sys.argv[1]):
    for d in range(0, 8):
        e.load(bm); m0 = e.ram(0, 0x800); e.poke(0x0B, (m0[0x0B] + d) & 255)
        trig = None; first = None; slot = None
        for k in range(8279, 8600):
            e.step(bt(ins[OFF + k]), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
            q = [q for q in range(2, 15) if m[0x3C1 + q] == 0x72 and m[0x42A + q] == 23]
            if q and trig is None and m[0x4FC + q[0]] == 128: trig = (k + 1, m[0x3FD] | m[0x3EE] << 8, m[0x0B]); slot = q[0]
            a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A])
            if first is None and a != c: first = (k + 1, a, c)
        print(bm, "d", d, "mine slot", slot, "trigger (old index, toad x, $0B):", trig, "| first track diff", first, flush=True)
e.close()

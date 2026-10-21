"""Track K: room 1 with the pause-free ride on snake 3's 7984-run: K6's inputs with 'Left x8' at index 1576 replaced by idle
(the toad stays 10 px behind the head's coordinate: the head never pauses and turns up 6 frames sooner) and `cut` idle
frames removed after it.  Replays from L4c5_end0 and reports the index the toad appears in room 2 (K6: 1992) for each cut.
    python u16k_r1shift.py <base segment> [cuts=5,6,7] -> logs/fix/u16k_r1shift_<cut>.json (room-1 inputs to the room-2 frame)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

base = sys.argv[1]
cuts = [int(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [5, 6, 7]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
k6 = json.load(open(LOGS_DIR / f"pbeam_{base}.json"))["inputs"]
assert k6[1576:1584] == ["Left"] * 8 and all(b == "" for b in k6[1584:1700])
e = BizHawk(log_name="u16k_r1shift.log")
e.load("L4c5_end0")
for b in k6[:1576]:
    e.step(bt(b), 1)
root = e.msave()
for cut in cuts:
    tail = [""] * 8 + k6[1584 + cut:1992] + [""] * 40
    e.mload(root)
    room2, minhp, cap = None, 99, None
    for j, b in enumerate(tail):
        e.step(bt(b), 1)
        n = 1576 + j + 1
        m = e.ram(0, 0x800)
        x, H, z = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475]
        minhp = min(minhp, m[0x51A])
        if cap is None and z == 0 and H >= 8090 and x >= 360:
            cap = (n, x, H)
        if x == 76 and H < 7600:
            room2 = n
            break
    print(f"cut {cut}: captured {cap} (K6: 1863), toad in room 2 at {room2} (K6 1992), min hp {minhp}", flush=True)
    if room2:
        json.dump({"inputs": k6[:1576] + tail[:room2 - 1576], "room2": room2, "cut": cut}, open(LOGS_DIR / "fix" / f"u16k_r1shift_{cut}.json", "w"))
e.close()

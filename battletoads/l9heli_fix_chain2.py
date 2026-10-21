"""Like l9heli_fix_chain.py but for several bookmarks in one emulator, with Select re-rolls and a lag report.
    python l9heli_fix_chain2.py <edits json or -> <stop old index> <bookmark>[:sel1/sel2...] ...
Per bookmark: the old indices of the lag frames, the first track / health difference, raw frames used from T' (old index 8279) to the stop,
the old index at which the level byte leaves 11, and the object ids at a few indices."""
import json, sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
EDITS = json.load(open(sys.argv[1])) if sys.argv[1] != "-" else []
STOP = int(sys.argv[2])
e = BizHawk(log_name="l9heli_fix_chain2.log")
def okin(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10])
for spec in sys.argv[3:]:
    bm, _, sels = spec.partition(":"); SEL = set(int(v) for v in sels.split("/") if v)
    e.load(bm); t = e.byte(0x0B); raw = 0; first = None; hpd = None; lagat = []; end = None; k = 8279; slots = {}
    while k < STOP:
        ed = [x for x in EDITS if x["A"] == k]
        if ed:
            for b in ed[0]["inputs"]: e.step(bt(b), 1); raw += 1
            k = ed[0]["TGT"]; m = e.ram(0, 0x800); t = m[0x0B]; continue
        b = ins[OFF + k]
        if (k + 1) in SEL: b = (b + ",Select").lstrip(",")
        if k >= 9650:
            e.step(bt(b), 1); raw += 1; m = e.ram(0, 0x800); t = m[0x0B]
        else:
            for _ in range(8):
                e.step(bt(b), 1); raw += 1; m = e.ram(0, 0x800)
                if m[0x0B] != t: break
                lagat.append(k + 1)
            t = m[0x0B]
        k += 1; ref = bytes(R[OFF + k - 1])
        if k in (8300, 8450, 8520, 8600, 8700, 8800, 8900, 9000, 9100, 9300, 9500): slots[k] = (" ".join(f"{m[0x3C1 + q]:02x}" for q in range(2, 15)), " ".join(f"{ref[0x3C1 + q]:02x}" for q in range(2, 15)))
        if end is None and m[0x10] != 11: end = (k, raw)
        if okin(m) != okin(ref):
            if first is None: first = (k, okin(m), okin(ref))
            if hpd is None and okin(m)[3:] != okin(ref)[3:]: hpd = (k, okin(m), okin(ref))
    print(f"{spec}: raw {raw} for old {STOP - 8279} (loss {raw - (STOP - 8279)}), lags {len(lagat)} at {lagat}, first diff {first}, hp/level diff {hpd}, level end (old index, raw) {end}, final level {m[0x10]} x {m[0x3FD] | m[0x3EE] << 8} hp {m[0x51A]} dice {bytes(m[0x25:0x29]).hex()}", flush=True)
    for kk, v in slots.items(): print("   objs", kk, "ours", v[0], "| old", v[1], flush=True)
e.close()

"""Dice re-rolls for the final tank (as rngfit does): Select does nothing in play but changes the CPU time of its frame, which re-rolls the
random numbers.  From a join bookmark + repairs replay to old index START, then for each candidate set of old indices add Select there and
replay the old inputs to the level end; a candidate is good if the toad's health track equals the old run's and the level byte leaves 11.
    python l9heli_fix_reroll.py <bookmark> <edits json> <START> <lo> <hi> [fixed select indices...]
Prints every good single (and, if none, pairs).  Comparison tolerates 1 px of height (the vertical sub-pixel is 3/256 off after the repairs)."""
import json, sys, itertools, random
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BM = sys.argv[1]; EDITS = json.load(open(sys.argv[2])); START, LO, HI = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
FIXED = set(int(v) for v in sys.argv[6:])
e = BizHawk(log_name="l9heli_fix_reroll.log"); e.load(BM); t = e.byte(0x0B)
def lstep(b):
    global t
    for _ in range(8):
        e.step(bt(b), 1); m = e.ram(0, 0x800)
        if m[0x0B] != t: break
    t = m[0x0B]; return m
k = 8279
while k < START:
    ed = [x for x in EDITS if x["A"] == k]
    if ed:
        for b in ed[0]["inputs"]: e.step(bt(b), 1)
        k = ed[0]["TGT"]; t = e.byte(0x0B); continue
    b = ins[OFF + k]
    if (k + 1) in FIXED: b = (b + ",Select").lstrip(",")
    m = lstep(b); k += 1
base = e.msave(); tb = t
def run(sel, verbose=False):
    global t
    e.mload(base); t = tb; first = None; hurt = None; end = None; n = 0
    for k in range(START, 9987):
        b = ins[OFF + k]
        if (k + 1) in sel or (k + 1) in FIXED: b = (b + ",Select").lstrip(",")
        if k >= 9650: e.step(bt(b), 1); m = e.ram(0, 0x800); t = m[0x0B]
        else: m = lstep(b)
        n += 1
        ref = bytes(R[OFF + k])
        a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x51A], m[0x585]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x51A], ref[0x585])
        if k < 9590 and hurt is None and (a[2] != c[2] or abs(a[0] - c[0]) > 2 or abs(a[1] - c[1]) > 2): hurt = (k + 1, a, c); break
        if end is None and m[0x10] != 11: end = (k + 1, m[0x10])
    return hurt, end, (m[0x10], m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x51A], m[0x11])
h0 = run(set()); print("no select:", h0, flush=True)
good = []
for s in range(HI, LO - 1, -1):
    h = run({s})
    if h[0] is None: good.append((s,)); print("GOOD single Select at old index", s, h, flush=True)
    elif h[0][0] > (h0[0][0] if h0[0] else 0) + 40: print("  later failure with Select at", s, h[0], flush=True)
if not good:
    rnd = random.Random(5); tries = 0
    while tries < 400 and len(good) < 3:
        c = set(rnd.sample(range(LO, HI + 1), rnd.choice((2, 2, 3)))); tries += 1
        h = run(c)
        if h[0] is None: good.append(tuple(sorted(c))); print("GOOD Select set", sorted(c), h, flush=True)
print("good:", good[:10], flush=True)
e.close()

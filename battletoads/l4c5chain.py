"""Level 4 with the TAS-style checkpoint 5 (2026-10-04): L4nm up to the switchback sprint (up6 frame 6800), the new cp5 piece
(knowledge/l4c5_throws0.json: TAS inputs with a landing re-sync, then two-throw scan), the new edge piece (l4s_L4c5_bardead0.json),
then a wait w and the OLD inputs from the old edge state on (L4nm[j0:]: the ice-ball knock-down, the boost, the loader, the lift...).
    python l4c5chain.py  -> logs/pbeam_L4c5.json (bookmark L3skipu_end_r), bookmark L4c5_end0 (the toad set down in Karnath's Lair)"""
import json, os, sys
from toads.emulator import BizHawk, LOGS_DIR
d = json.load(open(LOGS_DIR / "pbeam_L4nm.json")); old = [x.replace(",", "+") for x in d["inputs"]]
fall = [x.replace(",", "+") for x in json.load(open("knowledge/l4_boost_fall.json"))]
def find(seq, sub):
    for i in range(len(seq) - len(sub) + 1):
        if seq[i:i + len(sub)] == sub: return i
j0 = find(old, fall[:60])
print("old fall piece starts at L4nm index", j0, "(up6 frame", j0 + 4733, ")", flush=True)
def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x42A], m[0x475], m[0x3B5], m[0x565], m[0x4A2] & 0x40, m[0x448], m[0x466], m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)
e = BizHawk(log_name="l4c5chain.log"); e.load(d["bookmark"])
ref = {}
for i, b in enumerate(old):
    e.step(tuple(v for v in b.split("+") if v), 1)
    if i + 1 in (j0, j0 + len(fall)): ref[i + 1] = toad(e.ram(0, 0x800))
m = e.ram(0, 0x800); ref["end"] = (m[0x10], toad(m)); print("old: at j0", ref[j0], "after the fall", ref[j0 + len(fall)], "end", ref["end"], "len", len(old), flush=True)
cp5 = json.load(open("knowledge/l4c5_throws0.json"))["inputs"]
edge = json.load(open("knowledge/l4s_L4c5_bardead0.json")); edge = edge["inputs"] if isinstance(edge, dict) else edge
pre = old[:6800 - 4733 + 1] + cp5 + [""] * 2 + edge          # (l4s pieces start 2 idle frames after their bookmark)          # L4c5_6800 = after the input of index 2067 (frame f = 4733 + i)
e.load(d["bookmark"])
for b in pre: e.step(tuple(v for v in b.split("+") if v), 1)
m = e.ram(0, 0x800); print("new edge state:", toad(m), "hp", m[0x51A], "lvl", m[0x10], "after", len(pre), "inputs (old j0 =", j0, ")", flush=True)
e.save("L4c5_edge2"); base = e.msave()
K_HIT = 7823 - 4733                                              # the old knock-down frame's input index (up6 7823: hp 47 -> 31)
e.load(d["bookmark"])
for b in old[:K_HIT]: e.step(tuple(v for v in b.split("+") if v), 1)
m = e.ram(0, 0x800); ref_hit = toad(m); print("old at the knock-down (index", K_HIT, "):", ref_hit, "hp", m[0x51A], "state", m[0x4B1], flush=True)
tail = old[K_HIT:]
best = None
J_FALLEND = j0 + len(fall)                                        # the old fall piece's end (mid-fall at (128,243,24)); the open-loop pieces follow from here
tail2 = old[J_FALLEND:]
for w, r, lie in [(w, r, lie) for w in range(0, 8) for r in (4, 5, 6, 7) for lie in (118, 124, 130, 137)]:
    e.mload(base); e.step((), w); e.step(("Right",), r); ins0 = [""] * w + ["Right"] * r; n = 0
    while e.byte(0x51A) >= 47 and e.byte(0x565) and n < 90 and (e.byte(0x3FD) | e.byte(0x3EE) << 8) < 191: e.step((), 1); ins0.append(""); n += 1
    m = e.ram(0, 0x800)
    if m[0x51A] >= 47:
        if lie == 118: print(f"w {w} r {r}: not hit (x {m[0x3FD] | m[0x3EE] << 8})", flush=True)
        continue
    xh = m[0x3FD] | m[0x3EE] << 8
    e.step((), lie); ins0 += [""] * lie                           # lying, getting up (the old route waited 137)
    m = e.ram(0, 0x800); up = toad(m); k = 0
    while (e.byte(0x3FD) | e.byte(0x3EE) << 8) < 192 and e.byte(0x475) == 0 and k < 60: e.step(("Right",), 1); ins0.append("Right"); k += 1
    m = e.ram(0, 0x800); off = toad(m); got = None
    for t in range(200):
        b = ("Left",) if t < 27 else ()
        e.step(b, 1); ins0.append("+".join(b)); m = e.ram(0, 0x800)
        if m[0x11] < 2: break
        if toad(m)[:3] == (128, 243, 24): got = t; break
    print(f"w {w} r {r} lie {lie}: hit at x {xh}; up {up[:5]}; stepped off after {k} Right at {off[:5]}; mid-fall match {'at +' + str(got) if got is not None else 'NO (end ' + str(toad(m)[:5]) + ' lives ' + str(m[0x11]) + ')'}", flush=True)
    if got is None: continue
    for i2, b in enumerate(tail2):
        e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
        if m[0x11] < 2: print("   died in the old tail at", i2, flush=True); break
    m = e.ram(0, 0x800); print(f"   full old tail: lvl {m[0x10]} toad {toad(m)[:5]} (old end {ref['end']})", flush=True)
    if m[0x10] == 8:
        best = ins0; e.save("L4c5_end0"); break
if best is not None:
    ins = pre + best + tail2
    json.dump({"bookmark": d["bookmark"], "inputs": ins, "slack": d.get("slack", 0), "note": d.get("note", "")}, open(LOGS_DIR / "pbeam_L4c5.json", "w"))
    print("saved pbeam_L4c5.json:", len(ins), "frames (L4nm", len(old), "; saves", len(old) - len(ins), ")", flush=True)
e.close()

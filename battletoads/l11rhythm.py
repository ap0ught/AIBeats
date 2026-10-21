"""The Buzzball on the TAS's rhythm (2026-10-03): after the opening (l11fight's TAS inputs, shift -2: first hit at
input 5668), press B exactly every P frames with a lead-in that keeps the toad near x 1744 (Left x n, Right, B) and
check the ball loses 16 each time; small per-hit scans (n, and +-2 frames) when the strict rhythm misses.
    python l11rhythm.py  -> logs/pbeam_L11c.json if it beats 6417 (the kill frame of L11b)"""
import json, itertools
from toads.emulator import BizHawk, LOGS_DIR
from l11fight import boss, Line, tas_inputs
old = [b.replace(",", "+") for b in json.load(open(LOGS_DIR / "pbeam_L11a.json"))["inputs"]]
e = BizHawk(log_name="l11rhythm.log"); e.load("L11_start"); L = Line(e)
for b in old:
    m = L.st(b)
    if boss(m): break
op = tas_inputs(68570, 68647)[2:]                             # shift -2 (l11fight's finding)
for b in op: m = L.st(b)
hp0, lives0 = m[0x51A], m[0x11]
# ride the opening to its first hit, then the second (the TAS's 'ri, B' at +41)
for _ in range(60):
    m = L.st("")
    if boss(m) and boss(m)[2] < 207: break
print("hit 1 at input", len(L.ins), "boss", boss(m), "toad", m[0x3FD] | m[0x3EE] << 8, flush=True)
lastB = len(L.ins) - 1
hits = 1
while hits < 13:
    base = e.msave(); n0 = len(L.ins); hp = boss(m)[2]; found = None
    for P, lead in itertools.product((45, 44, 46, 43, 47, 42, 48, 40, 50, 52, 55), ("Right", "", "Left|Right", "Left|Left|Right", "Left|Left|Left|Right", "Left|Left|Left|Left|Left|Right", "Right||Right", "Right||Right|Right|Right")):
        e.mload(base); del L.ins[n0:]
        pre = [x for x in lead.split("|")] if lead else []
        wait = lastB + P - len(pre) - len(L.ins)
        if wait < 0: continue
        m = L.st("", wait)
        for x in pre: m = L.st(x)
        m = L.st("B"); got = None
        for k in range(30):
            if m[0x51A] < hp0 or m[0x11] != lives0: break
            bs = boss(m)
            if bs is None or bs[2] <= hp - 16: got = k; break
            m = L.st("")
        if got is not None:
            x = m[0x3FD] | m[0x3EE] << 8
            if found is None or abs(x - 1746) < abs(found[2] - 1746) - 3 or (abs(x - 1746) <= abs(found[2] - 1746) + 3 and P < found[0]):
                found = (P, lead, x, list(L.ins), bs[2] if bs else 0)
        if found and P == 45 and abs(found[2] - 1748) <= 4: break
    if not found:
        print("no hit", hits + 1, "with any rhythm", flush=True); break
    P, lead, x, ins, left = found
    e.mload(base); L.ins = list(ins[:n0])
    for b in ins[n0:]: m = L.st(b)
    hits += 1; lastB = n0 + (lastB + P - n0)                    # the B press frame
    lastB = len([1 for _ in ins]) - 1 - (len(ins) - 1 - ins.index("B", n0) if "B" in ins[n0:] else 0)
    lastB = ins.index("B", n0)
    print(f"hit {hits}: period {P} lead {lead!r} toad x {x} ball hp {left} at input {len(L.ins)}", flush=True)
if hits == 13:
    print("dead at", len(L.ins), "(L11b: 6417)", flush=True)
    for _ in range(1200):
        if e.byte(0x10) != 10: break
        L.st("")
    for _ in range(150):
        m = e.ram(0, 0x800)
        if m[0x10] == 5 and m[0x51A] == 47: break
        L.st("Start", 2); L.st("", 18)
    for _ in range(400):
        m = e.ram(0, 0x800)
        if m[0x10] == 5 and (m[0x3FD] | m[0x3EE] << 8) == 136 and m[0x439] == 30 and m[0x51A] == 47: break
        L.st("")
    print("The Revolution start at", len(L.ins), "(L11b 7112)", flush=True)
    json.dump({"bookmark": "L11_start", "inputs": L.ins, "note": "CLINGER-WINGER: the unicycle maze with the Buzzball behind - turning at every arrow (no Up+Down presses). The Buzzball is pinned in the corner: a kick every 45 frames.||" f"{len(L.ins)} frames"}, open(LOGS_DIR / "pbeam_L11c.json", "w"))
e.close()

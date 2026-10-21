"""The Buzzball by the TAS's own inputs with local repairs (2026-10-05). The opening (TAS 68570-68647, shift -2 from the boss's
appearance on L11c) lands hit 1 like l11fight3.py; from there the TAS's inputs continue (Left+Right stripped). Whenever a TAS press
that should hit (the TAS's hp drops are known from tas/watch_1p_l11.txt hp7 column? no - we detect our own hp drops) misses, i.e. no
hp drop within 30 frames of a B press, rewind to that press and try waits 1..24 (idle frames inserted before it) and lead-ins; keep the
first that hits; continue. -> logs/pbeam_L11e.json when the ball dies and the toad is set down in Level 12."""
import json, os, re
from toads.emulator import BizHawk, LOGS_DIR
from l11fight import tas_inputs, boss, Line
seg = json.load(open(LOGS_DIR / "pbeam_L11c.json")); old = [b.replace(",", "+") for b in seg["inputs"]]
def legal(b): return "+".join(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
e = BizHawk(log_name="l11tas.log"); e.load(seg["bookmark"]); L = Line(e)
for b in old:
    m = L.st(b)
    if boss(m): break
print("boss at input", len(L.ins), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "boss", boss(m), flush=True)
hp0, lives0 = m[0x51A], m[0x11]
op = tas_inputs(68570, 68647); sh = int(os.environ.get("L11_SHIFT", -2))
L.st("", max(0, sh))
for b in op[max(0, -sh):]: m = L.st(legal(b))
tas = [legal(b) for b in tas_inputs(68648, 69300)]
print("after the opening: boss", boss(m), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], flush=True)
hits = []; last_hp = boss(m)[2]; i = 0; repairs = []
sid = e.msave(); n0 = len(L.ins)
while i < len(tas):
    b = tas[i]
    if "B" in b:                                                  # a kick: it must land within 30 frames, else repair
        save = e.msave(); nh = len(L.ins); found = None
        for w in [0] + list(range(1, 25)) + [-1, -2, -3, -4]:
            e.mload(save); del L.ins[nh:]
            if w > 0: L.st("", w)
            k = max(0, w)
            ins_try = []
            if w < 0:                                              # earlier: replace the last -w frames (they are idle/direction) by the kick
                pass
            got = None
            for j in range(i, min(i + 40, len(tas))):
                m = L.st(tas[j]); bs = boss(m)
                if m[0x51A] < hp0 or m[0x11] != lives0: break
                if bs is None or bs[2] < last_hp: got = (j, bs[2] if bs else 0); break
            if got and (got[1] <= last_hp - 16 or got[1] == 0):
                found = (w, got); break
        if found is None:
            print(f"press {i} (TAS {68648 + i}): no repair lands a hit; hits so far {len(hits)} at {hits}", flush=True); break
        w, (j, hpn) = found
        if w: repairs.append((i, w))
        hits.append((len(L.ins) - n0, hpn)); last_hp = hpn
        print(f"hit {len(hits)} at +{hits[-1][0]} hp {hpn} (wait {w}) toad {m[0x3FD] | m[0x3EE] << 8} ball {boss(m)[:2] if boss(m) else None}", flush=True)
        i = j + 1
        if hpn == 0: break
        continue
    m = L.st(b); i += 1
    if m[0x51A] < hp0 or m[0x11] != lives0: print("HURT at TAS", 68648 + i, flush=True); break
print("hits", len(hits), "fight frames", len(L.ins) - n0, "repairs", repairs, flush=True)
if hits and hits[-1][1] == 0:
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
    e.save("L11e_end0"); print("Level 12 placement at", len(L.ins), "(L11c", len(old), ")", flush=True)
    json.dump({"bookmark": seg["bookmark"], "inputs": L.ins, "slack": seg.get("slack", 0), "note": seg.get("note", "")}, open(LOGS_DIR / "pbeam_L11e.json", "w"))
e.close()

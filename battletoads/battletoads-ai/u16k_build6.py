"""Track K: build the Level 6 segment K6 = L6c[0:2022] (room 1, to the frame the toad appears in the warp room) + the new
warp-room line (sprint jump at the snake, over its rising head, flight to the portal ledge) + A,B alternating mash to
the Level 8 placement.  No Start anywhere in the new part (L6c's own warp mash had four Start pairs).

    python u16k_build6.py <out segment name> <line json>     line json = {inputs: [...]} from the room root (up14 frame 11910)
    -> logs/pbeam_<out>.json (bookmark L4c5_end0), states/<out>_end0b.State (bookmark replay), logs/fix/u16k_build6_<out>.txt

Steps: (1) reference = L6c replayed from L4c5_end0: portal frame, placement detector, end state; (2) the new line to the
portal; (3) mash scan: start offset after the portal contact x who presses first, each played to the placement, the
earliest placement wins (ties: the latest start); (4) the chosen inputs replayed in one piece from the bookmark and
compared with L6c's end state (toad, health, lives, score).
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

out = sys.argv[1]
line = json.load(open(sys.argv[2]))["inputs"]
CUT = 2022
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
old = json.load(open(LOGS_DIR / "pbeam_L6c.json"))
old_ins = old["inputs"]
logf = open(LOGS_DIR / "fix" / f"u16k_build6_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n")
    logf.flush()


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], rtn=m[0x23] | m[0x24] << 8, score="".join(str(d) for d in m[0x5F4:0x5FA]))


class Det:
    """placement in Level 8: level byte 7, then toad hp 0 and x 0, then hp > 0 and x > 0 (early_mash.py's detector)"""

    def __init__(self):
        self.stage, self.portal, self.contact, self.minhp, self.lives = 0, None, None, 99, None

    def feed(self, m, n):
        t = toad(m)
        if t["level"] == 8:
            self.minhp = min(self.minhp, t["hp"])
            self.lives = t["lives"] if self.lives is None else min(self.lives, t["lives"])
            if self.portal is None and t["rtn"] == 0xE50D:
                self.portal = n
            if self.contact is None and n > CUT and t["x"] >= 410 and t["spd"] == 0 and t["z"] == 0 and t["H"] & 0xFF == 7518 & 0xFF:
                self.contact = n
        if self.stage == 0 and t["level"] == 7:
            self.stage = 1
        if self.stage == 1 and t["hp"] == 0 and t["x"] == 0:
            self.stage = 2
        if self.stage == 2 and t["hp"] > 0 and t["x"] > 0:
            self.stage = 3
            return True
        return False


e = BizHawk(log_name=f"u16k_build6_{out}.log")

# ---- 1. the reference
e.load("L4c5_end0")
d = Det()
placed_ref, root_ref = None, None
for n, b in enumerate(old_ins, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if n == CUT:
        root_ref = toad(m)
    if d.feed(m, n) and placed_ref is None:
        placed_ref = n
m_ref = bytes(e.ram(0, 0x800))
log(f"reference L6c: {len(old_ins)} inputs; room root (after {CUT}) {root_ref}; portal contact {d.contact} (r+{d.contact - CUT}), "
    f"routine $E50D at {d.portal} (r+{d.portal - CUT}), placement at {placed_ref}; min hp {d.minhp}, lives {d.lives}; end {toad(m_ref)}")
assert placed_ref == len(old_ins), "the detector does not fire on L6c's last frame"
ref_contact, ref_portal = d.contact, d.portal

# ---- 2. the new line to the portal
e.load("L4c5_end0")
d = Det()
pre = old_ins[:CUT] + list(line)
contact_n = None
for n, b in enumerate(pre, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    d.feed(m, n)
    if d.contact and contact_n is None:
        contact_n = n
        at_contact = e.msave()
    if d.portal:
        break
t = toad(m)
assert d.portal and contact_n, f"the new line does not reach the portal: {t}"
log(f"new line: portal contact at {contact_n} (r+{contact_n - CUT}; L6c r+{ref_contact - CUT}), routine $E50D at {d.portal} (r+{d.portal - CUT}; "
    f"L6c r+{ref_portal - CUT}); min hp {d.minhp}, lives {d.lives}; {t}")
assert d.minhp == 47 and t["lives"] == root_ref["lives"], "hurt on the way"
base = pre[:contact_n]

# ---- 3. the mash
best = None
for start, first in [(s, f) for s in (0, 2, 4, 8, 12, 14, 15, 16, 17, 18, 20, 24, 30, 40, 60, 90, 120, 150) for f in ("A", "B")]:
    e.mload(at_contact)
    dd = Det()
    dd.stage = 0
    tail, placed = [], None
    for j in range(700):
        if j < start:
            b = ""
        else:
            b = first if (j - start) % 2 == 0 else ("B" if first == "A" else "A")
        e.step(bt(b), 1)
        tail.append(b)
        if dd.feed(e.ram(0, 0x800), contact_n + j + 1):
            placed = contact_n + j + 1
            break
    log(f"  mash from contact+{start} starting with {first}: placement at {placed}")
    if placed and (best is None or placed < best[0] or (placed == best[0] and start > best[1])):
        best = (placed, start, first, list(tail))
assert best, "no mash reaches the placement"
log(f"chosen mash: contact+{best[1]} starting with {best[2]} -> placement at {best[0]} (L6c: {placed_ref}; saves {placed_ref - best[0]})")
new = base + best[3]
assert len(new) == best[0]
bad = [i for i, b in enumerate(new[CUT:], CUT) if "Start" in b or ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)]
assert not bad, f"banned presses in the new part at {bad[:5]}"

# ---- 4. one piece from the bookmark
e.load("L4c5_end0")
d = Det()
placed = None
for n, b in enumerate(new, 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    if d.feed(m, n) and placed is None:
        placed = n
m_new = bytes(e.ram(0, 0x800))
a, b_ = toad(m_ref), toad(m_new)
diff = [i for i in range(0x800) if m_ref[i] != m_new[i]]
log(f"one-piece replay from L4c5_end0: {len(new)} inputs, placement at {placed}; end {b_}")
log(f"L6c end: {a}")
log(f"RAM bytes that differ from L6c's end state: {len(diff)}: {[hex(i) for i in diff[:40]]}")
ok = placed == len(new) and all(a[k] == b_[k] for k in ("level", "x", "H", "hp", "lives", "score")) and d.minhp == 47
log(f"VERIFIED {ok}: frames saved {len(old_ins) - len(new)}")
if ok:
    e.save(out + "_end0b")
    note = ("KARNATH'S LAIR. Room 1: three snakes, their heads pause at corners and lift you; the exit is a ledge three screens up. "
            "Warp room: a sprint jump at the rising snake (tap Right, let go, Right+A on the same frame keeps the run speed through the grab), "
            "climb with Right+A held, over the snake's head while it still rises and a 3-pixel-a-frame flight over the first star to the portal's ledge."
            "||The record's line, read off his video frame by frame; our jump comes 16 frames earlier than his")
    json.dump({"bookmark": "L4c5_end0", "inputs": new, "note": note, "rerolls": [], "slack": 0}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    json.dump({"segment": out, "len": len(new), "old_len": len(old_ins), "frames_saved": len(old_ins) - len(new), "contact_r": contact_n - CUT,
               "portal_r": d.portal - CUT if d.portal else None, "ref_contact_r": ref_contact - CUT, "ref_portal_r": ref_portal - CUT,
               "mash": [best[1], best[2]], "ram_diff": [hex(i) for i in diff]}, open(LOGS_DIR / "fix" / f"u16k_build6_{out}.json", "w"))
    log(f"wrote logs/pbeam_{out}.json and states/{out}_end0b.State")
e.close()

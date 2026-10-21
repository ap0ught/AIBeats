"""Level 11's Buzzball, the TAS's way (2026-10-02; 2026-10-05: on any segment - env L11_SEG (L11c), L11_OUT (L11d); ends at the toad set down in Level 12 as <OUT>_end0).

Our old fight (a damage-ranked beam) landed 13 kicks in ~985 frames: after a few hits the ball got out of the corner
and every kick had to chase it. The 1-player TAS (tas/watch_1p_l11.txt, frames 68569-69133) needs 564: one jump
left, a kick on the way back, then it stands at x~1744 and presses [direction, B] every 45 frames - the ball,
pinned at the right wall (x 1774), bounces straight back into every kick. Its Left+Right frames are replaced
by a scan: after each hit, a few waits and lead-in presses are tried on savestates and the earliest next hit that
leaves the toad unhurt is kept (small beam).

    python l11fight.py     -> logs/pbeam_L11b.json (bookmark L11_start, like pbeam_L11a.json), bookmarks L12_load/L12_start untouched
"""
import json
import os
import re

from toads.emulator import BizHawk, LOGS_DIR

KEYMAP = {"le": "Left", "ri": "Right", "up": "Up", "do": "Down", "A": "A", "B": "B", "se": "Select", "st": "Start"}


def tas_inputs(a, b):
    rows = {int(l.split()[0][1:]): l for l in open("tas/watch_1p_l11.txt") if " x=" in l}
    out = []
    for f in range(a, b + 1):
        p = re.search(r"p1=(\S+)", rows[f]).group(1)
        keys = re.findall(r"le|ri|up|do|se|st|A|B", p) if p != "-" else []
        out.append("+".join(KEYMAP[k] for k in keys))
    return out


def boss(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x7B:
            return m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q]
    return None


class Line:
    def __init__(self, e):
        self.e = e
        self.ins = []

    def st(self, b, n=1):
        for _ in range(n):
            self.e.step(tuple(v for v in b.split("+") if v), 1)
            self.ins.append(b)
        return self.e.ram(0, 0x800)


def main():
    SEG = os.environ.get("L11_SEG", "L11c"); OUT = os.environ.get("L11_OUT", "L11d")
    segd = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json")); old = [b.replace(",", "+") for b in segd["inputs"]]; ROOT = segd["bookmark"]
    e = BizHawk(log_name=f"l11fight_{OUT}.log")
    e.load(ROOT)
    L = Line(e)
    for b in old:
        m = L.st(b)
        if boss(m):
            break
    hp0, lives0 = (0 if os.environ.get('L11_NOHP') else m[0x51A]), m[0x11]
    print("Buzzball appears at input", len(L.ins), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "an", m[0x3B5], "boss", boss(m), flush=True)

    # opening: the TAS's own inputs 68570..68647 (legal), scanned over a small shift
    op = tas_inputs(68570, 68647)
    base = e.msave()
    n0 = len(L.ins)
    best = None
    for sh in range(-3, 5):
        e.mload(base)
        del L.ins[n0:]
        L.st("", max(0, sh))
        hits = []
        for b in op[max(0, -sh):]:
            m = L.st(b)
            bs = boss(m)
            if bs and (not hits or bs[2] < hits[-1][1]) and bs[2] < 207:
                hits.append((len(L.ins), bs[2]))
        for _ in range(40):
            m = L.st("")
            bs = boss(m)
            if bs and hits and bs[2] < hits[-1][1]:
                hits.append((len(L.ins), bs[2]))
                break
        ok = m[0x51A] >= hp0 and m[0x11] == lives0
        print("opening shift", sh, "hits", hits, "unhurt" if ok else "HURT", flush=True)
        if ok and hits and hits[0][1] == 191 and (best is None or hits[0][0] < best[0]):
            best = (hits[0][0], sh, list(L.ins[n0:hits[0][0]]))
    if best is None:
        print("opening failed")
        e.close()
        return
    e.mload(base)
    del L.ins[n0:]
    for b in best[2]:
        m = L.st(b)
    print("opening: shift", best[1], "first hit at input", len(L.ins), "boss", boss(m), "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], flush=True)

    # the loop: beam over (lead-in, wait) per hit
    LEADS = ["", "Right", "Right|Right", "Right||Right", "Left|Right", "Left", "Left|Left", "Left||Left", "Left||Left|Left|Left", "Left|Left|Right", "Left|Left|Left|Right",
             "Left|Left|Left|Left|Left|Right", "|".join(["Left"] * 8 + ["Right"]), "|".join(["Left"] * 12 + ["Right"]),
             "|".join(["Left"] * 16 + ["Right"]), "|".join(["Left"] * 20 + ["Right"]), "Left||Right", "Right||Right|Right|Right",
             "Right||Right|Right|Right|Right|Right|Right|Right"]
    if os.environ.get("L11_SELECT"):                               # Select presses re-roll the dice (the queen's moves; maybe the ball's bounce)
        LEADS += ["Select", "Select|Select", "Select|Left", "Left|Select", "Select|Select|Select|Select", "Select|Right"]
    XKEEP = int(os.environ.get("L11_XKEEP", 1748))                                                # the TAS stands at 1744: nearer the wall the kicks stop landing
    beam = [(len(L.ins), e.msave(), list(L.ins), boss(m)[2])]
    CK = f"knowledge/l11fight_{OUT}_ck.json"
    if os.path.exists(CK):                                      # resume: the beam's lines so far
        beam = []
        for ins in json.load(open(CK)):
            e.load(ROOT)
            L.ins = []
            for x in ins:
                m = L.st(x)
            beam.append((len(L.ins), e.msave(), list(L.ins), boss(m)[2]))
        print("resumed", [(n[0], n[3]) for n in beam], flush=True)
    WIDTH = int(os.environ.get('L11_WIDTH', 6))
    WAITMAX = 80
    while True:
        done = [n for n in beam if n[3] == 0]
        if done:
            break
        nxt = []
        for f, sid, ins, hp in beam:
            found = set()
            e.mload(sid)
            L.ins = list(ins)
            for w in range(0, WAITMAX):
                if len(found) == len(LEADS):
                    break
                m = e.ram(0, 0x800)
                if boss(m) is None or boss(m)[2] < hp or m[0x51A] < hp0 or m[0x11] != lives0:
                    break
                here = e.msave()
                nh = len(L.ins)
                for lead in LEADS:
                    if lead in found:
                        continue
                    e.mload(here)
                    del L.ins[nh:]
                    for b in (lead.split("|") if lead else []):
                        m = L.st(b)
                    m = L.st("B")
                    got = None
                    for _ in range(26):
                        bs = boss(m)
                        if m[0x51A] < hp0 or m[0x11] != lives0:
                            break
                        if bs is None or bs[2] < hp:
                            got = bs[2] if bs else 0
                            break
                        m = L.st("")
                    if got is None or got > hp - 16:              # (only clean 16-point kicks: a 2-point graze means the ball hit us)
                        continue
                    found.add(lead)
                    nxt.append((len(L.ins), e.msave(), list(L.ins), got, lead, w, (m[0x3FD] | m[0x3EE] << 8, m[0x439], boss(m)[:2] if boss(m) else None)))
                e.mload(here)
                e.mfree(here)
                del L.ins[nh:]
                L.st("")
        if not nxt:
            if WAITMAX < 700:
                WAITMAX = 700
                print("no next hit within 80 frames: looking up to 700", flush=True)
                continue
            print("no next hit from any beam state")
            break
        WAITMAX = 80
        good = [n for n in nxt if n[6][0] <= XKEEP + 4 and n[6][2] and n[6][2][0] >= 1766]   # the toad stays back, the ball stays at the wall
        if good or os.environ.get('L11_STRICT'):
            for n in nxt:
                if n not in good:
                    e.mfree(n[1])
            nxt = good
        nxt.sort(key=lambda n: (n[3], n[0] + 10 * max(0, n[6][0] - XKEEP) + (40 if n[6][2] and n[6][2][0] < 1768 else 0)))
        keep, seen = [], set()
        low = sorted((n for n in nxt if n[3] == nxt[0][3] and n[0] <= nxt[0][0] + 10), key=lambda n: n[6][0])[:2]   # and the two that stand furthest from the wall
        for n in nxt:                                           # different toad positions, not four copies of one line
            if n[6] in seen or (len(keep) >= WIDTH - 2 and n not in low):
                e.mfree(n[1])
                continue
            seen.add(n[6])
            keep.append(n)
        json.dump([n[2] for n in keep], open(CK, "w"))
        for n in beam:
            e.mfree(n[1])
        beam = [n[:4] for n in keep]
        print("hit ->", [(n[0], n[3], n[4], n[5], n[6]) for n in keep], flush=True)
    win = min((n for n in beam if n[3] == 0), key=lambda n: n[0], default=None)
    if not win:
        e.close()
        return
    e.mload(win[1])
    L.ins = list(win[2])
    print("Buzzball dead at input", len(L.ins), "(old 6710)", flush=True)
    for _ in range(1200):                                        # the ending, as l11.py did it
        if e.byte(0x10) != 10:
            break
        L.st("")
    print("level byte left 10 at", len(L.ins), flush=True)
    for _ in range(150):
        m = e.ram(0, 0x800)
        if m[0x10] == 5 and m[0x51A] == 47:
            break
        L.st("Start", 2)
        L.st("", 18)
    for _ in range(400):
        m = e.ram(0, 0x800)
        if m[0x10] == 5 and (m[0x3FD] | m[0x3EE] << 8) == 136 and m[0x439] == 30 and m[0x51A] == 47:
            break
        L.st("")
    e.save(f"{OUT}_end0")
    print("The Revolution start at", len(L.ins), "lives", m[0x11], "(old 7406)", flush=True)
    json.dump({"bookmark": ROOT, "inputs": L.ins, "slack": segd.get("slack", 0),
               "note": "CLINGER-WINGER: the unicycle maze with the Buzzball behind - turning at every arrow (no Up+Down presses). "
                       "The Buzzball itself is pinned in the corner: one kick every 45 frames.||" f"{len(L.ins)} frames"},
              open(LOGS_DIR / f"pbeam_{OUT}.json", "w"))
    e.close()


if __name__ == "__main__":
    main()

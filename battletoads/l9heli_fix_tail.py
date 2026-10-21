"""Tail search for the exact join T' (2026-10-09).

T' = the old route's state one frame before its jump at L9c 8280: on the floor (H 6182), running left with Left held,
x.sub = 785.160, speed 96, vertical sub-pixel $466 = 118, flags $4A2 = 72.  From there the old inputs (8280...) are replayed and
compared with the old run's own RAM (cap14).

Trunk = heli_beamAB.json[0] (L9c 7819 -> 7873) + heli_beam_b4.json[GI] (7873 -> the floor landing).
    python l9heli_fix_tail.py show                   print the trunk's last 45 frames (H, vy, anim, $466, mine)
    python l9heli_fix_tail.py vert <branch>          scan A-hold patterns from trunk frame <branch> to the landing: landing frame, $466
    python l9heli_fix_tail.py horiz <branch> <A pattern as i:len[,i:len]> <tag>
                                                     scan slow-down patterns on the floor for T' and verify every hit
-> logs/fix/heli_tail_<tag>.json (list of verified joins: inputs from 7819, f*, gain), bookmark L9heli_T_<tag>"""
import json, sys, os, time, itertools
from l9heli_fix_lib import *

GI = int(os.environ.get("GI", 0))
R = cap(); ins = up14_inputs()
AB = json.load(open(LOGS_DIR / "fix" / "heli_beamAB.json"))[0]
B4 = json.load(open(LOGS_DIR / "fix" / "heli_beam_b4.json"))[GI]
TRUNK = AB["inputs"] + B4["inputs"]
FLD = {"x": 0x3FD, "xh": 0x3EE, "sub": 0x448, "h": 0x439, "hh": 0x42A, "z": 0x475, "spd": 0x565, "hp": 0x51A, "sh": 0x466, "f": 0x4A2, "an": 0x3D0,
       "lives": 0x11, "vyh": 0x4C0, "vyl": 0x4CF}
J0 = 8279                                                    # the old index of T'
T = bytes(R[OFF + J0 - 1])
TK = (T[0x3FD] | T[0x3EE] << 8, T[0x448], T[0x439] | T[0x42A] << 8, T[0x475], T[0x565], T[0x466], T[0x4A2])
VER = int(os.environ.get("VER", 150))


def kin(s):
    return (s.x | s.xh << 8, s.sub, s.h | s.hh << 8, s.z, s.spd, s.hp)


def ckin(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x51A])


def setA(b, on):
    p = [v for v in bt(b) if v != "A"]
    if on:
        p.append("A")
    return "+".join(p)


def mine(e):
    m = e.ram(0x3C1, 0x1C0)
    for q in range(2, 15):
        if m[q] == 0x72:
            return (m[0x3FD - 0x3C1 + q] | m[0x3EE - 0x3C1 + q] << 8, m[0x565 - 0x3C1 + q])
    return None


def main():
    mode = sys.argv[1]
    e = BizHawk(log_name=f"l9heli_fix_tail_{mode}.log", fields=FLD)
    e.load("L9heli_7819")
    print("T' key (x, sub, H, z, spd, $466, $4A2):", TK, flush=True)
    if mode == "show":
        for i, b in enumerate(TRUNK):
            s = e.step(bt(b), 1)
            if i >= len(TRUNK) - 45:
                print(i + 1, 7819 + i + 1, repr(b).ljust(9), f"x {s.x | s.xh << 8}.{s.sub:3d} H {s.h | s.hh << 8} z {s.z} an {s.an} spd {s.spd} vy {s.vyh},{s.vyl} sh {s.sh} f {s.f} mine {mine(e)}", flush=True)
        e.close(); return
    br = int(sys.argv[2])
    for b in TRUNK[:br]:
        e.step(bt(b), 1)
    root = e.msave()
    rest = TRUNK[br:]
    if mode == "vert":
        res = {}
        pats = [()] + [((i, n),) for i in range(0, len(rest) + 6) for n in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16)]
        for pat in pats:
            e.mload(root); land = None
            for i in range(len(rest) + 40):
                b = rest[i] if i < len(rest) else "Left"
                on = any(a <= i < a + n for a, n in pat)
                s = e.step(bt(setA(b, on)), 1)
                if s.hp < 47 or s.an in CARRIED:
                    land = ("dead", i + 1); break
                if s.z == 0 and (s.h | s.hh << 8) == 6182:
                    land = (i + 1, s.sh, s.x | s.xh << 8, s.sub, s.spd); break
            res[pat] = land
            if land and land[0] != "dead" and land[1] == TK[5]:
                print("A pattern", pat, "-> landing at trunk frame", br + land[0], "index", 7819 + br + land[0], land, flush=True)
        vals = sorted(set(v[1] for v in res.values() if v and v[0] != "dead"))
        print(len(pats), "patterns;", len(vals), "distinct landing $466 values; baseline", res[()], flush=True)
        json.dump({f"{k}": v for k, v in res.items()}, open(LOGS_DIR / "fix" / "heli_tail_vert.json", "w"))
        e.close(); return
    # horiz
    pat = [tuple(int(v) for v in p.split(":")) for p in sys.argv[3].split(",") if p]
    tag = sys.argv[4]
    # landing with this A pattern
    e.mload(root); pre = []
    for i in range(len(rest) + 40):
        b = rest[i] if i < len(rest) else "Left"
        b = setA(b, any(a <= i < a + n for a, n in pat)); s = e.step(bt(b), 1); pre.append(b)
        if s.z == 0 and (s.h | s.hh << 8) == 6182:
            break
    print("landing after", len(pre), "frames at trunk frame", br + len(pre), "x", s.x | s.xh << 8, s.sub, "spd", s.spd, "$466", s.sh, "mine", mine(e), flush=True)
    if s.sh != TK[5]:
        print("WARNING: landing $466 is not", TK[5], flush=True)
    land = e.msave(); found = []; n = 0; t0 = time.time()
    AMAX = int(os.environ.get("AMAX", 44))

    def variants():
        for a in range(0, AMAX):                              # frames of Left after the landing before the slow-down
            for r in range(0, 7):                             # Right (brake) frames
                for i in range(0, 9):                         # idle frames
                    if r == 0 and i == 0 and a > 0:
                        continue
                    yield (a, r, i, None)
        for a in range(0, AMAX, 2):                           # two slow-downs
            for r in range(0, 5):
                for i in range(0, 5):
                    for g in range(2, 24, 2):
                        for i2 in (1, 2, 3):
                            yield (a, r, i, (g, i2))

    for (a, r, i, h2) in variants():
        seq = ["Left"] * a + ["Right"] * r + [""] * i
        if h2:
            seq += ["Left"] * h2[0] + [""] * h2[1]
        e.mload(land); n += 1; k = 0; hit = None
        while k < 150:
            b = seq[k] if k < len(seq) else "Left"
            s = e.step(bt(b), 1); k += 1
            if s.hp < 47:
                break
            x = s.x | s.xh << 8
            if x < 785:
                break
            if b == "Left" and (x, s.sub, s.h | s.hh << 8, s.z, s.spd, s.sh, s.f) == TK:
                hit = k; break
        if n % 500 == 0:
            print(f"  {n} variants, {len(found)} verified, {time.time() - t0:.0f}s", flush=True)
        if hit is None:
            continue
        sv = e.msave(); ok = 0; bad = None
        for j in range(J0, J0 + VER):
            s = e.step(bt(ins[OFF + j]), 1); ref = bytes(R[OFF + j])
            if kin(s) != ckin(ref):
                bad = (j + 1, kin(s), ckin(ref)); break
            ok += 1
        f = br + len(pre) + hit
        print(f"T' at trunk frame {f} (index {7819 + f}, gain {J0 - 7819 - f}) variant a={a} r={r} i={i} h2={h2}: verify {ok}/{VER} first diff {bad}", flush=True)
        if bad is None:
            full = TRUNK[:br] + pre + (seq + ["Left"] * 200)[:hit]
            found.append({"root": "L9heli_7819", "root_index": 7819, "inputs": full, "f": f, "join_old_index": J0, "gain": J0 - 7819 - f, "variant": [a, r, i, h2], "apat": pat})
            e.mload(sv); e.save(f"L9heli_T_{tag}_{len(found) - 1}")
            json.dump(found, open(LOGS_DIR / "fix" / f"heli_tail_{tag}.json", "w"))
        e.mfree(sv)
    print(n, "variants,", len(found), "verified joins; best gain", max([f["gain"] for f in found], default=None), flush=True)
    e.close()


if __name__ == "__main__":
    main()

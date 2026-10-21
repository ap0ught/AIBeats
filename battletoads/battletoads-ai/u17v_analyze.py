"""u17v_analyze.py - the up17 verifier's own reading of a per-frame RAM capture (logs/fix/u17v_<tag>.ram).

    python u17v_analyze.py <tag> [inputs.txt]

Frame N = the Nth line of the input list; record N-1 of the capture is the RAM after that input was stepped.
Prints and saves (logs/fix/u17v_<tag>_analysis.json): every change of the level byte $10, the Level 1 landing,
the 13 -> 254 cuts, lives / health / score at each level end, score monotony (a continue resets the score),
deaths, the game's pad bytes against the input list.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
FPS = 60.0988
RECORD = 749.25

LEVEL, TIMER, LIVES = 0x10, 0x0B, 0x11
PAD1, PAD2, NEW1, NEW2 = 0x29, 0x2A, 0x2B, 0x2C
ANIM, HP = 0x3B5, 0x51A
BITS = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 0x08, "Down": 0x04, "Left": 0x02, "Right": 0x01}


class Cap:
    def __init__(self, tag):
        self.data = (FIX / f"u17v_{tag}.ram").read_bytes()
        assert len(self.data) % 2048 == 0
        self.n = len(self.data) // 2048

    def b(self, frame, addr):                       # frame is 1-based
        return self.data[(frame - 1) * 2048 + addr]

    def col(self, addr):
        return self.data[addr::2048]

    def ram(self, frame):
        return self.data[(frame - 1) * 2048: frame * 2048]


def score_of(cap, f, addr=0x5F4):      # six decimal digits, found by searching the RAM for 004000 / 043600 / 334550

    return cap.ram(f)[addr:addr + 6]


def main():
    tag = sys.argv[1]
    cap = Cap(tag)
    N = cap.n
    out = {"tag": tag, "frames": N, "final_ram_sha1": hashlib.sha1(cap.ram(N)).hexdigest(),
           "capture_sha1": hashlib.sha1(cap.data).hexdigest()}
    print(f"{tag}: {N} frames; final RAM sha1 {out['final_ram_sha1']}; capture sha1 {out['capture_sha1']}")
    lv = cap.col(LEVEL)
    changes = [(f, lv[f - 2], lv[f - 1]) for f in range(2, N + 1) if lv[f - 1] != lv[f - 2]]
    out["level_changes"] = changes
    print("level byte $10 at frame 1:", lv[0])
    print("every change of the level byte (frame: from -> to):")
    print("   " + " | ".join(f"{f} {a}->{b}" for f, a, b in changes))
    # landing: anim $3B5 5 -> 4 while level == 1
    an = cap.col(ANIM)
    land = [f for f in range(2, N + 1) if lv[f - 1] == 1 and an[f - 2] == 5 and an[f - 1] == 4]
    out["landing_candidates"] = land[:5]
    landing = land[0] if land else None
    out["landing"] = landing
    print("Level 1: $3B5 5 -> 4 on frames", land[:5], "-> clock start", landing)
    if landing:
        print("   around the landing (frame: $3B5 anim, $41B y, $439 height, $3FD x, $87/$88 camera, $29 pad):")
        for f in range(landing - 8, landing + 8):
            r = cap.ram(f)
            print(f"   {f}: anim {r[ANIM]:3d}  y {r[0x41B]:3d}  h {r[0x439]:3d}  x {r[0x3FD]:3d}  cam {r[0x87] + 256 * r[0x88]:5d}  pad {r[PAD1]:02x}")
    cuts = [f for f, a, b in changes if a == 13 and b == 254]
    out["cuts_13_254"] = cuts
    print("level byte 13 -> 254 on frames:", cuts)
    if landing and len(cuts) >= 2:
        fr = cuts[1] - landing
        t = fr / FPS
        out["run_frames"] = fr
        out["run_seconds"] = t
        print(f"RUN: second cut {cuts[1]} - landing {landing} = {fr} frames / {FPS} = {t:.3f} s = {int(t // 60)}:{t % 60:06.3f}")
        print(f"   record {RECORD} s: under by {RECORD - t:.3f} s ({(RECORD - t) * FPS:.0f} frames); 720.00 s: under by {720 - t:.3f} s "
              f"({(720 - t) * FPS:.1f} frames)")
        print(f"   first cut {cuts[0]}: {(cuts[0] - landing) / FPS:.3f} s (NOT the end)")
        print(f"   inputs in the list: {N}; the list ends {N - cuts[1]} frames after the second cut")
    # lives
    li = cap.col(LIVES)
    lch = [(f, li[f - 2], li[f - 1]) for f in range(2, N + 1) if li[f - 1] != li[f - 2]]
    out["lives_changes"] = lch
    print("lives byte $11 changes:", " | ".join(f"{f} {a}->{b}" for f, a, b in lch))
    first_play = next(f for f, a, b in changes if b == 1)          # Level 1 begins
    print("lives minimum from the first level on:", min(li[first_play - 1:]))
    # score: find the six HUD digit bytes; print them at level ends, and check monotony
    sc = [int("".join(str(d % 10) for d in score_of(cap, f))) if all(d < 10 for d in score_of(cap, f)) else None
          for f in range(1, N + 1)]
    drops = []
    last = None
    for f, s in enumerate(sc, 1):
        if s is None:
            continue
        if last is not None and s < last[1] and f > first_play:
            drops.append((f, last[1], s))
        last = (f, s)
    out["score_drops"] = drops[:20]
    print(f"score ($5F4-$5F9 as six digits) decreases after frame {first_play}: {len(drops)} {drops[:10]}")
    hp = cap.col(HP)
    # level table
    rows = []
    for i, (f, a, b) in enumerate(changes):
        if b in (254, 255, 0):
            continue
        # a level starts on frame f with byte b; it ends at the next change
        end = changes[i + 1][0] if i + 1 < len(changes) else N + 1
        last_f = end - 1
        seg_hp = hp[f - 1 + 40:last_f] or bytes(1)            # skip the load (health is zeroed, then set)
        seg_li = li[f - 1:last_f]
        rows.append({"byte": b, "first": f, "last": last_f, "frames": last_f - f + 1, "lives_end": li[last_f - 1],
                     "hp_end": hp[last_f - 1], "score_end": sc[last_f - 1], "hp_min": min(seg_hp), "lives_min": min(seg_li),
                     "next": changes[i + 1][2] if i + 1 < len(changes) else None})
    out["levels"] = rows
    print("stretches of the level byte (byte: first-last frame, frames | at the last frame: lives / health / score | min health, min lives):")
    for r in rows:
        print(f"   byte {r['byte']:3d}: {r['first']:5d}-{r['last']:5d} ({r['frames']:5d} f) | {r['lives_end']} / {r['hp_end']:2d} / {r['score_end']} | "
              f"hp min {r['hp_min']:2d}, lives min {r['lives_min']} | then -> {r['next']}")
    # health drops
    hd = [(f, hp[f - 2], hp[f - 1], lv[f - 1]) for f in range(first_play + 1, N + 1) if hp[f - 1] < hp[f - 2]]
    out["health_drops"] = hd
    print(f"health $51A decreases ({len(hd)}):", " | ".join(f"{f} {a}->{b} (byte {l})" for f, a, b, l in hd[:60]))
    # pad bytes against the input list
    if len(sys.argv) > 2:
        body = Path(sys.argv[2]).read_bytes().decode("ascii").split("\n")[1:]
        if body[-1] == "":
            body = body[:-1]
        want = []
        for ln in body:
            ln = ln.rstrip("\r")
            v = 0
            for t in (ln.split(",") if ln else []):
                v |= BITS[t]
            want.append(v)
        p1, p2, n1, n2 = cap.col(PAD1), cap.col(PAD2), cap.col(NEW1), cap.col(NEW2)
        eq = sum(1 for f in range(1, N + 1) if p1[f - 1] == want[f - 1])
        print(f"game's pad byte $29 equals the listed input on {eq} of {N} frames")
        startbit = [f for f in range(1, N + 1) if p1[f - 1] & 0x10]
        print(f"frames with the Start bit in $29: {len(startbit)}: {startbit[:3]}..{startbit[-3:] if startbit else ''}")
        nz2 = [f for f in range(1, N + 1) if p2[f - 1]]
        nzn2 = [f for f in range(1, N + 1) if n2[f - 1]]
        rg = []
        for f in nz2:
            if rg and f == rg[-1][1] + 1:
                rg[-1][1] = f
            else:
                rg.append([f, f])
        print(f"second-pad byte $2A nonzero on {len(nz2)} frames: {rg[:20]}; values {sorted(set(p2[f - 1] for f in nz2))}")
        print(f"second-pad new-press byte $2C nonzero on {len(nzn2)} frames {nzn2[:10]}")
        out["pad2_nonzero"] = rg
        out["pad2_new_nonzero"] = len(nzn2)
        out["start_bit_frames"] = startbit
    (FIX / f"u17v_{tag}_analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

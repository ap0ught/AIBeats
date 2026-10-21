"""u16b (chain B): build the Level 8 segment from a climb (u16b_climb.py) and a fight (u16b_fight.py).

    segment = L8c inputs [0:5] (to the placement, up14 frame 12488)
            + the climb through the control frame + the fight to the killing blow
            + WAIT empty frames (the boss's death takes ~440; presses before that only make the toad jump)
            + A, B on alternate frames until the toad is set down in Terra Tubes (never Start), cut on that frame

    python u16b_build.py <climb json> <fight json> <out segment name> [wait=300] [first mash button=A]
    -> logs/pbeam_<out>.json (bookmark L6c_end0), bookmark <out>_end0 = the Terra Tubes placement, prints the checks
Replayed from the bookmark L6c_end0 (checked against cap14's row 12483 first).  No memory writes."""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import F8, bt, cap, banned, score, write_json, FIX, P0, L8_FIRST


def main():
    climb, fight, out = sys.argv[1], sys.argv[2], sys.argv[3]
    wait = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    first = sys.argv[5] if len(sys.argv) > 5 else "A"
    mash = ["A", "B"] if first == "A" else ["B", "A"]
    cj, fj = json.load(open(climb)), json.load(open(fight))
    assert cj["from_frame"] == P0 and fj["complete"]
    R = cap()
    e = BizHawk(log_name=f"u16b_build_{out}.log", fields=F8)
    s = e.load("L6c_end0")
    d0 = sum(1 for a, b in zip(e.ram_all(), bytes(R[L8_FIRST - 2])) if a != b)
    ins = [""] * (P0 - L8_FIRST + 1)
    for b in ins:
        s = e.step(bt(b), 1)
    d1 = sum(1 for a, b in zip(e.ram_all(), bytes(R[P0 - 1])) if a != b)
    print(f"L6c_end0 vs cap14 row {L8_FIRST - 1}: {d0} bytes differ; after {len(ins)} empty frames vs row {P0}: {d1} bytes differ; toad x {s.x} hp {s.hp} lives {s.lives}", flush=True)
    assert d0 == 0 and d1 == 0
    lives0, minhp = s.lives, 99
    for b in cj["inputs"]:
        s = e.step(bt(b), 1)
        ins.append(b)
        minhp = min(minhp, s.hp)
    print(f"climb: {len(cj['inputs'])} inputs -> control on up14-clock frame {L8_FIRST - 1 + len(ins)} (up14 15790), toad x {s.x} hp {s.hp} (lowest {minhp}) lives {s.lives} score {score(s)}", flush=True)
    assert s.hp == 47 and minhp == 47 and s.lives == lives0 and score(s) == 91600
    sc0, kill = score(s), None
    for b in fj["inputs"]:
        s = e.step(bt(b), 1)
        ins.append(b)
        minhp = min(minhp, s.hp)
    kill = L8_FIRST - 1 + len(ins)
    print(f"fight: {len(fj['inputs'])} inputs -> last blow on frame {kill} (up14 16877: {16877 - kill:+d}), score {score(s)} hp {s.hp} (lowest {minhp}) lives {s.lives}", flush=True)
    assert score(s) == 143600 and minhp == 47, (score(s), minhp)
    stage, left, placed = 0, None, None
    for j in range(wait + 900):
        b = "" if j < wait else mash[(j - wait) % 2]
        s = e.step(bt(b), 1)
        ins.append(b)
        f = L8_FIRST - 1 + len(ins)
        if s.level == 7:
            minhp = min(minhp, s.hp)
        if left is None and s.level in (254, 255):
            left = f
        if stage == 0 and s.level == 11:
            stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            placed = f
            break
    assert placed, "the toad was never set down in Terra Tubes"
    m = e.ram_all()
    e.save(out + "_end0")
    ref = bytes(R[17366 - 1])
    df = [a for a in range(0x800) if m[a] != ref[a]]
    bad = [b for b in ins if banned(b)]
    nsel = sum(1 for b in ins if "Select" in b)
    print(f"level byte leaves 7 on frame {left} (up14 17318); toad set down in Terra Tubes on frame {placed} (up14 17366): {17366 - placed} frames earlier; "
          f"hp {s.hp} lives {s.lives} score {score(s)} x {s.x | s.xh << 8} (up14: 47 / 3 / 143600 / 40); lowest hp in Level 8: {minhp}", flush=True)
    print(f"segment {out}: {len(ins)} inputs (L8c 4883: {4883 - len(ins)} shorter); banned presses (Left+Right, Up+Down, Start): {len(bad)}; Select frames: {nsel}; "
          f"entry RAM vs up14's Level 9 entry (cap14 row 17366): {len(df)} bytes differ {[hex(a) for a in df[:24]]}", flush=True)
    assert not bad and s.hp == 47 and s.lives == 3 and score(s) == 143600
    note = ("INTRUDER EXCLUDER: the 4,000-px tower again, re-searched by landings instead of by frames - every node is the toad standing somewhere unhurt, "
            "the earliest arrival wins; no entry wait, the stalls at the flier columns cut. Then Robo-Manus the fast way: only the jump-smash keeps him "
            "in his corner, which attack B gives is a dice roll, and a Select press on an earlier frame re-rolls it." +
            f"||{len(ins)} frames (L8c: 4883; {len(ins) - 4883:+d}). Climb {len(cj['inputs'])} frames to control (up14 3302), fight {len(fj['inputs'])} (up14 1087)")
    write_json(LOGS_DIR / f"pbeam_{out}.json", {"bookmark": "L6c_end0", "inputs": ins, "note": note, "slack": 0, "climb": climb, "fight": fight,
                                                 "wait": wait, "mash": mash, "kill_frame": kill, "level_left": left, "placed": placed})
    e.close()


if __name__ == "__main__":
    main()

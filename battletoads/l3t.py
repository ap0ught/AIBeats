"""Level 3, the Turbo Tunnel (speeder bike course): jump the walls, learn the timing by dying.

Measured: the bike accelerates 0 -> 8 ($D5) over ~235 frames and drives itself. Walls are objects with ID 0x23,
spawning ~250 px ahead in one of the lanes (depth 200 / 224 / ...). Hitting one stops the bike, the toad dies
and respawns back at the rat section. A (held) jumps.

Policy: for the nearest wall ahead in our lane, press A when it is `lead` px ahead; `lead` per wall is learned:
a death at wall x moves that wall's lead (or adds one). Other lanes' walls are ignored unless `steer` says to
change lane instead of jumping (learned too).

    python l3t.py [rounds]   -> logs/pbeam_L3t.json, knowledge/l3_walls.json
"""
import json
import random
import sys
import time

from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens

WALL = 0x23
WALLS = PROJECT / "knowledge" / "l3_walls.json"


def rd(r):
    tx = r[0x3FD] + 256 * r[0x3EE]                     # unsigned: the course runs past 32767
    walls = [(r[0x3FD + s] + 256 * ((r[0x3EE + s] + 128) % 256 - 128), r[0x41B + s]) for s in range(2, 12) if r[0x3C1 + s] == WALL]
    return dict(x=tx, y=r[0x41B], z=r[0x475], h=r[0x439], spd=r[0xD5], lives=r[0x11], lvl=r[0x10], walls=walls,
                clear=r[0x33], hp=r[0x51A], cam=r[0x87] + 256 * r[0x88])


class Rec:
    def __init__(self, emu):
        self.emu, self.inputs = emu, []

    def step(self, btn=(), n=1):
        self.inputs += ["+".join(btn)] * n
        return self.emu.step(btn, n)


def attempt(emu, seed, presses, bookmark="L3_bike_go", max_frames=9000, stop_x=None):
    """presses: sorted list of world x at which to press A (4 frames). Learned, not reactive: a wall exists in RAM
    only ~20 px before impact, while the jump must start 155-283 px before it (measured on wall 1)."""
    emu.load(bookmark)
    rec = Rec(emu)
    f = 0
    lives0 = rd(emu.ram_all())["lives"]
    done = set()
    wraps, last_raw = 0, None
    edge = None                                          # last x seen at road height before a fall
    while f < max_frames:
        q = rd(emu.ram_all())
        if last_raw is not None and q["x"] < last_raw - 30000:
            wraps += 1                                   # the 16-bit world x wraps at 65536 part-way down the course
        last_raw = q["x"]
        q["x"] += 65536 * wraps
        if stop_x is not None and q["x"] >= stop_x:
            return "reached", rec.inputs, dict(x=q["x"], f=f, edge=edge, fall=False, wraps=wraps)
        if q["hp"] == 0 or q["lives"] < lives0 or (q["spd"] == 0 and f > 300):
            # HP hits 0 at the crash itself; the lives byte only drops after the respawn at the last checkpoint,
            # which is where the first version thought every gap death happened
            fall = edge is not None and q["x"] - edge > 120 and q["spd"] != 0
            return "died", rec.inputs, dict(x=q["x"], f=f, edge=edge, fall=fall)
        if 60 <= q["h"] <= 120:
            edge = q["x"]
        if q["lvl"] != 3:
            return "level", rec.inputs, dict(x=q["x"], f=f)
        if q["clear"] == 0x81:
            return "clear", rec.inputs, dict(x=q["x"], f=f)
        due = [e for e in presses if e[0] <= q["x"] < e[0] + 200 and e[0] not in done]
        if due and (q["z"] <= 13 or due[0][1] != "A"):
            px, act = due[0]
            done.add(px)
            if act == "A":                             # first frame back on the ground (the hover sits at z 3-13)
                rec.step(("A",), 4); rec.step((), 2); f += 6
            else:                                      # steer: U40 = hold Up 40 frames, D40 = Down
                n = int(act[1:]); btn = ("Up",) if act[0] == "U" else ("Down",)
                rec.step(btn, n); rec.step((), 2); f += n + 2
            continue
        rec.step((), 2); f += 2
    return "timeout", rec.inputs, dict(x=q["x"], f=f)


def learn(emu, rounds=80, seed=1):
    """Hill-climb with rollback. best_map is the press list that got furthest (best_x). Each round edits only the
    front: the wall that killed the best run (x+19) gets its press walked through the window 155-283, and if that
    wall keeps killing, the press before it is walked too (it decides where the bike lands). An edit that dies
    earlier than best_x - 60 is thrown away."""
    raw = json.loads(WALLS.read_text()) if WALLS.exists() else []
    best_map = sorted({tuple(e) if isinstance(e, list) else (e, "A") for e in raw})
    outcome, ins, info = attempt(emu, seed, best_map)
    if outcome != "died":
        return outcome, ins, info, best_map
    best_x, best_info = info["x"], info
    print(f"  start: best_x {best_x} with {len(best_map)} presses (fall {info.get('fall')} edge {info.get('edge')})", flush=True)
    k = 0
    for r in range(rounds):
        xw = best_x + 19
        if best_info.get("fall"):                       # a gap: the jump must start before the road ends
            xw = best_info["edge"] + 120
        front = [e for e in best_map if xw - 700 <= e[0] < xw]
        trial = [e for e in best_map if e not in front]
        # candidate edit k: this wall's lead from the window, and the previous press nudged on later tries;
        # after the jump timings and nudges are exhausted, try steering (the bouncing 0x2B things weave lanes)
        leads = [220, 190, 250, 170, 270, 205, 235, 160, 280]
        steers = [("U40", 260), ("D40", 260), ("U80", 300), ("D80", 300), ("U40", 180), ("D40", 180), ("U120", 360), ("D120", 360)]
        n_jump = len(leads) * 5
        prev = [e for e in front if e[0] < xw - 300]
        if k < n_jump:
            lead = leads[k % len(leads)]
            prev_shift = 0 if k < len(leads) else (16 if (k // len(leads)) % 2 else -16) * ((k // len(leads) + 1) // 2)
            new_front = [(e[0] + prev_shift, e[1]) for e in prev[-1:]] + [(xw - lead, "A")]
        else:
            act, lead = steers[(k - n_jump) % len(steers)]
            new_front = list(prev[-1:]) + [(xw - lead, act)]
        keep = [e for e in front if e not in prev[-1:]]
        cand = sorted(set(trial + keep + new_front))
        outcome, ins, info = attempt(emu, seed + r + 1, cand)
        print(f"  round {r}: {outcome} x {info['x']} f {info['f']} fall {info.get('fall')} (best {best_x}) edit lead {lead} prev {prev_shift}", flush=True)
        if outcome != "died":
            WALLS.write_text(json.dumps([list(e) for e in cand]))
            return outcome, ins, info, cand
        if info["x"] > best_x + 60:                     # progress: accept, start on the new wall
            best_map, best_x, best_info, k = cand, info["x"], info, 0
            WALLS.write_text(json.dumps([list(e) for e in best_map]))
        else:                                           # no progress (or worse): roll back, try the next edit
            k += 1
    return "unsolved", None, None, best_map


if __name__ == "__main__":
    emu = BizHawk(log_name="l3t.log")
    t0 = time.time()
    outcome, ins, info, leads = learn(emu, int(sys.argv[1]) if len(sys.argv) > 1 else 80)
    emu.close()
    print(outcome, info, f"{time.time() - t0:.0f}s")
    if ins:
        (LOGS_DIR / "pbeam_L3t.json").write_text(json.dumps({
            "bookmark": "L3_bike_go", "inputs": ins, "info": info, "state": None, "history": [],
            "note": "TURBO TUNNEL: the bike drives itself; each wall's jump timing learned by crashing into it.||"
                    f"{len(leads)} obstacles learned"}))
    tokens.mark("L3 tunnel policy", {"outcome": outcome, "walls": len(leads)})

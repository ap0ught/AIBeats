"""Level 3, part 1 (the rat gauntlet before the bikes): a scripted policy plus a pit map learned by dying.

Recipe (measured): a rat (ID 0x47, 31 HP) takes a headbutt (16) and lies down 93 frames, untouchable; a second
headbutt a few frames after it stands kills it. Otherwise run right at full speed. Pits are unknown: when the
toad loses a life at world x, the map gets a jump a little before x, and the attempt restarts. Held-A jumps
(20+ frames) are the long ones.

    python l3.py [attempts] [scouts]   -> logs/pbeam_L3.json (segment for assemble.py), knowledge/l3_pits.json
"""
import json
import random
import sys
import threading
import time
from pathlib import Path

from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens

RAT_IDS = {0x47, 0xC7}
PITS = PROJECT / "knowledge" / "l3_pits.json"


def rd(r):
    tx = r[0x3FD] + 256 * ((r[0x3EE] + 128) % 256 - 128)
    foes = [(s, r[0x3FD + s] + 256 * ((r[0x3EE + s] + 128) % 256 - 128), r[0x41B + s], r[0x51A + s], r[0x4B1 + s], r[0x3C1 + s])
            for s in range(2, 15) if r[0x3C1 + s] and r[0x51A + s] and r[0x583 + s] != 0x55 and r[0x3C1 + s] & 0x7F != 6]
    return dict(x=tx, y=r[0x41B], z=r[0x475], h=r[0x439], spd=r[0x565], lvl=r[0x10], lives=r[0x11], hp=r[0x51A],
                cam=r[0x87] + 256 * r[0x88], foes=foes, clear=r[0x33], bike=r[0x3C1 + 2])


class Rec:
    def __init__(self, emu):
        self.emu, self.inputs = emu, []

    def step(self, btn=(), n=1):
        self.inputs += ["+".join(btn)] * n
        return self.emu.step(btn, n)


def attempt(emu, seed, jumps, bookmark="L3_rat1b", max_frames=7000, hold_a=30):
    """jumps: sorted list of world x where a long dash-jump starts. Returns (outcome, inputs, info)."""
    rng = random.Random(seed)
    ram_lo, ram_hi = rng.choice([(24, 40), (28, 44), (32, 48)])
    wake = rng.choice([2, 4, 8])
    coast = rng.choice([120, 140, 160])
    emu.load(bookmark)
    rec = Rec(emu)
    f = 0
    lives0 = rd(emu.ram_all())["lives"]
    jumped = set()
    hp_full = {}
    edge = None                                          # last x seen on the floor before the current fall
    maxx = 0
    while f < max_frames:
        q = rd(emu.ram_all())
        if q["lives"] < lives0:
            return "died", rec.inputs, dict(x=q["x"], cam=q["cam"], f=f, edge=edge, passed=sorted(jumped), maxx=maxx,
                                            foes=[(fo[5], fo[1], fo[2], fo[3]) for fo in q["foes"]])
        if q["h"] == 64 and q["z"] <= 2 and q["hp"]:
            edge = q["x"]
            maxx = max(maxx, q["x"])
        if q["lvl"] != 3:
            return "level", rec.inputs, dict(x=q["x"], cam=q["cam"], f=f)
        if q["clear"] == 0x81:
            return "clear", rec.inputs, dict(x=q["x"], cam=q["cam"], f=f)
        if q["bike"] == 0x18 and q["z"] <= 2 and q["x"] > 1700:
            return "bikes", rec.inputs, dict(x=q["x"], cam=q["cam"], f=f)
        # a rat in reach on our line: the recipe
        for fo in q["foes"]:
            hp_full.setdefault(fo[0], fo[3])
        # drifting "Green Vaders" (ID 0x15, HP 255) hold the camera and drain health: a punch when one is close
        vaders = [fo for fo in q["foes"] if fo[5] & 0x7F == 0x15 and abs(fo[1] - q["x"]) <= 36 and abs(fo[2] - q["y"]) <= 10]
        if vaders and q["z"] <= 2:
            v = vaders[0]
            rec.step((("Right",) if v[1] > q["x"] else ("Left",)) + ("B",), 2); rec.step((), 8); f += 10
            continue
        rats = [fo for fo in q["foes"] if fo[5] in RAT_IDS and abs(fo[1] - q["x"]) <= 90]
        if rats:
            # a standing rat is the threat and the target; a downed one just needs distance kept
            standing = [fo for fo in rats if fo[4] != 64]
            s, fx, fy, fhp, fst, fid = min(standing or rats, key=lambda fo: abs(fo[1] - q["x"]))
            dx, dy = fx - q["x"], fy - q["y"]
            if fx > q["cam"] + 228 and q["x"] > q["cam"] + 190:
                rec.step(("Left",), 2); f += 2            # it is off the right edge and will not come while we pin the edge
                continue
            side = ("Right",) if dx > 0 else ("Left",)
            v = ("Down",) if dy > 3 else ("Up",) if dy < -3 else ()
            if fst == 64:                                   # down: hold 24-40 px on its line, wait
                if abs(dx) > ram_hi:
                    rec.step(side + v, 1)
                elif abs(dx) < ram_lo:
                    rec.step((("Left",) if dx > 0 else ("Right",)) + v, 1)
                else:
                    rec.step(v, 1)
                f += 1
                continue
            # standing and in range: headbutt (the first one knocks it down, the next one after it stands kills)
            if 24 <= abs(dx) <= 56 and abs(dy) <= 4 and q["z"] <= 2:
                if fhp < hp_full.get(s, fhp):
                    rec.step((), wake); f += wake
                rec.step(side, 1); rec.step((), 1); rec.step(side, 4); rec.step(side + ("B",), 2); rec.step(side, 6)
                f += 14
                continue
            if abs(dx) > 54:
                rec.step(side + v, 2); f += 2
            elif abs(dx) < 28:
                rec.step((("Left",) if dx > 0 else ("Right",)) + v, 2); f += 2
            else:
                rec.step(v, 2); f += 2
            continue
        # no rat: run right. Pits: a dash-jump from a STANDSTILL carries 89 px (measured); one out of a run only 29.
        # So coast to a stop before a mapped edge, then tap-release-tap-A with A held.
        ahead = [jx for jx in jumps if jx not in jumped and q["x"] < jx + 30]
        if ahead:
            jx = min(ahead)
            if q["x"] >= jx - 10:
                if q["z"] <= 2 and q["spd"] <= 24:
                    jumped.add(jx)
                    rec.step(("Right",), 1); rec.step((), 1); rec.step(("Right", "A"), hold_a); rec.step(("Right",), 6)
                    f += 8 + hold_a
                else:
                    rec.step((), 2); f += 2
                continue
            if q["x"] >= jx - 40:                     # last 30 px: let the walk die out; nudge if it stops short
                rec.step(("Right",) if q["spd"] == 0 else (), 2); f += 2
                continue
            if q["x"] >= jx - coast:                  # approach at walking speed (no double tap)
                rec.step(("Right",), 2); f += 2
                continue
        if q["spd"] < 100 and q["z"] <= 2:
            rec.step(("Right",), 1); rec.step((), 1); rec.step(("Right",), 4); f += 6
        else:
            rec.step(("Right",), 2); f += 2
    return "timeout", rec.inputs, dict(x=q["x"], cam=q["cam"], f=f, edge=edge, maxx=maxx, foes=[(fo[5], fo[1], fo[2], fo[3]) for fo in q["foes"]], lvl=q["lvl"], bike=q["bike"])


def learn(emu, rounds=40, seed=1):
    """Grow the pit map: run; on a death at x, add a jump before it (random lead), retry."""
    jumps = json.loads(PITS.read_text()) if PITS.exists() else []
    rng = random.Random(seed)
    frozen = set()                                     # jumps the toad has landed past alive
    for r in range(rounds):
        outcome, ins, info = attempt(emu, seed + r, sorted(jumps))
        print(f"  round {r}: {outcome} at x {info['x']} (edge {info.get('edge')}) cam {info['cam']} f {info['f']} jumps {sorted(jumps)}", flush=True)
        if outcome == "died":
            fx = info.get("edge") or info["x"]         # the ledge's end: the fall itself lasts 140 frames
            for j in jumps:                            # any jump well behind the furthest floor contact worked
                if info.get("maxx", 0) > j + 120:
                    frozen.add(j)
            if abs(info["x"] - fx) < 12 and info.get("foes"):
                print(f"     died on the floor with enemies {info['foes']}: not a pit", flush=True)
            near = [j for j in jumps if abs(j - fx) < 70 and j not in frozen]
            if near:                                   # a mapped jump did not carry: start it earlier
                jumps.remove(near[0])
                jumps.append(near[0] - rng.choice([4, 8, 12]))
            elif not any(abs(j - fx) < 70 for j in jumps):
                jumps.append(fx - rng.choice([8, 12, 16]))
            PITS.write_text(json.dumps(sorted(jumps)))
        else:
            return outcome, ins, info, sorted(jumps)
    return "unsolved", None, None, sorted(jumps)


if __name__ == "__main__":
    emu = BizHawk(log_name="l3.log")
    t0 = time.time()
    outcome, ins, info, jumps = learn(emu, int(sys.argv[1]) if len(sys.argv) > 1 else 40)
    emu.close()
    print(outcome, info, jumps, f"{time.time() - t0:.0f}s")
    if ins:
        (LOGS_DIR / "pbeam_L3.json").write_text(json.dumps({
            "bookmark": "L3_rat1b", "inputs": ins, "info": info, "state": None, "history": [],
            "note": "LEVEL 3, the rat gauntlet: headbutt, wait for the rat to stand, headbutt again. Pits learned by dying.||"
                    f"jumps at x {jumps}"}))
    tokens.mark("L3 part 1 policy", {"outcome": outcome, "jumps": jumps})

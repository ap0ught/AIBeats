"""Level 3 Turbo Tunnel, reactive version. Holding Left keeps the bike at the LEFT edge of the screen (x-cam 22),
so obstacles spawn ~200 px ahead instead of 18 - the first tunnel policy rode pinned to the right edge and had to
learn every wall blind. Now walls (ID 0x23) are jumped on sight; learned overrides [(x, act)] still apply first.

    python l3r.py [rounds]  -> logs/pbeam_L3t.json, knowledge/l3r_map.json
"""
import json, sys, time
from collections import deque
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens

MAP = PROJECT / "knowledge" / "l3r_map.json"
WALL = 0x23
PIT = 0x25
PAD = 0x24        # trampoline diamond: on the road (h 64) or floating (h 92)
PORTAL = 0x22     # mega-warp portal (level 3 -> 5): avoid
DROP = 0x29       # drops out of the sky and sits on the road like a wall


def rd(r):
    tx = r[0x3FD] + 256 * r[0x3EE]
    objs = [(s, (r[0x3C1 + s], r[0x3FD + s] + 256 * ((r[0x3EE + s] + 128) % 256 - 128), r[0x41B + s], r[0x439 + s], r[0x475 + s]))
            for s in range(2, 12) if r[0x3C1 + s]]
    return dict(x=tx, y=r[0x41B], z=r[0x475], h=r[0x439], spd=r[0xD5], lives=r[0x11], lvl=r[0x10], objs=objs,
                clear=r[0x33], hp=r[0x51A], cam=r[0x87] + 256 * r[0x88])


class Rec:
    def __init__(self, emu):
        self.emu, self.inputs = emu, []

    def step(self, btn=(), n=1):
        self.inputs += ["+".join(btn)] * n
        return self.emu.step(btn, n)


def attempt(emu, presses, bookmark="L3_bike_go", max_frames=12000, stop_x=None, lead=(150, 283), trace=60):
    emu.load(bookmark)
    rec = Rec(emu)
    f = 0
    lives0 = rd(emu.ram_all())["lives"]
    done = set()
    wraps, last_raw = 0, None
    hist = deque(maxlen=trace)
    edge = None
    goal = None
    events = []
    last_dx = {}
    last_x, last_f, vel = None, 0, 8.0
    while f < max_frames:
        q = rd(emu.ram_all())
        if last_raw is not None and q["x"] < last_raw - 30000:
            wraps += 1
        last_raw = q["x"]
        q["x"] += 65536 * wraps
        if last_x is not None and f > last_f:
            v = (q["x"] - last_x) / (f - last_f)
            if 2 <= v <= 16:
                vel = 0.7 * vel + 0.3 * v
        last_x, last_f = q["x"], f
        k = vel / 8.0                                             # all windows below were measured at 8 px/frame
        rel = []
        for s, o in q["objs"]:
            dx = (o[1] - last_raw + 32768) % 65536 - 32768         # 16-bit world x, unwrapped relative to the bike
            parked = last_dx.get(s) == dx and dx > 150            # waiting at the screen's right edge, not yet placed
            last_dx[s] = dx
            if not parked:
                rel.append((o[0], dx, o[2], o[3]))                 # (id, dx, lane, h)
        hist.append((f, q["x"], q["y"], q["z"], q["h"], round(vel, 1), [(hex(i), d, l, h) for i, d, l, h in rel]))
        if stop_x is not None and q["x"] >= stop_x:
            return "reached", rec.inputs, dict(x=q["x"], f=f, wraps=wraps)
        if q["hp"] == 0 or q["lives"] < lives0 or (q["spd"] == 0 and f > 300):
            fall = edge is not None and q["x"] - edge > 120
            return "died", rec.inputs, dict(x=q["x"], f=f, edge=edge, fall=fall, hist=list(hist), events=events)
        if 60 <= q["h"] <= 120:
            edge = q["x"]
        if q["lvl"] != 3:
            # the level-3 -> level-5 mega-warp is a portal object (ID 0x22, same as level 1's) in the bottom lane
            # near the end of section 5; touching it skips to Surf City, which the route does not want (4 -> 6 instead)
            portal = any(i == PORTAL and abs(d) < 48 for i, d, l, h in rel)
            if portal:
                return "warped", rec.inputs, dict(x=q["x"], f=f, hist=list(hist), events=events, fall=False, edge=edge)
            return "level", rec.inputs, dict(x=q["x"], f=f, hist=list(hist), events=events)
        if q["clear"] == 0x81:
            return "clear", rec.inputs, dict(x=q["x"], f=f)
        due = [e for e in presses if e[0] <= q["x"] < e[0] + 200 and e[0] not in done]
        if due and (q["z"] <= 13 or due[0][1] != "A"):
            px, act = due[0]
            done.add(px)
            events.append((q["x"], act + "*"))
            if act == "A":
                rec.step(("Left", "A"), 4); rec.step(("Left",), 2); f += 6
            elif act == "N":                               # learned "do nothing here" (suppress the reactive jump)
                rec.step(("Left",), 40); f += 40
            else:
                n = int(act[1:]); btn = ("Left", "Up") if act[0] == "U" else ("Left", "Down")
                rec.step(btn, n); rec.step(("Left",), 2); f += n + 2
            continue
        # reactive. Walls sit in two lanes (depth 200 = top, 224 = bottom); a wall kills within |dy| <= 14 and is
        # passed at |dy| >= 19, the bike steers 193..231 at ~1 px/frame. A wall is "mine" if it would kill me at my
        # current depth. Prefer changing lane (no dead zone after a landing) when the other lane is clear; otherwise
        # jump on sight (walls spawn ~233 px ahead). A jump in my lane always takes priority over a steer in progress.
        grounded = q["z"] <= 13 and q["h"] - q["z"] <= 66    # h includes z; the road under the bike is at 64
        walls = [(d, l) for i, d, l, h in rel if (i == WALL or i == PORTAL or (i == DROP and h <= 66)) and -24 < d]
        # a floating trampoline (0x24 above the road) launches a huge arc when the bike is airborne over it: line up
        # with it (depth 212) and jump before it
        pads = [(d, l) for i, d, l, h in rel if i == PAD and h > 70 and -24 < d < 320 * k]
        if pads:
            d = min(pads)[0]
            if abs(q["y"] - 212) > 2 and d > 60:
                rec.step(("Left", "Up") if q["y"] > 212 else ("Left", "Down"), 1); f += 1
                continue
            if grounded and d <= 220 * k:
                events.append((q["x"], "A"))
                rec.step(("Left", "A"), 4); rec.step(("Left",), 2); f += 6
                continue
        mine = [d for d, l in walls if abs(l - q["y"]) <= 16 and d > 0]
        # a hole is crossed while airborne (press+40 .. press+430): press late so a second hole fits under the arc
        pits = [d for i, d, l, h in rel if i == PIT and d > 0]
        if pits and grounded and 60 * k <= min(pits) <= 160 * k:
            events.append((q["x"], "A"))
            rec.step(("Left", "A"), 4); rec.step(("Left",), 2); f += 6
            continue
        target_y = {"top": 205, "bottom": 224}
        if vel <= 9.5:
            # sections 1-4 (8 px/frame): jump on sight at 150-283 px, or slide to the other lane when it is clear
            other = [d for d, l in walls if abs(l - q["y"]) > 16]
            if mine and grounded and lead[0] * k <= min(mine) <= lead[1] * k:
                events.append((q["x"], "A"))
                rec.step(("Left", "A"), 4); rec.step(("Left",), 2); f += 6
                continue
            if goal is not None:
                if (goal == "top" and q["y"] <= 205) or (goal == "bottom" and q["y"] >= 224):
                    goal = None
                elif any(abs(l - target_y[goal]) <= 16 and -24 < d < 420 * k for d, l in walls):
                    goal = None                                    # the lane I was heading for just got a wall
            if goal is None and mine and min(mine) <= 300 * k and grounded:
                wall_lane = min((d, l) for d, l in walls if abs(l - q["y"]) <= 16 and d > 0)[1]
                cand = "top" if wall_lane >= 212 else "bottom"
                if not any(abs(l - target_y[cand]) <= 16 and -24 < d < 420 * k for d, l in walls):
                    goal = cand
                    events.append((q["x"], goal))
        else:
            # section 5 (12 px/frame, walls alternating lanes every ~21 frames), in frames: a jump clears a wall
            # 19-35 frames out (z >= 35 there) and lasts 55; a lane change takes 19 frames and works in the air,
            # so weave: switch lanes whenever the next wall in mine cannot be jumped after this one's landing.
            t_mine = sorted(d / vel for d in mine)
            t_other = [d / vel for d, l in walls if abs(l - q["y"]) > 16 and abs(l - (205 if q["y"] > 212 else 224)) <= 16 and d > -24]
            if goal is not None:
                if (goal == "top" and q["y"] <= 205) or (goal == "bottom" and q["y"] >= 224):
                    goal = None
                elif any(abs(l - target_y[goal]) <= 16 and -24 < d < 21 * vel for d, l in walls):
                    goal = None
            if t_mine and t_mine[0] <= 38:
                dead = t_mine[0] < 19
                can_jump = grounded and 19 <= t_mine[0] <= 35
                can_switch = not any(0 <= t < 24 for t in t_other)
                room_after = len(t_mine) < 2 or t_mine[1] - t_mine[0] >= 55
                if goal is None and can_switch and (dead or not can_jump or not room_after):
                    goal = "top" if q["y"] > 212 else "bottom"
                    events.append((q["x"], goal))
                elif can_jump and goal is None:
                    events.append((q["x"], "A"))
                    rec.step(("Left", "A"), 4); rec.step(("Left",), 2); f += 6
                    continue
        if goal is not None:
            rec.step(("Left", "Up") if goal == "top" else ("Left", "Down"), 1); f += 1
            continue
        rec.step(("Left",), 1); f += 1
    return "timeout", rec.inputs, dict(x=q["x"], f=f)


def learn(emu, rounds=60):
    """Hill-climb with rollback on top of the reactive policy: overrides only where reacting is not enough
    (a wall landing in the dead zone right after a jump, a lane the reaction picked wrong)."""
    raw = json.loads(MAP.read_text()) if MAP.exists() else []
    best_map = sorted(tuple(e) for e in raw)
    outcome, ins, info = attempt(emu, best_map)
    info["warped"] = outcome == "warped"
    if outcome not in ("died", "warped"):
        return outcome, ins, info, best_map
    score = lambda i: i["edge"] if i.get("fall") and i.get("edge") else i["x"]
    best_x, best_info = score(info), info
    print(f"  start: best_x {best_x} with {len(best_map)} overrides", flush=True)
    k = 0
    for r in range(rounds):
        xd = best_x
        ev = [e for e in best_info["events"] if e[0] < xd - 30]
        last_jump = [e for e in ev if e[1].startswith("A")]
        lj = last_jump[-1][0] if last_jump else xd - 300
        if best_info.get("warped"):
            cands = [(xd - d, a) for d in (400, 550, 300, 700) for a in ("U40", "D40")]
        elif best_info.get("fall"):                                                     # a gap: jump from the edge
            edge = best_info["edge"]
            cands = [(edge - s, "A") for s in (100, 140, 60, 180, 20, 220, 260)]
            cands += [(edge - d, a) for d in (700, 900, 500) for a in ("U16", "U24", "D16", "U40")]
        else:
            cands = [(lj - s, "A") for s in (32, 64, 96, 128, 16, 48, 80, 112, 160)]    # jump earlier than sight
            cands += [(xd - d, a) for d in (300, 400, 500) for a in ("U40", "D40")]     # take the other lane
            cands += [(lj - 8, "N"), (xd - 250, "N")]                                   # suppress a bad reaction
        if k >= len(cands):
            print("  out of edits", flush=True)
            break
        edit = cands[k]
        trial = sorted(set([e for e in best_map if abs(e[0] - edit[0]) > 40] + [edit]))
        outcome, ins, info = attempt(emu, trial)
        info["warped"] = outcome == "warped"
        print(f"  round {r}: {outcome} x {info['x']} fall {info.get('fall')} edge {info.get('edge')} f {info['f']} (best {best_x}) edit {edit}", flush=True)
        if outcome not in ("died", "warped"):
            MAP.write_text(json.dumps([list(e) for e in trial]))
            return outcome, ins, info, trial
        if score(info) > best_x + 60:
            best_map, best_x, best_info, k = trial, score(info), info, 0
            MAP.write_text(json.dumps([list(e) for e in best_map]))
        else:
            k += 1
    return "unsolved", None, None, best_map


def show(info, n=30):
    for row in info["hist"][-n:]:
        print("   ", row)


if __name__ == "__main__":
    emu = BizHawk(log_name="l3r.log")
    t0 = time.time()
    outcome, ins, info, overrides = learn(emu, int(sys.argv[1]) if len(sys.argv) > 1 else 60)
    emu.close()
    print(outcome, info and {k: v for k, v in info.items() if k != "hist"}, f"{time.time() - t0:.0f}s")
    if ins:
        (LOGS_DIR / "pbeam_L3t.json").write_text(json.dumps({
            "bookmark": "L3_bike_go", "inputs": ins, "info": {k: v for k, v in info.items() if k != "hist"}, "state": None, "history": [],
            "note": "TURBO TUNNEL: hold Left to ride at the screen's left edge and see the walls 200 px out; jump or change lane on sight.||"
                    f"{len(overrides)} learned overrides"}))
    tokens.mark("L3 tunnel reactive policy", {"outcome": outcome, "overrides": len(overrides)})

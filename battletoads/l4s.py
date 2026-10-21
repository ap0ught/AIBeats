"""Layered BFS for a Level-4 stretch: from a bookmark, 4-frame holds over a small action set, every distinct
(x, h, airborne) state kept per layer, HP loss = death. Goal is a predicate on the toad's unwrapped height.

    python l4s.py <bookmark> <goal_x> <goal_dh> [width]  -> knowledge/l4s_<bookmark>.json (inputs)
"""
import json, sys, time
from toads.emulator import BizHawk, PROJECT

ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("Down", "Right"), ("B",), ("Right", "B"), ("Left", "B"), ("Up",), ("Down",)]
if __import__('os').environ.get('L4S_ACTS') == 'climb':      # Intruder Excluder: no punches, just run/jump/crouch
    ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("Down",)]
if __import__('os').environ.get('L4S_ACTS') == 'rev':        # The Revolution: springs need Down+dir+A (dash-springs), punches for Hornheads, runs
    ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("B",), ("Right", "B"), ("Left", "B"),
            ("Down",), ("Down", "Left"), ("Down", "Right"), ("Down", "Left", "A"), ("Down", "Right", "A"), ("Up",),
            ("RunR",), ("RunL",), ("RunRA",), ("RunLA",)]
if __import__('os').environ.get('L4S_ACTS') == 'queen':      # Armageddon: the Revolution set plus SELECT presses - the queen's moves are random and Select re-rolls the dice (the TAS presses it between blows)
    ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("B",), ("Right", "B"), ("Left", "B"),
            ("Down",), ("Up",), ("RunR",), ("RunL",), ("RunRA",), ("RunLA",), ("Select",), ("Right", "Select"), ("Left", "Select"), ("Select", "B")]
if __import__('os').environ.get('L4S_ACTS') == 'dpad':       # Clinger-Winger: the unicycle only takes directions
    ACTS = [(), ("Up",), ("Down",), ("Left",), ("Right",)]
if __import__('os').environ.get('L4S_ACTS') == 'swim':       # Terra Tubes: swimming needs Up+A, no punches
    ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("Up", "A"), ("Up",), ("Down",), ("Down", "Right"), ("Down", "Left")]
MACRO = int(__import__('os').environ.get('L4S_MACRO', 4))   # frames per action (2 for narrow underwater gaps)
WALL_HP0 = [31]                                            # the barrier's HP at the search root (set in search())
LVL = int(__import__('os').environ.get('L4S_LVL', 4))   # 0 = any level (a level change then counts as a goal-free end)
SAFE = int(__import__('os').environ.get('L4S_SAFE', 60))
HPMIN = __import__('os').environ.get('L4S_HPMIN')          # if set: allow damage down to this health instead of none
ENDCP = int(__import__('os').environ.get('L4S_ENDCP', 0))  # if set: the goal is $585 >= this (Terra Tubes end trigger = 27)
LIVESOK = bool(__import__('os').environ.get('L4S_LIVESOK')) # if set: losing a life does not prune (the end trigger works while dying)
AIRB = bool(__import__('os').environ.get('L4S_AIRB'))       # if set: attacks allowed while airborne (Rat Race: the flying kick on the bomb)
HCAM = bool(__import__('os').environ.get('L4S_HCAM'))       # if set: "height" = -camera y (Clinger-Winger maze)
XWRAP = int(__import__('os').environ.get('L4S_XWRAP', 0))   # if set: x wraps at this value (The Revolution: 512)
XSIGN = 1          # +1: progress is rightward; -1 for reach_left / leftward goals
L4WARP = len(sys.argv) > 5 and sys.argv[5] == "l4warp"
CLIMB = len(sys.argv) > 5 and sys.argv[5] == "climb"     # finer x buckets: a 4-frame walk must leave its bucket
BOSS = len(sys.argv) > 5 and sys.argv[5] == "boss"       # Robo-Manus: the score counts the smashes (2,000 each)
TRACE = __import__('os').environ.get('L4S_TRACE')         # file: every kept node (step x dh z act) per layer
FOLLOW = __import__('os').environ.get('L4S_FOLLOW')       # "i_from,i_to": follow the TAS's Terra Tubes path (placement-anchored frames)
HROOT = int(__import__('os').environ.get('L4S_HROOT', 0)) # the root's absolute height (drop-in frame) for the follow mode
FORBID = [int(v) for v in __import__('os').environ['L4S_FORBID'].split(",")] if __import__('os').environ.get('L4S_FORBID') else None   # x0,x1,H0,H1 (absolute): states inside are pruned
TP = []                                                   # follow mode: [(i, x, H_abs)] of the TAS's player 1
TASIN = []                                                # L4S_TASIN: the TAS inputs; a node in exact sync with TP[j] may replay TASIN[j+1..j+MACRO]
ILLEGAL = lambda b: ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)


def load_tas_path():
    """the TAS path: L4S_TASLOG (default the 2-player watcher log; tas/watch_1p_log.txt for FODA's 1-player run),
    Terra Tubes rows only, index 0 = the placement frame (x 40, h 112)"""
    import re, os
    rows = []
    fn = os.environ.get("L4S_TASLOG", "tas/watch_all_log.txt")
    for ln in open(PROJECT / fn):
        m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=\d+ an=(\d+) hp=\d+ cam=\d+ camy=(\d+)", ln)
        if m and (fn != "tas/watch_all_log.txt" or 12282 <= int(m.group(1)) <= 21378):
            cy = (int(m.group(6)) + 32768) % 65536 - 32768
            rows.append((int(m.group(2)), int(m.group(3)), int(m.group(5)), cy, int(m.group(4))))
    px, ph = (int(v) for v in os.environ.get("L4S_PLACE", "40,112").split(","))   # the level's placement point (Rat Race: 88,158)
    start = next(i for i, r in enumerate(rows) if r[0] == px and r[1] == ph)
    H, prev = 0, ph
    cy0 = rows[start][3]
    for i, (x, h, an, cy, z) in enumerate(rows[start:]):
        H += (h - prev + 128) % 256 - 128; prev = h
        TP.append((i, x, -(cy - cy0) if HCAM else H, an in (98, 99), z, an))   # (index, x, H or -camy, TAS swimming?, z, anim)
    if os.environ.get("L4S_TASIN"):                          # the TAS's own inputs, TASIN[j] = the input that produced TP[j]
        import json as _j
        TASIN.extend(tuple(b for b in v.split("+") if b) for v in _j.load(open(PROJECT / os.environ["L4S_TASIN"])))


def follow_progress(x, dh, pj, window=48):
    """nearest TAS point ahead of the parent's progress pj (within `window` frames): (j, distance)"""
    hx = dh + HROOT
    best = None
    for j in range(pj, min(pj + window, len(TP))):
        ddx = abs(TP[j][1] - x)
        if XWRAP:
            ddx = min(ddx, XWRAP - ddx)                      # The Revolution: x wraps around the tower
        d = ddx + abs(TP[j][2] - hx)
        if best is None or d <= best[1]:                     # ties go to the LATEST index: standing where the TAS waits still advances
            best = (j, d)
    return best
_E = __import__('os').environ
ATKNEAR = _E.get('L4S_ATKNEAR', '1' if (_E.get('L4S_LVL') == '5' and not _E.get('L4S_RATDEAD')) else '0') == '1'
HOSTILE = (0x5c, 0x62, 0x5d, 0x56, 0x53, 0x5b)            # The Revolution's enemies: attacks are only tried near one
CTR = int(__import__('os').environ.get('L4S_CTR', '0'), 16)          # a RAM counter to maximise (Dark Queen hits: $586, +12 per hit)
CTRGOAL = int(__import__('os').environ.get('L4S_CTRGOAL', '240'))
ENDOBJ = int(__import__('os').environ.get('L4S_ENDOBJ', '0'), 16)   # goal: this object id appears (The Revolution's end event 0x7F)
GOALAIR = bool(int(__import__('os').environ.get('L4S_GOALAIR', 0)))   # follow goal may be airborne (hanging on a pole)
SPDKEY = bool(int(__import__('os').environ.get('L4S_SPDKEY', 0)))   # The Revolution: a sprint ($565 >= 160) is its own state
SYNCTOL = int(__import__('os').environ.get('L4S_SYNCTOL', 0))   # TAS replay: allowed |dx|+|dH| (0 = exact, anim too)


def tas_sync(x, dh, z, an, pj, sj=None):
    """the TAS frame our state matches (x, height, z, and anim when exact): sj if still matching, else the best in [pj-4, pj+48)"""
    hx = dh + HROOT
    def d(j):
        t = TP[j]
        if t[4] != z or (SYNCTOL == 0 and t[5] != an):
            return None
        dd = min(abs(t[1] - x), (XWRAP - abs(t[1] - x)) if XWRAP else 999) + abs(t[2] - hx)
        return dd if dd <= SYNCTOL else None
    if sj is not None and sj < len(TP) and d(sj) is not None:
        return sj
    best = None
    for j in range(max(pj - 4, 0), min(pj + 48, len(TP))):
        dd = d(j)
        if dd is not None and (best is None or dd <= best[1]):
            best = (j, dd)
    return best[0] if best else None


RANK = lambda n: -(n["dh"] * 2 + XSIGN * n["x"] / 4)   # smaller = better; set per goal in __main__


SEQS = {                                                   # composite 4-frame actions: a run needs a double tap
    "RunR": [("Right",), (), ("Right",), ("Right",)],
    "RunL": [("Left",), (), ("Left",), ("Left",)],
    "RunRA": [("Right",), (), ("Right",), ("Right", "A")],
    "RunLA": [("Left",), (), ("Left",), ("Left", "A")],
}


def act_frames(act):
    if len(act) == 2 and act[0] == "TASSEQ":                  # the TAS's inputs after its frame j
        return [TASIN[act[1] + 1 + i] for i in range(MACRO)]
    if len(act) == 1 and act[0] in SEQS:
        seq = SEQS[act[0]]
        return [seq[i * len(seq) // MACRO] for i in range(MACRO)] if MACRO != len(seq) else seq
    return [act] * MACRO


def apply_act(e, act):
    for b in act_frames(act):
        e.step(b, 1)


def last_a(act):
    """is A held on the action's last frame (composites and TAS replays included)"""
    return "A" in act_frames(act)[-1]


def act_ins(act):
    return ["+".join(b) for b in act_frames(act)]


def rd(e):
    r = e.ram_all()
    sm = [r[0x51A + s] for s in range(2, 15) if r[0x3C1 + s] == 0x33]
    wall = [r[0x51A + s] for s in range(2, 15) if r[0x3C1 + s] == 0x3c]
    warp = r[0x23] == 0x0D and r[0x24] == 0xE5
    marker = any(r[0x3C1 + s] == 0x4f for s in range(2, 15))    # Karnath's Lair: the room's exit-hole marker object
    rats = [(r[0x51A + s], abs(r[0x3FD + s] + 256 * r[0x3EE + s] - (r[0x3FD] + 256 * r[0x3EE]))) for s in range(2, 15) if r[0x3C1 + s] in (0x47, 0xC7)]
    foeid = int(__import__('os').environ.get('L4S_FOEID', '0x46'), 16)          # the tracked foe: Rat Race's rat 0x46, the Buzzball 0x7b
    giblet = [r[0x51A + s] for s in range(2, 15) if r[0x3C1 + s] == foeid]      # its hp (rat: 255, 239 after a hard hit, 0 = booted)
    bx = [r[0x3FD + s] + 256 * r[0x3EE + s] for s in range(2, 15) if r[0x3C1 + s] == 0x7d]     # Robo-Manus
    hval = r[0x439]
    if HCAM:                                                  # Clinger-Winger: the maze's vertical position is the camera's (-camy)
        hval = (-(r[0x89] + 256 * r[0x8A])) & 0xFF
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=hval, z=r[0x475], hp=r[0x51A], an=r[0x3B5], spd=r[0x565], lives=r[0x11], st=r[0x4B1], lvl=r[0x10],
                score=r[0x5F4] * 100 + r[0x5F5] * 10 + r[0x5F6], boss_alive=bool(bx),      # score in thousands (+2 per smash)
                dirv=r[0x448] // 32, face=r[0x4A2] & 0x40,                                  # horizontal velocity/direction, facing
                cp=r[0x585],                                                                # Terra Tubes progress/checkpoint byte (27 = level-end trigger)
                giblet=min(giblet) if giblet else None,
                foelive=any(r[0x51A + s] > 0 for s in range(2, 15) if r[0x3C1 + s] == foeid),   # a live tracked foe on screen
                ctr=r[CTR] if CTR else 0,
                endobj=bool(ENDOBJ) and any(r[0x3C1 + s] == ENDOBJ for s in range(2, 15)),
                enear=any(r[0x3C1 + s] in HOSTILE and
                          min(abs(r[0x3FD + s] + 256 * r[0x3EE + s] - (r[0x3FD] + 256 * r[0x3EE])) % 512,
                              512 - abs(r[0x3FD + s] + 256 * r[0x3EE + s] - (r[0x3FD] + 256 * r[0x3EE])) % 512) <= 120
                          for s in range(2, 15)),                                        # an enemy within 120 px
                foedx=min((min(abs(r[0x3FD + s] + 256 * r[0x3EE + s] - (r[0x3FD] + 256 * r[0x3EE])) % 512,
                               512 - abs(r[0x3FD + s] + 256 * r[0x3EE + s] - (r[0x3FD] + 256 * r[0x3EE])) % 512)
                           + abs((r[0x439 + s] - r[0x439] + 128) % 256 - 128)
                           for s in range(2, 15) if r[0x3C1 + s] == foeid and r[0x51A + s] > 0), default=0),   # distance to the nearest live foe
                bomb=any(r[0x3C1 + s] == 0x5a and r[0x51A + s] > 0 for s in range(2, 15)),   # Rat Race's bomb still live
                swim=r[0x3B5] in (98, 99),                                                  # Terra Tubes: swimming (z is 8 in water)
                vv=r[0x484] // 4,                                                            # vertical velocity/buoyancy state (a water bob is a slow 30-frame lift)
                boss_dx=min(abs(b - (r[0x3FD] + 256 * r[0x3EE])) for b in bx) if bx else 0,
                sm_hp=min(sm) if sm else None, sm_n=len(sm), wall_hp=min(wall) if wall else None, warp=warp, marker=marker,
                rat_hp=min(h for h, d in rats) if rats else None, rat_dx=min(d for h, d in rats) if rats else 60,
                optr=r[0xB7] | r[0xB8] << 8,                                                 # the object list pointer (L4S_GOALPTR)
                lift=next((r[0x42A + s] << 8 | r[0x439 + s] for s in range(2, 15) if r[0x3C1 + s] == 0x35), 0))   # Arctic Caverns' lift height


def search(e, bookmark, goal, width=600, max_steps=300):
    max_steps = int(__import__('os').environ.get('L4S_STEPS', max_steps))
    e.load(bookmark); e.step((), 2)
    q0 = rd(e)
    WALL_HP0[0] = q0['wall_hp'] if q0.get('wall_hp') is not None else 31
    root = dict(sid=e.msave(), ins=[], x=q0["x"], h=q0["h"], dh=0, z=q0["z"], score=q0["score"], boss_dx=q0["boss_dx"], swim=q0["swim"],
                foeseen=q0["foelive"])
    if FOLLOW:
        root["pj"], root["dist"] = follow_progress(q0["x"], 0, int(FOLLOW.split(",")[0]))
        print(f"  follow: root at TAS index {root['pj']} (dist {root['dist']}), goal index {int(FOLLOW.split(',')[1])}", flush=True)
        if TASIN:
            root["sj"] = tas_sync(q0["x"], 0, q0["z"], q0["an"], root["pj"])
            print(f"  TAS inputs loaded ({len(TASIN)}); root in exact sync with TAS frame {root['sj']}", flush=True)
    layer = {(q0["x"], q0["h"], 0): root}
    hp0, lives0 = (int(HPMIN) if HPMIN else q0["hp"]), q0["lives"]
    best_seen = None
    t0 = time.time()
    for step in range(max_steps):
        nxt = {}
        for node in layer.values():
            acts = list(ACTS)
            if ATKNEAR and not node.get("enear", True):
                acts = [a for a in acts if "B" not in a]      # nothing to hit nearby: don't spend effort on swings
            sj = node.get("sj")
            if TASIN and sj is not None and sj + MACRO < len(TASIN) and not any(ILLEGAL(TASIN[sj + 1 + i]) for i in range(MACRO)):
                acts.append(("TASSEQ", sj))
            for act in acts:
                if not (act and act[0] == "TASSEQ") and node["z"] > 0 and not node.get("swim") and (("B" in act and not AIRB) or (last_a(act) and not (node.get("act") and last_a(node["act"])))):
                    continue                                     # airborne (not swimming): no punches (unless L4S_AIRB); A only as a continued hold
                e.mload(node["sid"])
                apply_act(e, act)
                q = rd(e); q["px"] = node["x"]
                if q["hp"] < hp0 or (q["lives"] < lives0 and not LIVESOK) or (LVL and q["lvl"] != LVL):
                    continue
                dh = node["dh"] + ((q["h"] - node["h"] + 128) % 256 - 128)
                if FORBID and FORBID[0] <= q["x"] <= FORBID[1] and FORBID[2] <= dh + HROOT <= FORBID[3]:
                    continue                                     # a forbidden box (e.g. a dead-end surface)
                ins = node["ins"] + act_ins(act)
                if FOLLOW:
                    q["pj"], q["dist"] = follow_progress(q["x"], dh, node["pj"])
                q["foeseen"] = bool(node.get("foeseen") or q["foelive"])   # a kill counts only if a live foe was seen on this line
                if goal(q["x"], dh, q):
                    e.step((), SAFE)                          # the endpoint must be safe to stand on for a while
                    q2 = rd(e)
                    if (q2["hp"] < hp0 or q2["lives"] < lives0) and not ENDCP:
                        continue
                    print(f"  GOAL at step {step}: x {q['x']} dh {dh} ({time.time() - t0:.0f}s)", flush=True)
                    for n in layer.values():
                        e.mfree(n["sid"])
                    return ins, q
                key = ((q["optr"] >= 0xf574, q["lift"] // 6) if L4WARP else ()) + (q["x"] // (4 if CLIMB else 8), q["h"] // 4, q["z"] > 0, q["z"] > 0 and last_a(act), q["dirv"], q["face"], q["vv"] if q["swim"] else 0, q.get("giblet"), q["spd"] >= 160 if SPDKEY else 0) + ((q["score"],) if BOSS else ()) + ((q["ctr"],) if CTR else ())   # airborne: a held A is a different state; swimming: the lift phase too
                cand = dict(sid=None, ins=ins, x=q["x"], h=q["h"], dh=dh, z=q["z"], act=act, parent=node, swim=q["swim"],
                            rat_hp=q.get("rat_hp"), rat_dx=q.get("rat_dx", 60), score=q["score"], boss_dx=q["boss_dx"],
                            pj=q.get("pj", 0), dist=q.get("dist", 0), giblet=q.get("giblet"), foeseen=q["foeseen"], foedx=q["foedx"], enear=q["enear"], ctr=q["ctr"],
                            sm_hp=q.get("sm_hp"), optr=q["optr"], lift=q["lift"],
                            gdh=dh if q["z"] == 0 else node.get("gdh", 0))       # the last height stood on
                if TASIN and FOLLOW:
                    cand["sj"] = tas_sync(q["x"], dh, q["z"], q["an"], q["pj"], (sj + MACRO) if (act and act[0] == "TASSEQ") else None)
                if key in nxt and (RANK(nxt[key]) < RANK(cand) or (RANK(nxt[key]) == RANK(cand) and (nxt[key].get("sj") is not None or cand.get("sj") is None))):
                    continue                                   # same bucket: keep the better-ranked child (ties: the TAS-synced one)
                nxt[key] = cand
        keep = sorted(nxt.values(), key=RANK)[:width]
        for n in keep:
            e.mload(n["parent"]["sid"]); apply_act(e, n["act"]); n["sid"] = e.msave()
        for n in layer.values():
            e.mfree(n["sid"])
        if not keep:
            print("  died out at step", step, flush=True)
            break
        layer = {i: n for i, n in enumerate(keep)}
        if TRACE:
            with open(TRACE, "a") as tf:
                tf.write(chr(10).join(f"{step} {n['x']} {n['dh']} {n['z']} {'+'.join(n['act'])}" for n in keep) + chr(10))
        if __import__('os').environ.get('L4S_DEBUG') and step < int(__import__('os').environ.get('L4S_DEBUG')):
            print(f"  layer {step} ({len(keep)}): " + " ".join(f"({n['x']},{n['h']},{n['z']},{'+'.join(n['act'])})" for n in keep if "A" in n["act"] or n["x"] < 40)[:60], flush=True)
        b = min(layer.values(), key=RANK)                     # the best-ranked node of the layer (goal distance)
        if best_seen is None or RANK(b) < best_seen["rank"]:
            best_seen = dict(ins=b["ins"], dh=b["dh"], x=b["x"], rank=RANK(b), score=b.get("score"))
        if step % 10 == 0:
            gm = min((n.get("giblet") for n in layer.values() if n.get("giblet") is not None), default=None)
            print(f"  step {step}: states {len(layer)} best dh {b['dh']} x {b['x']} score {b.get('score')} foe {b.get('giblet')} (min {gm}) pj {b.get('pj')} ({time.time() - t0:.0f}s)", flush=True)
            if best_seen:                                        # live checkpoint of the best line so far
                (PROJECT / "knowledge" / f"l4s_{bookmark}_live.json").write_text(json.dumps(best_seen["ins"]))
    if best_seen:
        (PROJECT / "knowledge" / f"l4s_{bookmark}_best.json").write_text(json.dumps(best_seen["ins"]))
        print(f"  best unsolved: dh {best_seen['dh']} x {best_seen['x']} score {best_seen.get('score')} ({len(best_seen['ins'])} frames) saved", flush=True)
    return None, None


MAXSTEPS = int(__import__('os').environ.get('L4S_STEPS', 300))


def make_goal(mode, gx, gdh):
    if mode == "snowman":
        return lambda x, dh, q: q["sm_hp"] == 0 and q["z"] == 0 and dh >= gdh
    if mode == "wall":
        return lambda x, dh, q: q["wall_hp"] == 0 and q["z"] == 0
    if mode == "wallhit":
        return lambda x, dh, q: q["wall_hp"] is not None and q["wall_hp"] < WALL_HP0[0]
    if mode in ("warp", "l4warp"):
        return lambda x, dh, q: q["warp"]
    if mode == "room":                                      # the room's marker object gone = next room loaded
        return lambda x, dh, q: not q["marker"]
    if mode == "teleport":                                  # the toad moved >100 px in one macro = a room transition
        return lambda x, dh, q: abs(q["x"] - q.get("px", q["x"])) > 100
    if mode == "rat":                                       # the nearest rat dead, toad on the ground
        return lambda x, dh, q: q["rat_hp"] == 0 and q["z"] == 0
    if mode == "reach_down":
        return lambda x, dh, q: x >= gx and dh <= gdh and q["z"] == 0
    if mode == "reach_band":
        return lambda x, dh, q: x >= gx and abs(dh - gdh) <= 4 and q["z"] == 0
    if mode == "reach_left":
        return lambda x, dh, q: x <= gx and dh >= gdh and q["z"] == 0
    if mode == "reach_x":                                   # any height: just get past gx on the ground
        return lambda x, dh, q: x >= gx and q["z"] == 0
    if mode == "reach_down_left":                           # LEFT and DOWN: x <= gx, height <= gdh
        return lambda x, dh, q: x <= gx and dh <= gdh and q["z"] == 0
    if mode == "climb":                                     # any x: just get gdh higher and land
        return lambda x, dh, q: dh >= gdh and q["z"] == 0
    if mode == "boss":                                      # Robo-Manus gone from the object table
        return lambda x, dh, q: not q["boss_alive"]
    if mode == "reach_w":                                   # water variants: no "on the ground" requirement
        return lambda x, dh, q: x >= gx and dh >= gdh
    if mode == "reach_down_w":
        return lambda x, dh, q: x >= gx and dh <= gdh
    if mode == "reach_left_w":
        return lambda x, dh, q: x <= gx and dh >= gdh
    if mode == "reach_down_left_w":
        return lambda x, dh, q: x <= gx and dh <= gdh
    if mode == "reach_band_w":                              # past gx with the height within 12 of gdh (water)
        return lambda x, dh, q: x >= gx and abs(dh - gdh) <= 12
    if mode == "explore":                                   # map what is reachable (use with L4S_TRACE); with gx > 0 also a goal
        return (lambda x, dh, q: x >= gx and dh >= gdh) if gx > 0 else (lambda x, dh, q: False)
    if mode == "follow":                                    # caught up with the TAS path's goal index, close to it, same medium
        gd = int(__import__('os').environ.get('L4S_GOALDIST', 16))
        return lambda x, dh, q: (q["pj"] >= int(FOLLOW.split(",")[1]) and q["dist"] <= gd and (q["swim"] or not TP[q["pj"]][3])
                                 and (q["z"] == 0 or q["swim"] or GOALAIR))       # never end a section mid-jump (L4S_GOALAIR: hanging is fine)
    return lambda x, dh, q: x >= gx and dh >= gdh and q["z"] == 0


def make_rank(mode, gx, gdh):
    if mode == "rat":                                       # a fight: reward damage on the nearest rat, then closeness
        return lambda n: (n.get("rat_hp") if n.get("rat_hp") is not None else 99) * 4 + abs(n.get("rat_dx", 60))
    if mode == "l4warp":                                    # Arctic Caverns' end: down the lift shaft until the warp spawns, then up to it
        wdh = int(__import__('os').environ.get('L4S_WARPDH', 11))
        return lambda n: ((2000 + abs(gx - n["x"])) if not n.get("lift") else 2 * (n["lift"] - 0x16c0) + abs(gx - n["x"]) / 4) if n.get("optr", 0) < 0xf574 else -1000 + abs(779 - n["x"]) + 2 * abs(wdh - n["dh"])
    if mode == "reach_left":
        return lambda n: max(0, n["x"] - gx) + 2 * max(0, gdh - n["dh"])
    if mode == "reach_x":
        return lambda n: max(0, gx - n["x"])
    if mode == "reach_down_left":
        return lambda n: max(0, n["x"] - gx) + 2 * max(0, n["dh"] - gdh)
    if mode == "climb":
        return lambda n: -n["dh"] * 4 + (1 if not n.get("act") else 0)
    if mode == "boss":
        return lambda n: -n["score"] * 10 + n["boss_dx"] / 32
    if mode == "ctr":                                       # hits on a boss: the counter first, closeness to the foe second
        fd = float(__import__('os').environ.get('L4S_FOEDX', 0.25))
        return lambda n: -n.get("ctr", 0) * 100 + fd * n.get("foedx", 0)
    if mode in ("reach_w", "reach_down_w"):
        return lambda n: max(0, gx - n["x"]) + 2 * (max(0, gdh - n["dh"]) if mode == "reach_w" else max(0, n["dh"] - gdh))
    if mode == "reach_band_w":
        return lambda n: max(0, gx - n["x"]) + 2 * abs(n["dh"] - gdh)
    if mode == "explore":                                   # diversity: a hash of the position bucket
        return lambda n: hash((n["x"] // 8, n["dh"] // 8)) % 1000
    if mode == "follow":                                    # progress along the TAS path first, closeness second
        if __import__('os').environ.get('L4S_RATDEAD'):     # Rat Race boot: damage on the rat outranks path progress
            fw = float(__import__('os').environ.get('L4S_FOEW', 3))   # weight per hp point (The Revolution's Hornheads: 16 hp per hit -> use ~20)
            fd = float(__import__('os').environ.get('L4S_FOEDX', 0))  # pull toward the live foe (per px)
            i1 = int(FOLLOW.split(",")[1])                            # no credit for running past the section's end while the foe lives
            return lambda n: (fw * (n.get("giblet") if n.get("giblet") is not None else 255) - min(n["pj"], i1)
                              + (2 * n["dist"] if n["pj"] < i1 else 0)       # past the end: free to go back to the foe
                              + fd * n.get("foedx", 0)
                              - (n["dh"] if n.get("giblet") is None else 0))   # no foe on screen yet: climb (the camera spawns it)
        return lambda n: -n["pj"] + 2 * n["dist"]
    if mode in ("reach_left_w", "reach_down_left_w"):
        return lambda n: max(0, n["x"] - gx) + 2 * (max(0, gdh - n["dh"]) if mode == "reach_left_w" else max(0, n["dh"] - gdh))
    if mode in ("reach", "wallhit", "wall", "reach_down", "reach_band", "room", "teleport"):
        return lambda n: abs(gx - n["x"]) + 2 * abs(gdh - n["dh"])
    return lambda n: -(n["dh"] * 2 + n["x"] / 4)


if __name__ == "__main__":
    bm, gx, gdh = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    mode = sys.argv[5] if len(sys.argv) > 5 else "reach"
    if mode == "reach_left":
        XSIGN = -1
        RANK = lambda n: max(0, n["x"] - gx) + 2 * max(0, gdh - n["dh"])         # distance to the goal corner
    elif mode == "reach_x":                                # ignore height: distance along x only
        RANK = lambda n: max(0, gx - n["x"])
    elif mode == "reach_down_left":
        RANK = lambda n: max(0, n["x"] - gx) + 2 * max(0, n["dh"] - gdh)
    elif mode == "climb":                                  # Intruder Excluder: height is everything; idling loses ties
        RANK = lambda n: -n["dh"] * 4 + (1 if not n.get("act") else 0)
        if __import__('os').environ.get('L4S_RANKGROUND'):  # The Revolution: rank by the last height stood on (jump apexes don't crowd out ledge-waiters)
            RANK = lambda n: -n.get("gdh", 0) * 4 - n["dh"] / 64
    elif mode == "boss":                                   # more smashes (score), then closeness to the boss
        RANK = lambda n: -n["score"] * 10 + n["boss_dx"] / 32
    elif mode == "snowman":                                # the nearest snowman's hp first, then closeness to it (gx)
        RANK = lambda n: (n.get("sm_hp") if n.get("sm_hp") is not None else 99) * 10 + abs(gx - n["x"]) + abs(gdh - n["dh"])
    elif mode == "ctr":                                    # a hit counter (Dark Queen $586), then closeness to the foe
        RANK = make_rank("ctr", gx, gdh)
    elif mode in ("reach_w", "reach_down_w", "reach_left_w", "reach_down_left_w", "reach_band_w", "explore", "follow"):
        RANK = make_rank(mode, gx, gdh)
        if mode == "follow":
            load_tas_path()
    elif mode in ("reach", "wallhit", "wall", "reach_down", "reach_band", "room", "teleport"):    # head for the goal corner (gx, gdh) in every direction
        RANK = lambda n: abs(gx - n["x"]) + 2 * abs(gdh - n["dh"])
    e = BizHawk(log_name=f"l4s_{bm}.log")
    if mode == "snowman":                                  # the nearest snowman dead, toad on the ground
        goal = lambda x, dh, q: q["sm_hp"] == 0 and q["z"] == 0 and dh >= gdh
    elif mode == "wall":                                   # the checkpoint barrier broken, toad on the ground
        goal = lambda x, dh, q: q["wall_hp"] == 0 and q["z"] == 0
    elif mode == "wallhit":                                # any damage to the barrier at all (vs its HP at the root)
        goal = lambda x, dh, q: q["wall_hp"] is not None and q["wall_hp"] < WALL_HP0[0]
    elif mode == "warp":                                   # the level-1 portal engaged (routine pointer $E50D)
        goal = lambda x, dh, q: q["warp"]
    elif mode == "room":
        goal = lambda x, dh, q: not q["marker"]
    elif mode == "teleport":
        goal = lambda x, dh, q: abs(q["x"] - q.get("px", q["x"])) > 100
    elif mode == "reach_down":                             # get DOWN to a floor: x >= gx, height <= gdh
        goal = lambda x, dh, q: x >= gx and dh <= gdh and q["z"] == 0
    elif mode == "reach_band":                             # a specific floor: x >= gx and height within 4 of gdh
        goal = lambda x, dh, q: x >= gx and abs(dh - gdh) <= 4 and q["z"] == 0
    elif mode == "reach_left":
        goal = lambda x, dh, q: x <= gx and dh >= gdh and q["z"] == 0
    elif mode == "reach_x":
        goal = lambda x, dh, q: x >= gx and q["z"] == 0
    elif mode == "reach_down_left":
        goal = lambda x, dh, q: x <= gx and dh <= gdh and q["z"] == 0
    elif mode == "climb":
        goal = lambda x, dh, q: dh >= gdh and q["z"] == 0
    elif mode == "boss":
        goal = lambda x, dh, q: not q["boss_alive"]
    elif mode.endswith("_w") or mode in ("explore", "follow"):
        goal = make_goal(mode, gx, gdh)
    else:
        goal = lambda x, dh, q: x >= gx and dh >= gdh and q["z"] == 0
    if ENDCP:
        goal = lambda x, dh, q: q["cp"] >= ENDCP
    if __import__('os').environ.get('L4S_RATDEAD'):          # Rat Race: the rat booted (hp 0)
        goal = lambda x, dh, q: q["giblet"] == 0 and q.get("foeseen", True) and not q.get("foelive")   # a seen foe dead, none alive
    if mode == "ctr":
        goal = lambda x, dh, q: q["ctr"] >= CTRGOAL
    if ENDOBJ:                                               # The Revolution: the end event object appeared
        goal = lambda x, dh, q: q["endobj"]
    if __import__('os').environ.get('L4S_GOALWARP'):          # any rank mode, but the goal is a warp portal engaged (routine $E50D)
        goal = lambda x, dh, q: q["warp"]
    if mode == "l4warp":
        RANK = make_rank("l4warp", gx, gdh)
        goal = lambda x, dh, q: q["warp"]
    if __import__('os').environ.get('L4S_GOALPTR'):           # the goal is the object loader's pointer reaching this address (hex)
        _gp = int(__import__('os').environ['L4S_GOALPTR'], 16)
        goal = lambda x, dh, q: q["optr"] >= _gp
    if __import__('os').environ.get('L4S_GOALSTILL'):         # the goal must also be reached standing still (no slide into a pit after it)
        _g0 = goal
        goal = lambda x, dh, q, _g0=_g0: _g0(x, dh, q) and q["z"] == 0 and q["spd"] <= 24
    if __import__('os').environ.get('L4S_FOEGONE'):          # Dark Queen: her object gone (the 21st hit), whatever the rank mode
        goal = lambda x, dh, q: q.get("foeseen", True) and not q.get("foelive")
    if __import__('os').environ.get('L4S_BOMBDONE'):         # Rat Race: the bomb kicked (no live 0x5a), toad on the ground
        goal = lambda x, dh, q: not q["bomb"] and q["z"] == 0
    ins, q = search(e, bm, goal, width)
    if ins:
        e.load(bm); e.step((), 2)
        for s in ins:
            e.step(tuple(b for b in s.split("+") if b), 1)
        e.save(f"{bm}_solved")
        (PROJECT / "knowledge" / f"l4s_{bm}.json").write_text(json.dumps(ins))
        print("solved", len(ins), "frames", q)
    else:
        print("unsolved")
    e.close()

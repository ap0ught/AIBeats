"""EARLY track (2026-10-09): Robo-Manus (Level 8's boss) the TAS's way, proved on a snapshot of the verified run up14.

up14's fight: control at frame 15790, first hit 15847, kill 16877 = 1,087 frames from control (49 f a hit; the boss
relocates seven times).  The 1-player TAS (#5093, logs/fix/early_tas1p_l8.txt): 599 frames from control, a smash
every 26 frames with the boss never leaving its corner.  early_l8probe.py shows why: which attack B gives (38 = the
jump-smash that keeps him in place, 24/28/29 punches and 31/30 kicks that send him across the room, 49 the ram) is a
dice roll, and ONE Select press on an earlier frame re-rolls it (the TAS presses Select/Up/Down between blows).  He
jumps every ~165 frames; a smash right at take-off knocks him back down, a toad standing under him when he lands dies,
so around a jump the TAS uses a jump attack (direction+A, then direction+B in the air).

This is a hit-by-hit beam on savestates.  Node = the state right after a hit.  A candidate is one randomised cycle:
    wait to land (Select on random frames = dice noise) -> walk into reach -> optional delay ->
    either direction+B on the ground (kept only if the smash, anim 38, comes out)
    or a jump attack: direction+A for a few frames, a gap, direction+B in the air
It is kept when the score counts the next hit and the toad is unhurt.  A node whose toad then dies simply has no
children.  The W fastest nodes per hit are expanded.

    python early_l8fight.py [width=10] [tries=80] [out=l8fight_c] [seed=3]
    -> logs/fix/early_<out>.json   {inputs from up14 frame 15790, hits, attacks, kill frame}
No memory writes; nothing here is assembled into a route.
"""
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR

ROOT_FRAME = 15790                       # up14: the frame the arrival cutscene hands control back (toad at x 128)
F = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "height": 0x439, "z": 0x475, "anim": 0x3B5, "st": 0x4B1, "hp": 0x51A,
     "face": 0x4A2, "lives": 0x11}
for k in range(6):
    F[f"sc{k}"] = 0x5F4 + k
for q in range(1, 15):
    F[f"id{q}"] = 0x3C1 + q
    F[f"ox{q}"] = 0x3FD + q
    F[f"oh{q}"] = 0x439 + q

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
score = lambda s: int("".join(str(s[f"sc{k}"] & 15) for k in range(6)))


def boss(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x7D:
            return s[f"ox{q}"], s[f"oh{q}"]
    return None


def grounded(s):
    return s.z == 0 and 1 <= s.anim <= 8


def candidate(e, s0, rng, horizon, final=False, loose=False):
    """one randomised cycle from the loaded node -> (inputs, state, attack anim, mode) at the next score change, or None"""
    p_sel = rng.choice([0.0, 0.05, 0.1, 0.2, 0.35])
    noise = rng.choice(["Select", "Select", "Select", "Up", "Down"])
    hold_air = rng.random() < 0.5
    reach = rng.choice([6, 7, 8, 9, 10, 11, 12])
    delay = rng.choice([0, 0, 0, 0, 1, 2, 3, 4, 6, 8, 10, 14])
    gap = rng.choice([0, 1, 1, 2])                               # released frames between a walk/run and the press
    run = rng.random() < 0.6
    mode = "jump" if rng.random() < 0.35 else "ground"
    a_frames = rng.choice([1, 1, 2, 3, 4])                       # the TAS: direction+A one frame, direction one frame, direction+B
    air_gap = rng.choice([0, 1, 1, 2, 3, 5])
    s, ins, sc0 = s0, [], score(s0)
    phase, cnt, tap, moved, attack, since = "land", 0, 0, False, None, 0
    for _ in range(horizon):
        b = boss(s)
        if b is None:
            return None
        d = b[0] - s.x
        dirn = "Right" if d >= 0 else "Left"
        inp = ()
        if phase == "land":
            if grounded(s):
                phase = "ground"
            else:
                if hold_air:
                    inp = (dirn,)
                if rng.random() < p_sel:
                    inp = tuple(sorted(set(inp) | {"Select"})) if noise == "Select" else (inp or (noise,))
        if phase == "ground":
            if abs(d) > reach:
                moved = True
                if run and abs(d) > 30 and tap < 2:              # legal double tap: tap, gap, hold
                    inp = [(dirn,), ()][tap]
                    tap += 1
                else:
                    inp = (dirn,)
            elif moved and cnt < gap:
                cnt += 1
                inp = ()
            elif cnt < gap + delay if moved else cnt < delay:
                cnt += 1
                inp = ("Select",) if rng.random() < p_sel else ()
            elif mode == "ground":
                inp = (dirn, "B")
                phase, cnt, since = "hold", 5, 0
            else:
                inp = (dirn, "A")
                phase, cnt = "jumpA", a_frames - 1
        elif phase == "jumpA":
            if cnt > 0:
                inp = (dirn, "A")
                cnt -= 1
            else:
                phase, cnt = "airgap", air_gap
        if phase == "airgap":
            if cnt > 0:
                inp = (dirn,)
                cnt -= 1
            else:
                inp = (dirn, "B")
                phase, cnt, since = "hold", 5, 0
        elif phase == "hold" and since > 0:
            if cnt > 0:
                inp = (dirn,)
                cnt -= 1
            else:
                phase = "wait"
        if phase == "wait":
            inp = ()
            if grounded(s) and since > 8:
                return None                                      # landed again without a hit
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if phase in ("hold", "wait"):
            since += 1
            if since == 1:
                attack = s.anim
                if attack != 38 and not final and not loose:
                    return None                                  # only the jump-smash keeps him where he is
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
            return None
        if score(s) != sc0:
            return ins, s, attack, mode
    return None


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    tries = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    out = sys.argv[3] if len(sys.argv) > 3 else "l8fight_c"
    rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 3)
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=f"early_{out}.log", fields=F)
    e.load("cap14_f15000")
    s = None
    prefix = []
    root_frame = ROOT_FRAME
    if len(sys.argv) > 5:                                        # an arrival piece (early_l8arrive3.py): {from_frame, inputs}
        pj = json.load(open(sys.argv[5]))
        for i in range(15000, pj["from_frame"]):
            s = e.step(bt(lines[i]), 1)
        for b in pj["inputs"]:
            s = e.step(bt(b), 1)
        prefix = list(pj["inputs"])
        root_frame = pj["from_frame"] + len(prefix)
    else:
        for i in range(15000, ROOT_FRAME):
            s = e.step(bt(lines[i]), 1)
    print(f"root: frame {root_frame} toad x {s.x} h {s.height} anim {s.anim} boss {boss(s)} score {score(s)} hp {s.hp}", flush=True)
    nodes = [{"sid": e.msave(), "ins": [], "state": s, "hits": [], "attacks": []}]
    level = 0
    best = nodes[0]
    while True:
        level += 1
        kids = []
        for horizon, loose in (((90 if level == 1 else 50), False), (240, True)):
            for nd in nodes:
                for _ in range(tries):
                    e.mload(nd["sid"])
                    r = candidate(e, nd["state"], rng, horizon, final=len(nd["hits"]) >= 21, loose=loose)
                    if r is None:
                        continue
                    ins, s2, attack, mode = r
                    kids.append({"ins": nd["ins"] + ins, "state": s2, "hits": nd["hits"] + [len(nd["ins"]) + len(ins)],
                                 "sid": e.msave(), "gain": score(s2) - score(nd["state"]),
                                 "attacks": nd["attacks"] + [f"{mode[0]}{attack}"]})
            if kids:
                break                                            # the loose long horizon is only a fallback (a chase)
        if not kids:
            print(f"level {level}: no candidate lands a hit - stopped", flush=True)
            break
        kids.sort(key=lambda k: (len(k["ins"]), rng.random()))
        keep, seen = [], {}                                      # the W fastest, at most 2 per (length, boss height)
        for k in kids:
            key = (len(k["ins"]), boss(k["state"]))
            n = seen.get(key, 0)
            if len(keep) < width and n < 2:
                keep.append(k)
                seen[key] = n + 1
            else:
                e.mfree(k["sid"])
        for nd in nodes:
            e.mfree(nd["sid"])
        nodes = keep
        best = nodes[0]
        prev_hit = best["hits"][-2] if len(best["hits"]) > 1 else 0
        print(f"hit {level}: {len(kids)} landed; best +{len(best['ins'])} (interval {best['hits'][-1] - prev_hit}) +{best['gain']} "
              f"attack {best['attacks'][-1]} boss {boss(best['state'])} toad x {best['state'].x} h {best['state'].height}; "
              f"kept {[(len(k['ins']), k['attacks'][-1], (boss(k['state']) or (0, 0))[1]) for k in nodes]}", flush=True)
        json.dump({"root_frame": root_frame, "arrival_prefix": prefix, "inputs": best["ins"], "hits": best["hits"], "attacks": best["attacks"], "partial": True},
                  open(LOGS_DIR / "fix" / f"early_{out}_partial.json", "w"))
        done = [k for k in nodes if boss(k["state"]) is None or k["gain"] >= 10000]
        if done:
            best = done[0]
            break
        if level >= 28:
            break
    res = {"root_frame": root_frame, "arrival_prefix": prefix, "arrival_from_frame": root_frame - len(prefix),
           "inputs": best["ins"], "hits": best["hits"], "attacks": best["attacks"],
           "note": "from up14 frame 15790 (control after the arrival cutscene); snapshot proof, not a route segment",
           "kill_frame_abs": root_frame + len(best["ins"]), "up14_kill_frame": 16877, "up14_first_hit": 15847,
           "complete": bool(boss(best["state"]) is None or best.get("gain", 0) >= 10000)}
    json.dump(res, open(LOGS_DIR / "fix" / f"early_{out}.json", "w"), indent=1)
    print(f"RESULT {out}: {len(best['hits'])} scoring blows in {len(best['ins'])} frames from control, complete={res['complete']} "
          f"(up14: 1,087 = 15790 -> 16877; TAS: 599 = its control 50566 -> 51165). "
          f"Kill at absolute frame {root_frame + len(best['ins'])} vs 16877: saves {16877 - root_frame - len(best['ins'])} frames", flush=True)
    e.close()


if __name__ == "__main__":
    main()

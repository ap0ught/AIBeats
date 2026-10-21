"""Track C: Robo-Manus behind a climb (chain B's u16b_fight.py + chain A's fixes from u16a_l8fight.py + ranking by kill + death).

    python u17c_fight.py <climb json> <out tag> [width=12] [tries=100] [seed=5] [earlier fight json] [hits of it to keep]
        climb json = {from_frame 12488, inputs through the control frame}; root = bookmark early_L8_p0 (the Level 8 placement:
        behind C6 the level is bit-identical to the old lineage from its frame 8, so this root is the route's own state)
    -> logs/fix/u17c_fight_<out>.json {climb, root_frame, inputs (control -> killing blow), hits, attacks, complete, death, cost}
       logs/fix/u17c_fight_<out>_partial.json after every hit
Differences from u16b_fight.py: the 84-frame strict tier and the loose tier are also used when the short tier leaves fewer than
half a beam; the last three generations are kept and a dead end goes back two blows with a doubled beam (u16a_l8fight.py); the
KILL is ranked by kill frame + the boss's death time (437 frames after a ground blow, 443 after a jump attack: u16b_notes),
over ALL killing candidates of the generation and of the next one (a kill one generation later can still be sooner).
No memory writes; nothing here is a route segment."""
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR
from early_l8fight import candidate, boss, score, F, bt
from u17c_lib import write_json, FIX

P0 = 12488
CREF = 1085                                                      # kill + death of fight b3 on climb C4, which merges with A9r behind a 44-frame page


def pad(c):
    """frames the page costs over 44 so that the Terra Tubes entry merges with the A9r lineage (u17c_notes section 4, refined):
    play and load frames advance the hidden class by 1 each (period 3), the frames a card WAITS for its press do not.  The
    dice give a 44-frame page (45 = one more wait frame) or a 46-frame page (two more LOAD frames, 47 with a wait frame).
    With CREF = 1085 (fight b3, merges behind 44):  c = CREF (mod 3): 44, or 45 when c is even;  c = CREF + 1 (mod 3): 46 / 47;
    c = CREF + 2 (mod 3): never (it would take a 48-frame load)."""
    m = (c - CREF) % 3
    odd = (c - CREF) % 2
    if m == 0:
        return odd
    if m == 1:
        return 2 + odd
    return 1000


def death(k):
    """frames from the killing blow to the level byte leaving 7 = 277 + the dead body's flight; measured on 12 stored fights
    (u17c_death.py): 437 with the boss on the floor (h 30..37), 442 at h 72-73, 443 at h 78-79 -> 437 + (h - 30) // 8"""
    s = k["state"]
    for q in range(1, 15):
        if s[f"id{q}"] == 0x46:
            return 437 + max(0, (s[f"oh{q}"] - 30)) // 8
    return 437 if k["attacks"][-1].startswith("g") else 443


def main():
    climb = sys.argv[1]
    out = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    tries = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    rng = random.Random(int(sys.argv[5]) if len(sys.argv) > 5 else 5)
    cj = json.load(open(climb))
    assert cj["from_frame"] == P0
    e = BizHawk(log_name=f"u17c_fight_{out}.log", fields=F)
    s = e.load("early_L8_p0")
    for b in cj["inputs"]:
        s = e.step(bt(b), 1)
    root_frame = P0 + len(cj["inputs"])
    print(f"root: frame {root_frame} (up14: 15790) toad x {s.x} h {s.height} anim {s.anim} boss {boss(s)} score {score(s)} hp {s.hp} lives {s.lives}", flush=True)
    assert s.hp == 47 and boss(s) is not None and s.anim != 50
    keep_ins, keep_hits, keep_att = [], [], []
    if len(sys.argv) > 7:
        kj = json.load(open(sys.argv[6]))
        K = int(sys.argv[7])
        assert kj["root_frame"] == root_frame
        keep_ins, keep_hits, keep_att = list(kj["inputs"][:kj["hits"][K - 1]]), list(kj["hits"][:K]), list(kj["attacks"][:K])
        for b in keep_ins:
            s = e.step(bt(b), 1)
        print(f"resumed after hit {K} of {sys.argv[6]}: +{len(keep_ins)} toad x {s.x} boss {boss(s)} score {score(s)} hp {s.hp}", flush=True)
    nodes = [{"sid": e.msave(), "ins": keep_ins, "state": s, "hits": keep_hits, "attacks": keep_att}]
    level = len(keep_hits)
    history, backtracks, boost = [], 0, 0
    best_kill = None                                             # (cost = kill + death, kid)
    extra_gens = 0
    while True:
        level += 1
        kids = []
        for horizon, loose in (((90 if level == 1 else 50), False), (84, False), (240, True)):
            for nd in nodes:
                for _ in range(tries if not loose else max(20, tries // 3)):
                    e.mload(nd["sid"])
                    r = candidate(e, nd["state"], rng, horizon, final=len(nd["hits"]) >= 21, loose=loose)
                    if r is None:
                        continue
                    ins, s2, attack, mode = r
                    kids.append({"ins": nd["ins"] + ins, "state": s2, "hits": nd["hits"] + [len(nd["ins"]) + len(ins)],
                                 "sid": e.msave(), "gain": score(s2) - score(nd["state"]),
                                 "attacks": nd["attacks"] + [f"{mode[0]}{attack}"]})
            if len(kids) >= max(4, width // 2):
                break
        if not kids:
            if best_kill is not None:
                break
            if history and backtracks < 10:
                backtracks += 1
                for nd in nodes:
                    e.mfree(nd["sid"])
                if len(history) > 1:
                    for nd in history.pop():
                        e.mfree(nd["sid"])
                nodes = history.pop()
                level = len(nodes[0]["hits"])
                boost = 4
                print(f"dead end: back to the generation after blow {level}, beam doubled for 4 blows (backtrack {backtracks})", flush=True)
                continue
            print(f"level {level}: no candidate lands a hit - stopped", flush=True)
            break
        # killing candidates: rank by kill + death over ALL of them
        for k in kids:
            if boss(k["state"]) is None or k["gain"] >= 10000:
                c = len(k["ins"]) + death(k)
                c = c + pad(c)
                if best_kill is None or c < best_kill[0]:
                    best_kill = (c, {q: k[q] for q in ("ins", "hits", "attacks", "state", "gain")})
        live = [k for k in kids if not (boss(k["state"]) is None or k["gain"] >= 10000)]
        for k in kids:
            if k not in live:
                e.mfree(k["sid"])
        live.sort(key=lambda k: (len(k["ins"]), rng.random()))
        keep, seen = [], {}
        for k in live:
            key = (len(k["ins"]), boss(k["state"]))
            n = seen.get(key, 0)
            if len(keep) < width * (2 if boost > 0 else 1) and n < 2:
                keep.append(k)
                seen[key] = n + 1
            else:
                e.mfree(k["sid"])
        history.append(nodes)
        while len(history) > 3:
            for nd in history.pop(0):
                e.mfree(nd["sid"])
        boost = max(0, boost - 1)
        if best_kill is not None:
            # live nodes that can still beat the best kill: one more blow costs at least 18 frames
            keep2 = [k for k in keep if len(k["ins"]) + 18 + 437 < best_kill[0]]
            for k in keep:
                if k not in keep2:
                    e.mfree(k["sid"])
            keep = keep2
            extra_gens += 1
            print(f"hit {level}: kill in hand: +{len(best_kill[1]['ins'])} last attack {best_kill[1]['attacks'][-1]} cost {best_kill[0]}; {len(keep)} live nodes could still beat it", flush=True)
            if not keep or extra_gens >= 3:
                break
            nodes = keep
            continue
        if not keep:
            break
        nodes = keep
        best = nodes[0]
        prev_hit = best["hits"][-2] if len(best["hits"]) > 1 else 0
        print(f"hit {level}: {len(kids)} landed; best +{len(best['ins'])} (interval {best['hits'][-1] - prev_hit}) +{best['gain']} "
              f"attack {best['attacks'][-1]} boss {boss(best['state'])} toad x {best['state'].x} h {best['state'].height}; "
              f"kept {[(len(k['ins']), k['attacks'][-1], (boss(k['state']) or (0, 0))[1]) for k in nodes][:8]}", flush=True)
        write_json(FIX / f"u17c_fight_{out}_partial.json", {"climb": climb, "root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"],
                                                            "attacks": best["attacks"], "partial": True})
        if level >= 30:
            break
    if best_kill is None:
        print(f"RESULT {out}: no kill", flush=True)
        e.close()
        return
    cost, best = best_kill
    st = best["state"]
    res = {"climb": climb, "root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"], "attacks": best["attacks"],
           "kill_frame_abs": root_frame + len(best["ins"]), "up14_kill_frame": 16877, "complete": True, "death": death(best), "cost": len(best["ins"]) + death(best), "cost_padded": cost,
           "hp": st.hp, "lives": st.lives, "score": score(st),
           "note": "from the control frame of the climb (inputs from up14 frame 12488 = climb + these); snapshot proof, not a route segment"}
    write_json(FIX / f"u17c_fight_{out}.json", res, indent=1)
    print(f"RESULT {out}: {len(best['hits'])} scoring blows in {len(best['ins'])} frames from control, last attack {best['attacks'][-1]} (death {death(best)}; padded to the A9r phase: {cost}), "
          f"kill + death {cost}; kill at absolute frame {root_frame + len(best['ins'])}; hp {st.hp} lives {st.lives} score {score(st)}", flush=True)
    e.close()


if __name__ == "__main__":
    main()

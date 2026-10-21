"""u16b (chain B): Robo-Manus behind a NEW climb.  The hit-by-hit beam of early_l8fight.py (its candidate() is imported
unchanged: jump-smashes only, Select re-rolls), rooted on the control frame of a climb found by u16b_climb.py.

    python u16b_fight.py <climb json> <out tag> [width=10] [tries=100] [seed=5] [earlier fight json] [hits of it to keep]
        climb json = {from_frame 12488, inputs through the control frame}   (logs/fix/u16b_climb_<tag>.json)
    -> logs/fix/u16b_fight_<out>.json  {climb, root_frame, inputs (from control to the killing blow), hits, attacks, complete}
       logs/fix/u16b_fight_<out>_partial.json after every hit
No memory writes; nothing here is a route segment (u16b_build.py makes B8)."""
import json
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR
from early_l8fight import candidate, boss, score, F, bt
from u16b_lib import write_json, FIX, P0


def main():
    climb = sys.argv[1]
    out = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    tries = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    rng = random.Random(int(sys.argv[5]) if len(sys.argv) > 5 else 5)
    cj = json.load(open(climb))
    assert cj["from_frame"] == P0
    e = BizHawk(log_name=f"u16b_fight_{out}.log", fields=F)
    s = e.load("early_L8_p0")
    for b in cj["inputs"]:
        s = e.step(bt(b), 1)
    root_frame = P0 + len(cj["inputs"])
    print(f"root: frame {root_frame} (up14: 15790) toad x {s.x} h {s.height} anim {s.anim} boss {boss(s)} score {score(s)} hp {s.hp} lives {s.lives}", flush=True)
    assert s.hp == 47 and boss(s) is not None and s.anim != 50
    keep_ins, keep_hits, keep_att = [], [], []
    if len(sys.argv) > 7:                                        # resume: keep the first K hits of an earlier fight on the SAME climb
        kj = json.load(open(sys.argv[6]))
        K = int(sys.argv[7])
        assert kj["climb"] == climb and kj["root_frame"] == root_frame
        keep_ins, keep_hits, keep_att = list(kj["inputs"][:kj["hits"][K - 1]]), list(kj["hits"][:K]), list(kj["attacks"][:K])
        for b in keep_ins:
            s = e.step(bt(b), 1)
        print(f"resumed after hit {K} of {sys.argv[6]}: +{len(keep_ins)} toad x {s.x} boss {boss(s)} score {score(s)} hp {s.hp}", flush=True)
    nodes = [{"sid": e.msave(), "ins": keep_ins, "state": s, "hits": keep_hits, "attacks": keep_att}]
    level = len(keep_hits)
    best = nodes[0]
    while True:
        level += 1
        kids = []
        for horizon, loose in (((90 if level == 1 else 50), False), (84, False), (240, True)):
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
            if len(kids) >= max(4, width // 2):
                break                                            # the longer / loose horizons are fallbacks (a chase); chain A's fix:
                                                                 # also used when the short tier leaves fewer than half a beam
        if not kids:
            print(f"level {level}: no candidate lands a hit - stopped", flush=True)
            break
        kids.sort(key=lambda k: (len(k["ins"]), rng.random()))
        keep, seen = [], {}                                      # the W fastest, at most 2 per (length, boss position)
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
              f"kept {[(len(k['ins']), k['attacks'][-1], (boss(k['state']) or (0, 0))[1]) for k in nodes][:8]}", flush=True)
        write_json(FIX / f"u16b_fight_{out}_partial.json", {"climb": climb, "root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"],
                                                            "attacks": best["attacks"], "partial": True})
        done = [k for k in nodes if boss(k["state"]) is None or k["gain"] >= 10000]
        if done:
            best = done[0]
            break
        if level >= 28:
            break
    complete = bool(boss(best["state"]) is None or best.get("gain", 0) >= 10000)
    st = best["state"]
    res = {"climb": climb, "root_frame": root_frame, "inputs": best["ins"], "hits": best["hits"], "attacks": best["attacks"],
           "kill_frame_abs": root_frame + len(best["ins"]), "up14_kill_frame": 16877, "complete": complete,
           "hp": st.hp, "lives": st.lives, "score": score(st),
           "note": "from the control frame of the climb (inputs from up14 frame 12488 = climb + these); snapshot proof, not a route segment"}
    write_json(FIX / f"u16b_fight_{out}.json", res, indent=1)
    print(f"RESULT {out}: {len(best['hits'])} scoring blows in {len(best['ins'])} frames from control, complete={complete}; "
          f"kill at absolute frame {root_frame + len(best['ins'])} vs up14's 16877: saves {16877 - root_frame - len(best['ins'])} frames; "
          f"hp {st.hp} lives {st.lives} score {score(st)}", flush=True)
    e.close()


if __name__ == "__main__":
    main()

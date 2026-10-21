"""Run the old Level 3 rat/pit policy (l3.attempt) from the TAS-synced state L3_tas_13919; grow a separate pit map
(knowledge/l3_pits_fast.json) by dying, and keep the fastest line that reaches the bikes
(knowledge/l3_fast_best.json, inputs after L3_tas_13919)."""
import json, random, sys
from toads.emulator import BizHawk
import l3

MAP = "knowledge/l3_pits_fast.json"

def main(rounds):
    e = BizHawk(log_name="l3fast.log")
    try:
        jumps = json.load(open(MAP))
    except FileNotFoundError:
        jumps = [j for j in json.load(open("knowledge/l3_pits.json")) if j > 700]
    best = None; rng = random.Random(7)
    for r in range(rounds):
        seed = rng.randrange(1000)
        out, ins, info = l3.attempt(e, seed, sorted(jumps), bookmark="L3_tas_13919", max_frames=3000)
        print(r, seed, out, len(ins), info.get("x"), "edge", info.get("edge"), "jumps", sorted(jumps), flush=True)
        if out == "died" and info.get("edge"):
            ex = info["edge"]
            near = [j for j in jumps if abs(j - ex) < 40]
            if near:                                      # the jump before this pit was too late/early: move it
                jumps.remove(near[0]); jumps.append(near[0] - rng.choice([4, 8, 12, 16]))
            else:
                jumps.append(ex - rng.choice([8, 16, 24]))
            json.dump(sorted(jumps), open(MAP, "w"))
        if out == "bikes" and (best is None or len(ins) < len(best)):
            best = ins
            json.dump(best, open("knowledge/l3_fast_best.json", "w"))
            print("  NEW BEST", len(best), flush=True)
    print("best", len(best) if best else None)
    e.close()

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)

"""Acts 3-4: open-loop replay of a stage input file from a start state; reports the next-stage load frame and the
carried resources, saves the end state.

    python ng/stages/a34_verify.py <rows name in logs/a34> <start state> <stage name> [--save <state name>]
    python ng/stages/a34_verify.py --chain <start state> <name1> <name2> ...   (consecutive stages)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402


def replay(e, rows, stage):
    e.trace(True)
    e.run(rows)
    tr = e.last_trace
    e.trace(False)
    load = next((x["frame"] for x in tr if x["stage"] != stage), None)
    last_in = [x for x in tr if x["stage"] == stage]
    s = last_in[-1] if last_in else tr[-1]
    return load, s, tr[-1]


def main():
    args = sys.argv[1:]
    save = ""
    if "--save" in args:
        i = args.index("--save")
        save = args[i + 1]
        del args[i:i + 2]
    e = K.open_emu("a34_verify.log")
    try:
        if args[0] == "--chain":
            st = e.load(args[1])
            for nm in args[2:]:
                rows = K.load_rows(nm)
                stage = st.stage if hasattr(st, "stage") else st["stage"]
                load, s, end = replay(e, rows, stage)
                print(f"{nm}: stage {K.STAGES[stage][0]} load {load} end frame {end['frame']} item {s['item']} "
                      f"ninpo {s['ninpo']} hp {s['hp']} timer {s['timer']} rng {end['rng']}")
                st = end
        else:
            name, start, sname = args[0], args[1], args[2]
            stage = K.BY_NAME[sname]
            s0 = e.load(start)
            rows = K.load_rows(name)
            load, s, end = replay(e, rows, stage)
            print(f"{name}: from {start} frame {s0.frame}; rows {len(rows)}; load {load} (TAS {K.TAS_LOAD[stage]}, "
                  f"{(load or 0) - K.TAS_LOAD[stage]:+d}); end frame {end['frame']}; last play state item {s['item']} "
                  f"ninpo {s['ninpo']} hp {s['hp']} timer {s['timer']}; end rng {end['rng']}")
            if save:
                e.save(save)
                print("saved", save)
    finally:
        e.close()


if __name__ == "__main__":
    main()

"""DEBUG ONLY: stage-start savestates for stage 3 / stage 8 with other start conditions (never part of a run).

    python tools/s3_mkvariants.py <stage 3|8> <k1,k2,...> [weapon=0x13]

Like tools/mk_stage_state.py, but the opening waits k extra frames on the title screen before Select / Start, so
the frame counter ($1A) and the random number ($34) at the stage's first frame differ. Saves
states/s<stage>/var<k>_pre.State (one frame before the first playable frame) and prints fc / rng at L.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import F  # noqa: E402

stage = int(sys.argv[1])
ks = [int(x) for x in sys.argv[2].split(",")]
weapon = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x13
opening = read_inputs(LOGS_DIR / "open_nh.inputs.txt")
for k in ks:
    with BizHawk(log_name=f"mkvar{stage}_{k}.log", fields=F) as e:
        rows = opening[:9] + [()] * k + opening[9:20]
        s = e.run(rows)
        n = 0
        while not (s["groutine"] == 5 and s["lroutine"] == 0) and n < 800:
            s = e.step((), 1)
            n += 1
        assert s["groutine"] == 5 and s["lroutine"] == 0, s
        e.poke(0x30, stage - 1)
        sid = None
        n = 0
        while True:
            prev = sid
            sid = e.msave()
            s = e.step((), 1)
            n += 1
            if s["lroutine"] == 4:
                break
            if prev:
                e.mfree(prev)
            assert n < 2000, s
        e.mload(sid)
        e.poke(0xAA, weapon)
        name = f"s{stage}/var{k}_pre"
        e.save(name)
        s2 = e.step((), 1)
        print(f"stage {stage} delay {k}: saved states/{name}.State; L = frame {s2['frame']}, fc {s2['fc']}, rng {s2['rng']}, "
              f"weapon ${e.byte(0xAA):02x}", flush=True)

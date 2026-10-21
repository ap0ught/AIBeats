"""Rule v2 runs, one after the other (3 emulators each): the stage 8 solver from the start conditions named on the
command line, and stage 3 once. Each solver's output goes to logs/s8/v3/<name>.out.

    python tools/s8c_runall.py dbg var1 var37 c1 s3 [--quick]

    dbg    states/dbg/s8_pre                         -> logs/s8/v3_dbg.*
    var1   states/s8/var1_pre                        -> logs/s8/v3_var1.*
    var37  states/s8/var37_pre                       -> logs/s8/v3_var37.*
    c1     states/s8c/c1_s8_pre (copy of chain1/states/s8_pre.State, the verified run's real state) with the real
           press history chain1/runs/prior_s8_c1b.inputs.txt (= through_s7.inputs.txt without its last row, which
           is the row the solver replaces)           -> logs/s8/v3_c1.*
    s3     states/dbg/s3_pre                         -> logs/s3/v3_dbg.*
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = {
    "dbg": ["-m", "contra.stages.s8", "dbg/s8_pre", "--out", "s8/v3_dbg"],
    "var1": ["-m", "contra.stages.s8", "s8/var1_pre", "--out", "s8/v3_var1"],
    "var37": ["-m", "contra.stages.s8", "s8/var37_pre", "--out", "s8/v3_var37"],
    "c1": ["-m", "contra.stages.s8", "s8c/c1_s8_pre", "--out", "s8/v3_c1", "--prior",
           str(ROOT / "chain1" / "runs" / "prior_s8_c1b.inputs.txt")],
    "s3": ["-m", "contra.stages.s3", "dbg/s3_pre", "--out", "s3/v3_dbg"],
}

if __name__ == "__main__":
    args = sys.argv[1:]
    extra = []
    for flag in ("--quick", "--metronome"):
        if flag in args:
            args.remove(flag)
            extra.append(flag)
    (ROOT / "logs" / "s8" / "v3").mkdir(parents=True, exist_ok=True)
    for name in args:
        spec = name.split("=")              # name or name=suffix (a second run under another output name)
        cmd = list(JOBS[spec[0]])
        if len(spec) > 1:
            cmd[cmd.index("--out") + 1] += spec[1]
        outp = ROOT / "logs" / "s8" / "v3" / f"{name.replace('=', '')}.out"
        t0 = time.time()
        with open(outp, "w", encoding="utf-8") as f:
            rc = subprocess.call([sys.executable, "-u"] + cmd + (extra if spec[0] != "s3" else []), cwd=str(ROOT),
                                 stdout=f, stderr=subprocess.STDOUT)
        print(f"{name}: exit {rc} in {time.time() - t0:.0f}s -> {outp}", flush=True)

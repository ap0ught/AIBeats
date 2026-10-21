"""Rule v2: run the stage 1 / stage 5 solves and their verification one after the other (never more than 3
emulators at a time: every step is its own process and they do not overlap).

    python tools/s1c_queue.py <step> [<step> ...]

steps:  s1:<k>     solve stage 1 from states/s1/pre_w<k> -> logs/s1/w<k>v3.seg.json, then verify (below)
        v1:<k>     verify only: tools/s1_finish.py (one replay after a core reboot, timeline, check_inputs at its
                   defaults), check_inputs with rule v2's windows, assemble.py (two fresh-launch replays, sha1)
                   and, for k = 0, tools/s1b_states.py (hand-over states with the suffix v3)
        s5:<name>  solve stage 5: d0 = dbg/s5_pre, w1 = s5/pre_w1, w37 = s5/pre_w37, c1 = s5/c1_pre (the real
                   state of the verified run, a copy of chain1/states/s5_pre.State) with the real press history
                   chain1/runs/prior_s5_c1.inputs.txt -> logs/s5/<name>_v3.seg.json, then verify
        v5:<name>  verify only: tools/s5_finish.py (open-loop replay on a fresh emulator) and tools/s5c_check.py
Everything is appended to logs/s1c_queue.log; each solver's own output goes to logs/s<N>/solve_<name>.log.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "s1c_queue.log"
PY = sys.executable
S5 = {"d0": ("dbg/s5_pre", None), "w1": ("s5/pre_w1", None), "w37": ("s5/pre_w37", None),
      "c1": ("s5/c1_pre", "chain1/runs/prior_s5_c1.inputs.txt")}
V2 = ["--windows", "600:109,1800:246"]


def say(*a):
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd, out=None, env=None):
    t0 = time.time()
    e = dict(os.environ)
    e.update(env or {})
    if out is not None:
        with open(ROOT / out, "w", encoding="utf-8") as f:
            rc = subprocess.call([str(c) for c in cmd], cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, env=e)
    else:
        c = subprocess.run([str(x) for x in cmd], cwd=str(ROOT), capture_output=True, text=True, env=e)
        rc = c.returncode
        tail = (c.stdout or "").strip().splitlines()[-14:] + (c.stderr or "").strip().splitlines()[-6:]
        for l in tail:
            say("    |", l[:400])
    say(f"  exit {rc} after {time.time() - t0:.0f} s: {' '.join(str(c) for c in cmd[1:])}")
    return rc


def last_lines(path, n=3):
    try:
        for l in (ROOT / path).read_text(encoding="utf-8", errors="replace").strip().splitlines()[-n:]:
            say("    |", l[:600])
    except OSError:
        pass


def verify1(k):
    w = f"w{k}v3"
    seg = ROOT / "logs" / "s1" / f"{w}.seg.json"
    if not seg.exists():
        say(f"  {w}: no segment, nothing to verify")
        return
    op = ROOT / "logs" / "s1" / f"open_{w}.inputs.txt"
    if not op.exists():
        shutil.copyfile(ROOT / "logs" / "s1" / f"open_w{k}.inputs.txt", op)
    run([PY, "tools/s1_finish.py", w])
    full = f"logs/s1/s1_{w}_full.inputs.txt"
    run([PY, "check_inputs.py", full] + V2 + ["--json", f"logs/s1/s1_{w}_full.check_v2.json"])
    run([PY, "assemble.py", f"s1_{w}_asm", full])
    if str(k) == "0":
        run([PY, "tools/s1b_states.py", w, "v3"], out="logs/s1/states_v3.log")
        last_lines("logs/s1/states_v3.log", 2)


def verify5(name):
    state, hist = S5[name]
    n = f"{name}_v3"
    if not (ROOT / "logs" / "s5" / f"{n}.seg.json").exists():
        say(f"  {n}: no segment, nothing to verify")
        return
    run([PY, "tools/s5_finish.py", state, n])
    run([PY, "tools/s5c_check.py", "5", n] + (["--history", hist] if hist else []))


def main():
    for step in sys.argv[1:]:
        kind, arg = step.split(":")
        say(f"=== {step}")
        if kind == "s1":
            seg = ROOT / "logs" / "s1" / f"w{arg}v3.seg.json"
            if seg.exists():
                os.replace(seg, seg.with_name(seg.name + ".prev"))
            run([PY, "-u", "-m", "contra.stages.s1", f"s1/pre_w{arg}", f"w{arg}v3", "--open", f"logs/s1/open_w{arg}.inputs.txt"],
                out=f"logs/s1/solve_w{arg}v3.log", env={"S1_REPAIR_DEBUG": "1"})
            last_lines(f"logs/s1/solve_w{arg}v3.log", 1)
            verify1(arg)
        elif kind == "v1":
            verify1(arg)
        elif kind == "s5":
            state, hist = S5[arg]
            seg = ROOT / "logs" / "s5" / f"{arg}_v3.seg.json"
            if seg.exists():
                os.replace(seg, seg.with_name(seg.name + ".prev"))
            run([PY, "-u", "-m", "contra.stages.s5", state, f"{arg}_v3"] + (["--history", hist] if hist else []),
                out=f"logs/s5/solve_{arg}_v3.log", env={"S1_REPAIR_DEBUG": "1"})
            last_lines(f"logs/s5/solve_{arg}_v3.log", 2)
            verify5(arg)
        elif kind == "v5":
            verify5(arg)
        else:
            say("unknown step", step)
    say("=== queue done")


if __name__ == "__main__":
    main()

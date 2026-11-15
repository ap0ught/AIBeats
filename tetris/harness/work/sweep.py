"""Run plan100 over a list of settings, a few at a time (default 4 workers, below-normal priority).

    python work/sweep.py NAME "--floor 8 --top 3" "--floor 7 --top 3 --wait 5" ...
Each job writes logs/NAME_<i>.inputs.txt and logs/NAME_<i>.log; a summary line per job is printed at the end.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BELOW_NORMAL = 0x00004000


def run(job):
    i, name, spec = job
    out = f"{name}_{i}"
    log = ROOT / "logs" / f"{out}.log"
    with open(log, "w") as f:
        subprocess.run([sys.executable, "-m", "work.plan100", "--out", out] + spec.split(), cwd=ROOT, stdout=f,
                       stderr=subprocess.STDOUT, creationflags=BELOW_NORMAL)
    plan = [l for l in log.read_text().splitlines() if l.startswith("PLAN") or "died" in l or "no finished" in l]
    return f"{out}: {spec} -> {plan[0] if plan else 'no result'}"


def main():
    name = sys.argv[1]
    jobs = [(i, name, s) for i, s in enumerate(sys.argv[2:])]
    with ThreadPoolExecutor(4) as ex:
        for line in ex.map(run, jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()

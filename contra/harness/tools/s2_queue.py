"""Run several base-stage solves, at most N at a time (one emulator each), each followed by its open-loop replay.

    python tools/s2_queue.py <N> "<stage> <state> <tag> [--pause K] [--hist file]" ...

Output of every job: logs/s<stage>/<tag>_solve.out and <tag>_verify.out; a summary line per job on stdout.
"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(job, lock):
    parts = job.split()
    stage, state, tag = parts[0], parts[1], parts[2]
    base = ROOT / "logs" / f"s{stage}"
    base.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.setdefault("BASE_BOSS_PROCS", "4")
    t = time.time()
    with open(base / f"{tag}_solve.out", "w") as f:
        r1 = subprocess.run([sys.executable, "tools/s2_solve.py"] + parts, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, env=env)
    hist = []
    if "--hist" in parts:
        hist = ["--hist", parts[parts.index("--hist") + 1]]
    v = "not run"
    if (base / f"{tag}.inputs.txt").exists() and r1.returncode == 0:
        with open(base / f"{tag}_verify.out", "w") as f:
            r2 = subprocess.run([sys.executable, "tools/s2_verify.py", stage, tag, state] + hist, cwd=ROOT, stdout=f,
                                stderr=subprocess.STDOUT)
        v = (base / f"{tag}_verify.out").read_text().splitlines()[0] if r2.returncode in (0, 1) else f"verify rc {r2.returncode}"
    with lock:
        print(f"[{time.strftime('%H:%M:%S')}] {job}: solve rc {r1.returncode}, {round(time.time() - t)} s; {v}", flush=True)


def main():
    n = int(sys.argv[1])
    jobs = sys.argv[2:]
    lock = threading.Lock()
    sem = threading.Semaphore(n)
    th = []

    def work(j):
        with sem:
            run(j, lock)
    for j in jobs:
        t = threading.Thread(target=work, args=(j,))
        t.start()
        th.append(t)
        time.sleep(20)          # stagger the emulator launches
    for t in th:
        t.join()
    print("queue finished", flush=True)


if __name__ == "__main__":
    main()

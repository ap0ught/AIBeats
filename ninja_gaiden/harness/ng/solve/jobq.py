"""ng.solve.jobq - RAM-gated job queue (the runq.py of the act agents, one shared copy).

    python -m ng.solve.jobq <jobfile> [--max 3] [--gb 2.5] [--pids logs/tk/pids.txt]

Rules: a job starts only when free RAM >= --gb (default 2.5 GB) and fewer than --max (default 3) of OUR jobs run;
--max drops to 1 while a HOLD_FARMS file exists (logs/HOLD_FARMS or ..\\Contra\\logs\\HOLD_FARMS). Each job is one
shell line (cwd = project; one EmuHawk per job by convention). Lines starting with '#' are skipped; new lines appended
to the job file are picked up; a line "STOP" ends the queue once all jobs finished. Started PIDs (with the command)
are appended to the pid file, so only our own processes are ever killed (kill_tracked()).

Library: free_gb(), hold_active(), Queue(jobfile, maxpar, gb).run(), kill_tracked(pidfile).
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from . import common as C

HOLDS = [C.LOGS / "HOLD_FARMS", C.PROJECT.parent / "Contra" / "logs" / "HOLD_FARMS"]


def free_gb() -> float:
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-c",
                              "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out) / 1048576
    except Exception:
        return 0.0


def hold_active() -> bool:
    return any(h.exists() for h in HOLDS)


class Queue:
    def __init__(self, jobfile, maxpar=3, gb=2.5, pidfile=None):
        self.jf, self.maxpar, self.gb = Path(jobfile), maxpar, gb
        self.pidf = Path(pidfile) if pidfile else C.LOGS / "tk" / "pids.txt"
        self.pidf.parent.mkdir(parents=True, exist_ok=True)

    def run(self):
        done, running = 0, []
        while True:
            lines = [l.strip() for l in self.jf.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            jobs = [l for l in lines if l != "STOP"]
            running = [p for p in running if p.poll() is None]
            lim = 1 if hold_active() else self.maxpar
            if done < len(jobs) and len(running) < lim:
                fg = free_gb()
                if fg >= self.gb:
                    cmd = jobs[done]
                    done += 1
                    p = subprocess.Popen(cmd, shell=True, cwd=str(C.PROJECT))
                    running.append(p)
                    with open(self.pidf, "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%m-%d %H:%M:%S')} {p.pid} {cmd}\n")
                    print(time.strftime("%H:%M:%S"), "started", p.pid, f"free {fg:.2f} GB", cmd, flush=True)
                    time.sleep(45)
                    continue
            if done >= len(jobs) and not running and "STOP" in lines:
                print("queue empty", flush=True)
                return
            time.sleep(20)


def kill_tracked(pidfile=None):
    """Kill the process trees of the PIDs in our pid file (and nothing else)."""
    pidf = Path(pidfile) if pidfile else C.LOGS / "tk" / "pids.txt"
    for line in pidf.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        pid = next((p for p in parts if p.isdigit() and len(p) >= 3), None)
        if pid:
            subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True)


if __name__ == "__main__":
    a = sys.argv[1:]

    def opt(n, d):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return type(d)(v) if d is not None else v
        return d
    mx = opt("--max", 3)
    gb = opt("--gb", 2.5)
    pf = opt("--pids", None)
    Queue(a[0], mx, gb, pf).run()

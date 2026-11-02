"""Acts 3-4 round-3 job queue (copy of a56r3/runq.py): run shell commands one by one / up to N at once, each started only when free RAM >= 2.5 GB
and no HOLD_FARMS file exists (then at most 1 running). Records PIDs of what it starts in logs/a34r3_pids.txt.

    python work/a56r2/runq.py <maxpar> <jobfile>      (jobfile: one command per line; '#' comments)
New lines appended to the job file while it runs are picked up.
"""
import subprocess
import sys
import time
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
HOLDS = [P / "logs" / "HOLD_FARMS", P.parent / "Contra" / "logs" / "HOLD_FARMS"]


def free_gb():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-c",
                              "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out) / 1048576
    except Exception:
        return 0.0


def main():
    maxpar = int(sys.argv[1])
    jf = Path(sys.argv[2])
    done = 0
    running = []
    pidf = P / "logs" / "a34r3_pids.txt"
    while True:
        lines = [l.strip() for l in jf.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]
        running = [p for p in running if p.poll() is None]
        lim = 1 if any(h.exists() for h in HOLDS) else maxpar
        if done < len(lines) and len(running) < lim and free_gb() >= 2.5:
            cmd = lines[done]
            done += 1
            p = subprocess.Popen(cmd, shell=True, cwd=str(P))
            running.append(p)
            with open(pidf, "a") as f:
                f.write(f"{time.strftime('%H:%M:%S')} {p.pid} {cmd}\n")
            print(time.strftime('%H:%M:%S'), "started", p.pid, cmd, flush=True)
            time.sleep(30)
            continue
        if done >= len(lines) and not running:
            time.sleep(60)
            lines = [l for l in jf.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]
            if done >= len(lines) and "STOP" in jf.read_text():
                print("queue empty", flush=True)
                return
        time.sleep(20)


if __name__ == "__main__":
    main()


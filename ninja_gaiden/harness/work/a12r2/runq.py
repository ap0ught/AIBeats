"""a12r2 job queue (same rules as work/a56r2/runq.py): start a job only when free RAM >= 2.5 GB, at most <maxpar> at
once (1 if a HOLD_FARMS file exists). PIDs -> logs/a12r2_pids.txt. New lines in the job file are picked up;
a line "STOP" ends the queue once everything ran.
    python work/a12r2/runq.py <maxpar> <jobfile>"""
import subprocess, sys, time
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
HOLDS = [P / "logs" / "HOLD_FARMS", P.parent / "Contra" / "logs" / "HOLD_FARMS"]
def free_gb():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-c", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out) / 1048576
    except Exception:
        return 0.0
def main():
    maxpar = int(sys.argv[1]); jf = Path(sys.argv[2]); done = 0; running = []
    pidf = P / "logs" / "a12r2_pids.txt"
    while True:
        lines = [l.strip() for l in jf.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]
        jobs = [l for l in lines if l != "STOP"]
        running = [p for p in running if p.poll() is None]
        lim = 1 if any(h.exists() for h in HOLDS) else maxpar
        if done < len(jobs) and len(running) < lim:
            fg = free_gb()
            if fg >= 2.5:
                cmd = jobs[done]; done += 1
                p = subprocess.Popen(cmd, shell=True, cwd=str(P)); running.append(p)
                with open(pidf, "a") as f:
                    f.write(f"{time.strftime('%H:%M:%S')} {p.pid} {cmd}\n")
                print(time.strftime('%H:%M:%S'), "started", p.pid, f"free {fg:.2f} GB", cmd, flush=True)
                time.sleep(45); continue
        if done >= len(jobs) and not running and "STOP" in lines:
            print("queue empty", flush=True); return
        time.sleep(20)
if __name__ == "__main__":
    main()

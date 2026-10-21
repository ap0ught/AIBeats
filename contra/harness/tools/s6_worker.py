"""A long-lived emulator for interactive experiments (stage 6/7 builder only).

    python tools/s6_worker.py <name> <jobdir>

Keeps one emulator open and executes every <jobdir>/*.<name>.job.py that appears (oldest first) with `sim` (a
contra.stages.s6lib.Sim) in its globals; stdout/stderr of the job are streamed to <id>.<name>.out, and
<id>.<name>.done is written when the job has finished. <jobdir>/STOP or STOP_<name> makes it close the emulator
and exit; <jobdir>/CANCEL_<name> aborts the running job.
"""
import contextlib
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s6lib  # noqa: E402

name, jobdir = sys.argv[1], Path(sys.argv[2])
jobdir.mkdir(parents=True, exist_ok=True)
sim = s6lib.Sim(name)
(jobdir / f"{name}.pid").write_text(f"{sim.pid}\n", encoding="utf-8")
print("worker ready, emulator pid", sim.pid, flush=True)
raw_run = s6lib.Sim.run
calls = [0]


def run_checked(self, rows, _raw=raw_run):
    calls[0] += 1
    if calls[0] % 200 == 0 and ((jobdir / f"CANCEL_{name}").exists() or (jobdir / "STOP").exists()
                                or (jobdir / f"STOP_{name}").exists()):
        try:
            (jobdir / f"CANCEL_{name}").unlink()
        except OSError:
            pass
        raise RuntimeError("job cancelled")
    return _raw(self, rows)


s6lib.Sim.run = run_checked
try:
    while True:
        if (jobdir / "STOP").exists() or (jobdir / f"STOP_{name}").exists():
            break
        jobs = sorted(jobdir.glob(f"*.{name}.job.py"), key=lambda p: p.stat().st_mtime)
        if not jobs:
            time.sleep(0.05)
            continue
        job = jobs[0]
        src = job.read_text(encoding="utf-8")
        out = job.with_suffix("").with_suffix(".out")
        buf = open(out, "w", encoding="utf-8", buffering=1)
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                for m in list(sys.modules):
                    if m.startswith("contra.stages.") and m != "contra.stages.s6lib":
                        del sys.modules[m]
                        pkg = sys.modules.get("contra.stages")
                        if pkg is not None and hasattr(pkg, m.rsplit(".", 1)[1]):
                            delattr(pkg, m.rsplit(".", 1)[1])
                exec(compile(src, str(job), "exec"), {"sim": sim, "__name__": "__job__", "__file__": str(job)})
        except BaseException:      # noqa: BLE001
            buf.write("\n" + traceback.format_exc())
        buf.write(f"\n[job {job.name}: {time.time() - t0:.1f} s]\n")
        buf.close()
        done = job.with_suffix("").with_suffix(".done")
        job.unlink()
        done.write_text("done", encoding="utf-8")
finally:
    sim.close()
    print("worker closed", flush=True)

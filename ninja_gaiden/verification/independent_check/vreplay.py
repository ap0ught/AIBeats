"""Launch ONE EmuHawk (BizHawk 2.11.1, NesHawk) on a fresh power-on with work/verify/vreplay.lua and an input file.
Verifier's own launcher: does not import ng/, assemble.py or any project clock code.

  python vreplay.py <inputs.txt> <outname> [--tail N] [--noshots]
Output: work/verify/run/<outname>/frames.csv, meta.txt, shots/*.png
Waits for >= 2.5 GB free RAM before launching; kills only the PID it started (and only on timeout).
"""
import json, os, shutil, subprocess, sys, time, ctypes

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))
BIZ = os.path.normpath(os.path.join(PROJ, "..", "BizHawk-2.11.1-win-x64"))
ROM = os.path.join(PROJ, "Ninja Gaiden (USA).nes")


def free_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS(); m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2**30


def main():
    a = sys.argv[1:]
    inputs, name = os.path.abspath(a[0]), a[1]
    tail = int(a[a.index("--tail") + 1]) if "--tail" in a else 300
    shots = "--noshots" not in a
    out = os.path.join(HERE, "run", name)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "shots"))
    with open(os.path.join(HERE, "run", "cfg.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{inputs.replace(os.sep, '/')}\n{out.replace(os.sep, '/')}\n{tail}\n{'shots' if shots else 'noshots'}\n")
    # private config: base config with rewind off, NES core = NesHawk, opposing directions passed through as given
    cdir = os.path.join(HERE, "run", "emucfg")
    os.makedirs(cdir, exist_ok=True)
    conf = json.loads(open(os.path.join(BIZ, "config.ini"), encoding="utf-8-sig").read())
    conf.setdefault("Rewind", {})["Enabled"] = False
    conf["PreferredCores"]["NES"] = "NesHawk"
    conf["OpposingDirPolicy"] = 2
    cfg = os.path.join(cdir, "config.ini")
    open(cfg, "w", encoding="utf-8").write(json.dumps(conf, indent=1))
    while free_gb() < 2.5:
        print(f"waiting for RAM: {free_gb():.2f} GB free", flush=True)
        time.sleep(30)
    t0 = time.time()
    p = subprocess.Popen([os.path.join(BIZ, "EmuHawk.exe"), f"--config={cfg}", f"--lua={os.path.join(HERE, 'vreplay.lua')}", ROM],
                         cwd=BIZ, stdout=open(os.path.join(out, "emuhawk.log"), "w"), stderr=subprocess.STDOUT)
    print("EmuHawk pid", p.pid, flush=True)
    open(os.path.join(out, "pid.txt"), "w").write(str(p.pid))
    meta = os.path.join(out, "meta.txt")
    while True:
        if p.poll() is not None:
            break
        try:
            lg = open(os.path.join(out, "emuhawk.log"), encoding="utf-8", errors="replace").read()
        except OSError:
            lg = ""
        if "LuaScriptException" in lg or "Exception" in lg.split("loaded script")[-1]:
            time.sleep(2); p.kill(); print("LUA ERROR, killed", p.pid); print(lg[-1500:]); break
        if time.time() - t0 > 3 * 3600:
            p.kill(); print("TIMEOUT, killed", p.pid); break
        time.sleep(5)
    txt = open(meta, encoding="utf-8").read() if os.path.exists(meta) else ""
    print("exit", p.returncode, "DONE" in txt, f"{time.time() - t0:.0f} s")
    print("\n".join(l for l in txt.splitlines() if not l.startswith("ram_after")))


if __name__ == "__main__":
    main()

"""Independent verifier launcher. Starts one EmuHawk (NesHawk) on the ROM with verify1/vreplay.lua and waits.

    python vlaunch.py <job> <out dir name> <inputs path> [shots=all] [extra=600] [maxrows=0] [every=0]

Nothing from the builders' harness is imported. The emulator is started from power-on by the command line; the Lua
script feeds controller input only. Private config copy under verify1/emu_tmp (rewind off, NES core NesHawk,
frame skip 0). The child is stopped only through its own handle.
"""
import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BIZ = ROOT / "BizHawk-2.11.1-win-x64"
ROM = HERE.parent / "Contra (USA).nes"


def main():
    job, outname, inputs = sys.argv[1], sys.argv[2], sys.argv[3]
    kv = dict(a.split("=", 1) for a in sys.argv[4:])
    out = HERE / outname
    out.mkdir(parents=True, exist_ok=True)
    for p in out.glob("*"):
        if p.is_file():
            p.unlink()
    lines = [f"inputs={Path(inputs).as_posix()}", f"out={out.as_posix()}", f"shots={kv.get('shots', 'all')}",
             f"extra={kv.get('extra', '600')}", f"maxrows={kv.get('maxrows', '0')}", f"every={kv.get('every', '0')}"]
    (HERE / f"job_{job}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    priv = HERE / "emu_tmp" / uuid.uuid4().hex[:8]
    priv.mkdir(parents=True, exist_ok=True)
    conf = json.loads((BIZ / "config.ini").read_text(encoding="utf-8-sig"))
    conf["Rewind"]["Enabled"] = False
    conf["PreferredCores"]["NES"] = kv.get("core", "NesHawk")
    conf["FrameSkip"] = 0
    conf["AutoLoadLastSaveSlot"] = False
    conf["Cheats"]["LoadFileByGame"] = False
    cfg = priv / "config.ini"
    cfg.write_text(json.dumps(conf, indent=1), encoding="utf-8")
    args = [str(BIZ / "EmuHawk.exe"), f"--config={cfg}", f"--lua={HERE / 'vreplay.lua'}", f"--userdata=job:{job}",
            str(ROM)]
    log = open(out / "emuhawk_stdout.log", "w")
    t0 = time.time()
    proc = subprocess.Popen(args, cwd=str(BIZ), stdout=log, stderr=subprocess.STDOUT)
    print("pid", proc.pid, flush=True)
    (out / "pid.txt").write_text(str(proc.pid))
    limit = float(kv.get("timeout", "1500"))
    code = None
    while time.time() - t0 < limit:
        try:
            code = proc.wait(timeout=5)
            break
        except subprocess.TimeoutExpired:
            pass
    if code is None:
        print("timeout: killing our own child", proc.pid, flush=True)
        proc.kill()
        proc.wait(timeout=10)
    log.close()
    shutil.rmtree(priv, ignore_errors=True)
    rl = out / "replay.log"
    print("exit", code, "seconds", round(time.time() - t0, 1))
    print(rl.read_text() if rl.exists() else "no replay.log")


if __name__ == "__main__":
    main()

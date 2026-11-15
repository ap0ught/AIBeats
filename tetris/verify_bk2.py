"""Check a Tetris movie with BizHawk's own movie playback: no input injection, no memory writes, no savestates.

    python verify_bk2.py --bizhawk "C:/path/BizHawk-2.11.1-win-x64" --rom "C:/path/Tetris (USA).nes"  [--run tetrises]

--run any (default) checks tetris_ai_2m14s_any_piece.bk2; --run tetrises checks tetris_ai_2m16s_tetrises_only.bk2.
--rom may also be the .zip that holds the .nes (BizHawk opens it directly).

Needs Python 3.9+ on Windows (EmuHawk.exe); no extra packages. It starts one EmuHawk with a private copy of your
BizHawk config (rewind off; your own config file is not changed), plays the movie hands-off with verify_movie.lua
(under a minute), then checks:

  1. BizHawk loaded the movie, played it on the NES from power-on (no savestate), and reached the last frame.
  2. For every frame from 2 to the end (BizHawk plays frame 1 before the Lua script starts), the lag flag and the
     SHA-256 of all 2 KB of RAM are identical to the reference in
     verification/<movie>.frames.csv. That file is the harness's own replay of the input list in BizHawk (inputs
     fed through Lua, not through a movie), which in turn matched the AI's Python copy of the game on every byte of
     every frame.
  3. The time, read from RAM: the LINES counter is the BCD bytes $0050 (tens, ones) and $0051 (hundreds). The run
     ends on the first frame the counter SHOWS 100 or more (one frame after RAM first holds it: the game draws the
     new count in the next vertical blank). It starts on the frame of the Start press on the level-select screen
     (the last Start press of the input list before the end). Time = frames / 60.0988. Also checked: the level byte
     $0044 is 19, and every line clear is listed by size (the tetrises-only run must have 25 clears of 4 rows).

Exit code 0 = everything matched, 1 = something did not (the report says what).
"""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROM_SHA1_WHOLE = "3026D28B63D94C921FE58364F8B0659D10B5A0AC"
ROM_SHA1_DATA = "FD9079CB5E8479EB06D93C2AE5175BFCE871746A"
FPS = 1789772.72727 / 29780.5          # NTSC NES frame rate, 60.0988 frames per second
RUNS = {
    "any": dict(movie="tetris_ai_2m14s_any_piece.bk2", frames=8108, tetrises_only=False),
    "tetrises": dict(movie="tetris_ai_2m16s_tetrises_only.bk2", frames=8188, tetrises_only=True),
}
REC = 4 + 2048


def rom_hashes(path):
    data = Path(path).read_bytes()
    if data[:2] == b"PK":
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".nes"))
            data = z.read(name)
    return hashlib.sha1(data).hexdigest().upper(), hashlib.sha1(data[16:]).hexdigest().upper()


def movie_inputs(movie):
    with zipfile.ZipFile(movie) as z:
        log = z.read("Input Log.txt").decode("utf-8").splitlines()
    body = [l for l in log if l.startswith("|")]
    order = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
    return [{b for b, c in zip(order, l[4:12]) if c != "."} for l in body]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", choices=sorted(RUNS), default="any")
    ap.add_argument("--movie", help="another .bk2 to play (default: the --run movie in this folder)")
    ap.add_argument("--bizhawk", required=True, help="the BizHawk 2.11.1 folder (with EmuHawk.exe)")
    ap.add_argument("--rom", required=True, help="your Tetris (USA) .nes file, or the .zip that holds it")
    ap.add_argument("--keep", action="store_true", help="keep the work folder (ram.bin, logs, last.png)")
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--json", help="also write the report to this file")
    a = ap.parse_args()

    prof = RUNS[a.run]
    biz = Path(a.bizhawk).resolve()
    rom = Path(a.rom).resolve()
    movie = Path(a.movie).resolve() if a.movie else HERE / prof["movie"]
    ref_csv = HERE / "verification" / (Path(prof["movie"]).stem + ".frames.csv")
    fails = []
    rep = {"movie": movie.name, "movie_sha1": hashlib.sha1(movie.read_bytes()).hexdigest()}
    whole, body = rom_hashes(rom)
    rep["rom_whole_sha1"], rep["rom_data_sha1"] = whole, body
    if whole != ROM_SHA1_WHOLE:
        print("WARNING: ROM whole-file SHA-1 is not " + ROM_SHA1_WHOLE +
              ("; the game data matches, only the iNES header differs" if body == ROM_SHA1_DATA else
               "; the game data differs too: this is not Tetris (USA)"))

    rows = movie_inputs(movie)
    target = len(rows)
    work = Path(tempfile.mkdtemp(prefix="tetris_bk2_"))
    play(a, biz, rom, movie, work, target, fails, rep)
    analyse(work, rows, ref_csv, prof, fails, rep)
    rep["result"] = "PASS" if not fails else "FAIL"
    rep["failures"] = fails
    rep["checked_utc"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print(json.dumps(rep, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    if a.keep or fails:
        print("work folder kept:", work)
    else:
        shutil.rmtree(work, ignore_errors=True)
    sys.exit(0 if not fails else 1)


def play(a, biz, rom, movie, work, target, fails, rep):
    cfg_src = biz / "config.ini"
    conf = {}
    if cfg_src.exists():
        conf = json.loads(cfg_src.read_text(encoding="utf-8-sig"))
        if isinstance(conf.get("Rewind"), dict):
            conf["Rewind"]["Enabled"] = False
        conf["FrameSkip"] = 0
        conf["AutoLoadLastSaveSlot"] = False
        if isinstance(conf.get("Cheats"), dict):
            conf["Cheats"]["LoadFileByGame"] = False
    cfg = work / "config.ini"
    if conf:
        cfg.write_text(json.dumps(conf, indent=1), encoding="utf-8")
    args = [str(biz / "EmuHawk.exe")]
    if conf:
        args.append(f"--config={cfg}")
    args += [f"--lua={HERE / 'verify_movie.lua'}", f"--userdata=frames:{target};out:{work.as_posix()}",
             f"--movie={movie}", str(rom)]
    t0 = time.time()
    with open(work / "emuhawk_stdout.log", "w") as so:
        proc = subprocess.Popen(args, cwd=str(biz), stdout=so, stderr=subprocess.STDOUT)
        print(f"EmuHawk pid {proc.pid}: playing {movie.name} to frame {target} ...", flush=True)
        try:
            proc.wait(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            fails.append("EmuHawk did not finish in time (stopped)")
    rep["seconds"] = round(time.time() - t0, 1)


def lines_of(ram):
    return (ram[0x51] & 0x0F) * 100 + (ram[0x50] >> 4) * 10 + (ram[0x50] & 0x0F)


def analyse(work, rows, ref_csv, prof, fails, rep):
    log = (work / "movie.log").read_text(encoding="utf-8") if (work / "movie.log").exists() else ""
    kv = {}
    for line in log.splitlines():
        if "=" in line and not line.startswith("movie_header"):
            k, v = line.split("=", 1)
            kv[k] = v
    rep["bizhawk"] = {k: kv.get(k) for k in ("movie_loaded", "movie_mode", "movie_startsfromsavestate", "system",
                                             "board", "romhash", "end_framecount", "end_movie_mode")}
    if "ERROR" in log or "DONE" not in log:
        fails.append("the Lua script did not finish: " + next((l for l in log.splitlines() if "ERROR" in l), "no DONE"))
    if kv.get("movie_loaded") != "true":
        fails.append("BizHawk did not load the movie")
    if kv.get("movie_startsfromsavestate") not in (None, "false"):
        fails.append("the movie starts from a savestate")
    if kv.get("system") != "NES":
        fails.append(f"system {kv.get('system')} is not NES")

    # BizHawk runs frame 1 of the movie before the Lua script starts, so the records begin at frame 2
    data = (work / "ram.bin").read_bytes() if (work / "ram.bin").exists() else b""
    n = len(data) // REC
    first_frame = int(kv.get("start_framecount", "0")) + 1
    if n != len(rows) - first_frame + 1:
        fails.append(f"recorded frames {first_frame}..{first_frame + n - 1}, the movie has {len(rows)}")
    ram_at, lag_at = {}, {}
    for i in range(n):
        r = data[i * REC:(i + 1) * REC]
        f = r[0] | r[1] << 8 | r[2] << 16
        if f != first_frame + i:
            fails.append(f"frame numbering: record {i} is frame {f}, expected {first_frame + i}")
            break
        lag_at[f], ram_at[f] = r[3], r[4:]

    # 2. against the harness's replay
    ref = {int(r["frame"]): r for r in csv.DictReader(open(ref_csv, encoding="utf-8"))}
    first = None
    for f in sorted(ram_at):
        if f not in ref or hashlib.sha256(ram_at[f]).hexdigest() != ref[f]["ram_sha256"] or int(ref[f]["lag"]) != lag_at[f]:
            first = f
            break
    rep["frames_compared"] = f"{min(ram_at, default=0)}..{max(ram_at, default=0)} ({len(ram_at)} frames)"
    rep["ram_and_lag_identical_to_reference"] = first is None and len(ram_at) > 0 and max(ram_at) == max(ref)
    if first is not None:
        fails.append(f"RAM or lag differs from the reference first on frame {first}")
    elif not ram_at or max(ram_at) != max(ref):
        fails.append(f"the reference ends on frame {max(ref)}, the playback on {max(ram_at, default=0)}")

    # 3. the clock (frame f's RAM is the RAM after frame f)
    lines = {f: lines_of(r) for f, r in ram_at.items()}
    end_ram = next((f for f in sorted(lines) if lines[f] >= 100), None)
    if end_ram is None:
        fails.append("the LINES counter never reaches 100")
        return
    shown = end_ram + 1
    starts = [k + 1 for k in range(min(shown, len(rows))) if "Start" in rows[k] and (k == 0 or "Start" not in rows[k - 1])]
    start = starts[-1]
    frames = shown - start
    clears = {}
    prev = 0
    for f in sorted(lines):
        if f > end_ram:
            break
        if lines[f] != prev:
            clears[lines[f] - prev] = clears.get(lines[f] - prev, 0) + 1
            prev = lines[f]
    level = ram_at[end_ram][0x44]
    rep["clock"] = {"start_press_frame": start, "lines_100_in_ram_after_frame": end_ram, "lines_100_shown_frame": shown,
                    "frames": frames, "seconds": round(frames / FPS, 2), "final_lines": lines[end_ram],
                    "level": level, "clears_by_rows": {str(k): v for k, v in sorted(clears.items())},
                    "world_record_time_s": 163.54, "faster_by_s": round(163.54 - frames / FPS, 2)}
    if frames != prof["frames"]:
        fails.append(f"time is {frames} frames, expected {prof['frames']}")
    if level != 19:
        fails.append(f"level is {level}, expected 19")
    if prof["tetrises_only"] and set(clears) != {4}:
        fails.append(f"not tetrises only: clears by rows {clears}")


if __name__ == "__main__":
    main()

"""Check the Super Mario Bros. 3 movie with BizHawk's own movie playback: no input injection, no memory writes, no
savestates.

    python verify_bk2.py --bizhawk "C:/path/BizHawk-2.11.1-win-x64" --rom "C:/path/Super Mario Bros. 3 (USA).nes" [smb3_ai_10m39s.bk2]

Needs Python 3.9+ and Pillow (pip install pillow). Windows (EmuHawk.exe). It starts one EmuHawk with a private copy
of your BizHawk config (rewind off; your own config file is not changed), plays the movie hands-off with
verify_movie.lua for 38,623 frames (a few minutes on NesHawk), then checks:

  1. BizHawk loaded the movie, played it on the NesHawk core, from power-on (no savestate), with the expected ROM.
  2. The per-frame RAM + lag flag of frames 2..38,623 has the SHA-1 below: the same digest as the frame-by-frame
     replay of the input file through BizHawk's Lua bridge that the video was captured from (and whose RAM
     milestones equal the Mesen replay's, all 197 of them). The RAM after frame 38,503 (the file's last line) has
     SHA-1 0312f20a5091f5669d88b67489b1fb844c04a156.
  3. The clock in RAM: the Start press that starts the timer is seen in the game's pad byte ($17 = $10) on frame 68;
     Level_ExitToMap ($14) becomes non-zero on frame 38,502 in Bowser's castle (World 8, tileset 2): 38,434 frames
     = 10:39.514 at 60.0988 frames a second (the leaderboard ends the time 5 frames before the fade).
  4. The pictures: frame 38,507 is darker than frame 38,506 (the fade starts 5 frames after the end event).

Exit code 0 = everything matched, 1 = something did not (the report says what).
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = 38623                                              # the movie's last frame (38,503 file lines + 120 idle)
WANT_TRACE = "0bac2e729dbca3718d221b3711c21622b3e434c6"     # sha1 over frames 2..38623 of (lag flag byte + 2048 RAM)
WANT_RAM_38503 = "0312f20a5091f5669d88b67489b1fb844c04a156"
WANT = {"start": 68, "end": 38502}
ROM_WHOLE_SHA1 = "5f9019040fe23cb412a484e1ef430e59e589f9b4"
ROM_HEADERLESS_SHA1 = "a611b90b4833b20a364bf06ee3be3b9093ea4df9"
SHOTS = (38506, 38507)
NES_FPS = 60.0988


def mean_brightness(png):
    from PIL import Image
    g = Image.open(png).convert("L")
    h = g.histogram()
    return sum(i * c for i, c in enumerate(h)) / max(1, sum(h))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("movie", nargs="?", default=str(HERE / "smb3_ai_10m39s.bk2"))
    ap.add_argument("--bizhawk", required=True, help="the BizHawk 2.11.1 folder (with EmuHawk.exe)")
    ap.add_argument("--rom", required=True, help="your Super Mario Bros. 3 (USA) .nes file (PRG0)")
    ap.add_argument("--keep", action="store_true", help="keep the work folder (pictures, ram.bin, logs)")
    ap.add_argument("--timeout", type=float, default=2400)
    ap.add_argument("--json", help="also write the report to this file")
    a = ap.parse_args()

    biz = Path(a.bizhawk).resolve()
    rom = Path(a.rom).resolve()
    movie = Path(a.movie).resolve()
    lua = HERE / "verify_movie.lua"
    fails = []
    rep = {"movie": movie.name, "movie_sha1": hashlib.sha1(movie.read_bytes()).hexdigest()}

    data = rom.read_bytes()
    rep["rom_whole_sha1"] = hashlib.sha1(data).hexdigest()
    rep["rom_headerless_sha1"] = hashlib.sha1(data[16:]).hexdigest() if data[:4] == b"NES\x1a" else None
    if rep["rom_whole_sha1"] != ROM_WHOLE_SHA1:
        msg = "ROM is not the expected Super Mario Bros. 3 (USA) PRG0 file (whole-file SHA-1 " + ROM_WHOLE_SHA1 + ")"
        if rep["rom_headerless_sha1"] == ROM_HEADERLESS_SHA1:
            msg += "; the game data matches (headerless SHA-1), only the 16-byte iNES header differs"
        print("WARNING:", msg)

    work = Path(tempfile.mkdtemp(prefix="smb3_bk2_"))
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
    ud = f"frames:{TARGET};out:{work.as_posix()};shots:{'_'.join(map(str, SHOTS))}"
    args = [str(biz / "EmuHawk.exe"), f"--config={cfg}", f"--lua={lua}", f"--userdata={ud}", f"--movie={movie}", str(rom)]
    t0 = time.time()
    with open(work / "emuhawk_stdout.log", "w") as so:
        proc = subprocess.Popen(args, cwd=str(biz), stdout=so, stderr=subprocess.STDOUT)
        print(f"EmuHawk pid {proc.pid}: playing {movie.name} to frame {TARGET} ...", flush=True)
        try:
            proc.wait(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            fails.append("EmuHawk did not finish in time (stopped)")
    rep["seconds"] = round(time.time() - t0, 1)

    log = (work / "movie.log").read_text(encoding="utf-8") if (work / "movie.log").exists() else ""
    kv = {}
    for line in log.splitlines():
        k, _, v = line.partition("=")
        kv.setdefault(k, v)
    rep["bizhawk"] = {k: kv.get(k) for k in ("start_framecount", "movie_loaded", "movie_mode", "movie_length",
                                             "movie_startsfromsavestate", "movie_header Core", "movie_header SHA1",
                                             "romhash", "board", "end_framecount", "end_movie_mode")}
    rep["movie_modes"] = [l for l in log.splitlines() if l.startswith("movie_mode_at_frame")]
    if "DONE" not in log:
        fails.append("the Lua script did not finish: " + (log.splitlines()[-1] if log else "no log"))
    if kv.get("movie_loaded") != "true" or kv.get("movie_mode") != "PLAY":
        fails.append(f"movie not playing (loaded={kv.get('movie_loaded')}, mode={kv.get('movie_mode')})")
    if kv.get("movie_startsfromsavestate") not in (None, "false"):
        fails.append("movie starts from a savestate")
    doms = kv.get("domains", "")
    rep["core_seen"] = "NesHawk" if "PPU Bus" in doms.split("|") else "not NesHawk"   # quickerNES has no PPU Bus
    if rep["core_seen"] != "NesHawk":
        fails.append("core is not NesHawk (memory domains: " + doms + ")")
    if (kv.get("romhash") or "").lower() != ROM_WHOLE_SHA1:
        fails.append(f"BizHawk's ROM hash {kv.get('romhash')} is not {ROM_WHOLE_SHA1.upper()}")

    rb = work / "ram.bin"
    R = 4 + 2048
    frames = {}
    if rb.exists():
        d = rb.read_bytes()
        for i in range(len(d) // R):
            r = d[i * R:(i + 1) * R]
            frames[r[0] | r[1] << 8 | r[2] << 16] = (r[3], r[4:])
    if not frames or max(frames) < TARGET:
        fails.append(f"RAM trace stops at frame {max(frames) if frames else None}")
    else:
        missing = [f for f in range(2, TARGET + 1) if f not in frames]
        if missing:
            fails.append(f"{len(missing)} frames missing from the trace, first {missing[0]}")
        else:
            h = hashlib.sha1()
            for f in range(2, TARGET + 1):
                h.update(bytes([frames[f][0]]) + frames[f][1])
            rep["trace_sha1_2_to_38623"] = h.hexdigest()
            rep["ram_sha1_at_38503"] = hashlib.sha1(frames[38503][1]).hexdigest()
            rep["lag_frames_2_to_38623"] = sum(frames[f][0] for f in range(2, TARGET + 1))
            if rep["trace_sha1_2_to_38623"] != WANT_TRACE:
                fails.append(f"per-frame trace sha1 {rep['trace_sha1_2_to_38623']}, expected {WANT_TRACE}")
            if rep["ram_sha1_at_38503"] != WANT_RAM_38503:
                fails.append(f"RAM sha1 at 38503 is {rep['ram_sha1_at_38503']}, expected {WANT_RAM_38503}")
            ram = lambda f, a_: frames[f][1][a_]
            fs = range(3, TARGET + 1)                      # (frame - 1) must be in the trace too
            start = [f for f in fs if f <= 400 and ram(f, 0x17) & 0x10 and not ram(f - 1, 0x17) & 0x10]
            ends = [f for f in fs if ram(f, 0x14) and not ram(f - 1, 0x14)]
            end = ends[-1] if ends else None
            rep["clock_ram"] = {"start_presses_seen": start, "end_Level_ExitToMap": end,
                                "end_tileset": ram(end, 0x70A) if end else None, "end_world": (ram(end, 0x727) + 1) if end else None}
            s0 = start[-1] if start else None
            if s0 != WANT["start"]:
                fails.append(f"timer start {s0}, expected {WANT['start']}")
            if end != WANT["end"] or (end and (ram(end, 0x70A) != 2 or ram(end, 0x727) != 7)):
                fails.append(f"end event {end} (tileset/world {rep['clock_ram']['end_tileset']}/{rep['clock_ram']['end_world']}), expected {WANT['end']} in the castle (2/8)")
            if s0 and end:
                n = end - s0
                s = n / NES_FPS
                rep["clock"] = {"frames": n, "seconds": round(s, 3), "time": f"{int(s // 60)}:{s % 60:06.3f}"}

    pics = {}
    for f in SHOTS:
        p = work / f"f{f:05d}.png"
        if not p.exists():
            fails.append(f"no screenshot of frame {f}")
            continue
        pics[f] = {"mean_brightness": round(mean_brightness(p), 2)}
    rep["pictures"] = pics
    if len(pics) == 2 and not pics[38507]["mean_brightness"] < 0.97 * pics[38506]["mean_brightness"]:
        fails.append(f"frame 38507 is not darker than 38506: {pics}")

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


if __name__ == "__main__":
    main()

"""Check the Ninja Gaiden movie with BizHawk's own movie playback: no input injection, no memory writes, no savestates.

    python verify_bk2.py --bizhawk "C:/path/BizHawk-2.11.1-win-x64" --rom "C:/path/Ninja Gaiden (USA).nes"
                         [ninja_gaiden_ai_11m25s.bk2]

Needs Python 3.9+ and Pillow (pip install pillow). Windows (EmuHawk.exe). It starts one EmuHawk with a private copy
of your BizHawk config (rewind off; your own config file is not changed), plays the movie hands-off with
verify_movie.lua for 41,390 frames (about 4 minutes on NesHawk), then checks:

  1. BizHawk loaded the movie, played it on the NesHawk core, from power-on (no savestate), the ROM it expected.
  2. The RAM after frame 41,390 (the frame of the last input row) has SHA-1 d5d58c8792b76f44d9e6892ce940ab367a19b3dd
     (the builders' two replays and the independent checker's replay, all fed through Lua, not through a movie).
     For every frame 2..41,390, the lag flag, the 20 RAM bytes the independent checker logged and the three HUD
     TIMER tiles in the nametable are identical to the checker's log (digest below).
  3. The clock events: control of Ryu gained in RAM on frame 174 ($33 = $97 in 1-1); 6-5 timer $63 = 0 on 41,382;
     the nametable shows TIMER 000 on 41,385. No life lost.
  4. The pictures: Ryu appears in the picture of frame 175 (not 174); the picture of 41,385 shows TIMER 000 (not
     41,384). All four pictures are pixel-identical to the reference pictures in verification/pictures/.
     Clock: 41,385 - 175 = 41,210 frames = 11:25.704 at 60.0988 frames a second.

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
TARGET = 41390                                              # frame of the last input row (row k = frame k)
WANT_RAM = "d5d58c8792b76f44d9e6892ce940ab367a19b3dd"
# sha1 over frames 2..41390 of (lag flag, the 20 RAM bytes below, 3 timer tiles): the independent checker's replay
# log (verification/independent_check/final/frames.csv) gives the same digest
WANT_SUBSET = "3d6654fd0fa9e790bff3a9b18131d272914825bd"
SUBSET = (0x33, 0x6D, 0x6E, 0x63, 0x62, 0x66, 0x3E, 0x1FD, 0x65, 0x64, 0xC9, 0x76, 0xBF, 0x2A, 0x29, 0x86, 0x85,
          0x8A, 0x4C, 0x1E)
WANT = {"control": 174, "timer0_ram": 41382, "timer000_nametable": 41385}
ROM_WHOLE_SHA1 = "ca513f841d75efeb33bb8099fb02beeb39f6bb9c"
ROM_HEADERLESS_SHA1 = "15f245161179ab1959b7dc20e82add024d23aa3d"
SHOTS = (174, 175, 41384, 41385)
START_SEEN, END_SEEN = 175, 41385
NES_FPS = 60.0988


def load_rgb(png):
    from PIL import Image
    return Image.open(png).convert("RGB")


def same_picture(a, b):
    ia, ib = load_rgb(a), load_rgb(b)
    return ia.size == ib.size and ia.tobytes() == ib.tobytes()


def playfield_change(a, b):
    """Mean absolute RGB difference over the lower 3/4 of the picture (the playfield, below the HUD)."""
    ia, ib = load_rgb(a), load_rgb(b)
    w, h = ia.size
    pa, pb = ia.crop((0, h // 4, w, h)).tobytes(), ib.crop((0, h // 4, w, h)).tobytes()
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def timer_cells(png):
    """The three TIMER digit cells as drawn (8x8 each at x 72, 80, 88; lines 24-31 of a 224-line picture)."""
    im = load_rgb(png)
    y0 = 32 if im.size[1] >= 240 else 24
    cells = [im.crop((x, y0, x + 8, y0 + 8)) for x in (72, 80, 88)]
    lit = [sum(cell.convert("L").tobytes()) / 64 for cell in cells]
    return [c.tobytes() for c in cells], lit


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("movie", nargs="?", default=str(HERE / "ninja_gaiden_ai_11m25s.bk2"))
    ap.add_argument("--bizhawk", required=True, help="the BizHawk 2.11.1 folder (with EmuHawk.exe)")
    ap.add_argument("--rom", required=True, help="your Ninja Gaiden (USA) .nes file")
    ap.add_argument("--keep", action="store_true", help="keep the work folder (pictures, ram.bin, logs)")
    ap.add_argument("--save-movie", help="also let BizHawk re-save the loaded movie to this path")
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--json", help="also write the report to this file")
    a = ap.parse_args()

    biz = Path(a.bizhawk).resolve()
    rom = Path(a.rom).resolve()
    movie = Path(a.movie).resolve()
    lua = HERE / "verify_movie.lua"
    ref = HERE / "verification" / "pictures"
    fails = []
    rep = {"movie": movie.name, "movie_sha1": hashlib.sha1(movie.read_bytes()).hexdigest()}

    data = rom.read_bytes()
    rep["rom_whole_sha1"] = hashlib.sha1(data).hexdigest()
    rep["rom_headerless_sha1"] = hashlib.sha1(data[16:]).hexdigest() if data[:4] == b"NES\x1a" else None
    if rep["rom_whole_sha1"] != ROM_WHOLE_SHA1:
        msg = "ROM is not the expected Ninja Gaiden (USA) file (whole-file SHA-1 " + ROM_WHOLE_SHA1 + ")"
        if rep["rom_headerless_sha1"] == ROM_HEADERLESS_SHA1:
            msg += "; the game data matches (headerless SHA-1), only the 16-byte iNES header differs"
        print("WARNING:", msg)

    work = Path(tempfile.mkdtemp(prefix="ng_bk2_"))
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
    if a.save_movie:
        ud += f";save:{Path(a.save_movie).resolve().with_suffix('').as_posix()}"   # BizHawk appends .bk2
    args = [str(biz / "EmuHawk.exe")]
    if conf:
        args.append(f"--config={cfg}")
    args += [f"--lua={lua}", f"--userdata={ud}", f"--movie={movie}", str(rom)]
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
                                             "romhash", "board", "end_framecount", "end_lagcount", "end_movie_mode")}
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

    # per-frame trace: 3-byte frame, lag, 3 timer tiles, 2048 RAM
    rb = work / "ram.bin"
    R = 4 + 3 + 2048
    frames = {}
    if rb.exists():
        d = rb.read_bytes()
        for i in range(len(d) // R):
            r = d[i * R:(i + 1) * R]
            frames[r[0] | r[1] << 8 | r[2] << 16] = (r[3], r[4:7], r[7:])
    if not frames or max(frames) < TARGET:
        fails.append(f"RAM trace stops at frame {max(frames) if frames else None}")
    else:
        missing = [f for f in range(2, TARGET + 1) if f not in frames]
        if missing:
            fails.append(f"{len(missing)} frames missing from the trace, first {missing[0]}")
        else:
            full, sub = hashlib.sha1(), hashlib.sha1()
            for f in range(2, TARGET + 1):
                lag, tiles, ram = frames[f]
                full.update(bytes([lag]) + ram)
                sub.update(bytes([lag] + [ram[x] for x in SUBSET]) + tiles)
            rep["trace_sha1_2_to_41390_lag_and_ram"] = full.hexdigest()
            rep["subset_sha1_2_to_41390"] = sub.hexdigest()
            rep["ram_sha1_at_41390"] = hashlib.sha1(frames[TARGET][2]).hexdigest()
            rep["lag_frames_2_to_41390"] = sum(frames[f][0] for f in range(2, TARGET + 1))
            if rep["ram_sha1_at_41390"] != WANT_RAM:
                fails.append(f"RAM sha1 at {TARGET} is {rep['ram_sha1_at_41390']}, expected {WANT_RAM}")
            if rep["subset_sha1_2_to_41390"] != WANT_SUBSET:
                fails.append(f"per-frame subset sha1 {rep['subset_sha1_2_to_41390']}, expected {WANT_SUBSET}")
            fs = range(2, TARGET + 1)
            ram = lambda f, a_: frames[f][2][a_]
            control = next((f for f in fs if ram(f, 0x33) == 0x97 and ram(f, 0x6D) == 0), None)
            t0r = next((f for f in fs if ram(f, 0x6D) == 21 and ram(f, 0x63) == 0 and ram(f, 0x66) == 0), None)
            nt0 = next((f for f in fs if ram(f, 0x6D) == 21 and ram(f, 0x63) == 0 and frames[f][1] == b"\0\0\0"),
                       None)
            drops = [f for f in fs if f > 400 and ram(f, 0x76) < ram(f - 1, 0x76)]
            stages, cur = [], None
            for f in fs:
                s = ram(f, 0x6D)
                if s <= 21 and s != cur and (cur is None or s == cur + 1):
                    cur = s
                    stages.append(f)
            rep["events_ram"] = {"control": control, "timer0_ram": t0r, "timer000_nametable": nt0,
                                 "lives_lost_at": drops, "stage_loads": len(stages)}
            for k, v in (("control", control), ("timer0_ram", t0r), ("timer000_nametable", nt0)):
                if v != WANT[k]:
                    fails.append(f"{k} = {v}, expected {WANT[k]}")
            if drops:
                fails.append(f"a life is lost on frames {drops}")
            if len(stages) != 22:
                fails.append(f"{len(stages)} stages seen in order, expected 22 (1-1 .. 6-5)")

    # pictures
    pics = {}
    for f in SHOTS:
        p = work / f"f{f:05d}.png"
        if not p.exists():
            fails.append(f"no screenshot of frame {f}")
            continue
        cells, lit = timer_cells(p)
        pics[f] = {"timer_cells_lit": [round(x) for x in lit],
                   "timer_reads_000": cells[0] == cells[1] == cells[2] and min(lit) > 10}
        rp = ref / f"f{f:05d}.png"
        if rp.exists():
            pics[f]["identical_to_reference"] = same_picture(p, rp)
            if not pics[f]["identical_to_reference"]:
                fails.append(f"frame {f} picture differs from {rp.name}")
    if all((work / f"f{f:05d}.png").exists() for f in SHOTS):
        ch = playfield_change(work / "f00175.png", work / "f00174.png")
        pics["playfield_change_174_to_175"] = round(ch, 2)
        if ch <= 0.5:
            fails.append(f"no visible change from 174 to 175 (Ryu should appear), mean diff {ch:.2f}")
        if pics[41384]["timer_reads_000"] or not pics[41385]["timer_reads_000"]:
            fails.append("TIMER 000 is not first shown on frame 41385")
    rep["pictures"] = pics
    if not fails:
        n = END_SEEN - START_SEEN
        s = n / NES_FPS
        rep["clock"] = {"start_seen": START_SEEN, "end_seen": END_SEEN, "frames": n, "seconds": round(s, 3),
                        "time": f"{int(s // 60)}:{s % 60:06.3f}"}

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

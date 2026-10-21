"""Check the Contra movie with BizHawk's own movie playback: no input injection, no memory writes, no savestates.

    python verify_bk2.py --bizhawk "C:/path/BizHawk-2.11.1-win-x64" --rom "C:/path/Contra (USA).nes" [contra_ai_9m24s.bk2]

Needs Python 3.9+ and Pillow (pip install pillow). Windows (EmuHawk.exe). It starts one EmuHawk with a private copy
of your BizHawk config (rewind off; your own config file is not changed), plays the movie hands-off with
verify_movie.lua for 34,568 frames (about 3 minutes on NesHawk), then checks:

  1. BizHawk loaded the movie, played it on the NesHawk core, from power-on (no savestate), the ROM it expected.
  2. The RAM after frame 34,568 (the frame of the last input row) has SHA-1 2242cdd88af3f06e8ed6a43de637fc42cb50d619,
     and the per-frame RAM + lag flag of frames 2..34,568 has the SHA-1 below (the same digest as two independent
     power-on replays made by feeding the input list through Lua, not through a movie).
  3. The clock events in RAM: medals written on frame 593 (seen 594), control lost on 34,507, Bill standing in RAM
     on 34,508 (seen 34,509): 33,915 frames = 9:24.321 at 60.0988 frames a second.
  4. The pictures: no medal-blue pixel in the HUD box on frames 590-593, the medals on 594; frame 34,508 still prone,
     34,509 standing, pixel-identical to the reference pictures in verification/pictures/.

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
TARGET = 34568                                              # frame of the last input row (row 34,566 -> frame 34,568)
WANT_RAM = "2242cdd88af3f06e8ed6a43de637fc42cb50d619"
WANT_TRACE = "9573e94d483c393b76f758818fe1bb9f242d1a61"     # sha1 over frames 2..34568 of (lag flag byte + 2048 RAM)
WANT = {"N": 593, "A": 34507, "P": 34508}
ROM_WHOLE_SHA1 = "c9ea66bb7cb30ad5343f1721b1d4d3219859319b"
ROM_HEADERLESS_SHA1 = "979494e7869ac7ab4815fdbd1dc99f893f713fbf"
MEDAL_BLUE = (66, 64, 254)                                   # the life medal's ribbon colour in BizHawk's NES palette
SHOTS = (590, 591, 592, 593, 594, 34508, 34509)
NES_FPS = 60.0988


def hud_medal_pixels(png):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    top = 0 if im.size[1] >= 240 else 8                      # BizHawk shows 224 lines by default (8 cut at the top)
    box = im.crop((16, 17 - top, 68, 33 - top))
    return sum(1 for y in range(box.size[1]) for x in range(box.size[0]) if box.getpixel((x, y)) == MEDAL_BLUE)


def same_picture(a, b):
    from PIL import Image
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    return ia.size == ib.size and ia.tobytes() == ib.tobytes()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("movie", nargs="?", default=str(HERE / "contra_ai_9m24s.bk2"))
    ap.add_argument("--bizhawk", required=True, help="the BizHawk 2.11.1 folder (with EmuHawk.exe)")
    ap.add_argument("--rom", required=True, help="your Contra (USA) .nes file")
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
        msg = ("ROM is not the expected Contra (USA) file (whole-file SHA-1 " + ROM_WHOLE_SHA1 + ")")
        if rep["rom_headerless_sha1"] == ROM_HEADERLESS_SHA1:
            msg += "; the game data matches (headerless SHA-1), only the 16-byte iNES header differs"
        print("WARNING:", msg)

    work = Path(tempfile.mkdtemp(prefix="contra_bk2_"))
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

    # per-frame RAM
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
            rep["trace_sha1_2_to_34568"] = h.hexdigest()
            rep["ram_sha1_at_34568"] = hashlib.sha1(frames[TARGET][1]).hexdigest()
            rep["lag_frames_2_to_34568"] = sum(frames[f][0] for f in range(2, TARGET + 1))
            if rep["ram_sha1_at_34568"] != WANT_RAM:
                fails.append(f"RAM sha1 at {TARGET} is {rep['ram_sha1_at_34568']}, expected {WANT_RAM}")
            if rep["trace_sha1_2_to_34568"] != WANT_TRACE:
                fails.append(f"per-frame trace sha1 {rep['trace_sha1_2_to_34568']}, expected {WANT_TRACE}")
            fs = sorted(f for f in frames if f >= 2)
            ram = lambda f, a_: frames[f][1][a_]
            N = next((f for f in fs if ram(f, 0x18) == 5 and ram(f, 0x1C) == 0 and ram(f, 0x30) == 0
                      and ram(f, 0x2C) == 4), None)
            A = next((f for f in fs if ram(f, 0x18) == 5 and ram(f, 0x1C) == 0 and ram(f, 0x30) == 7
                      and ram(f, 0x2C) == 9), None)
            P = next((f for f in fs if A and f > A and ram(f, 0xBC) == 0 and (ram(f, 0xA0) & 0x0F) == 0
                      and ram(f, 0xC2) in (2, 7)), None)
            rep["clock_ram"] = {"N_medals_written": N, "A_control_lost": A, "P_bill_standing": P,
                                "pad_at_A": ram(A, 0xF1) if A else None}
            for k, v in (("N", N), ("A", A), ("P", P)):
                if v != WANT[k]:
                    fails.append(f"{k} = {v}, expected {WANT[k]}")
            if N and P:
                rep["clock"] = {"start_seen": N + 1, "end_seen": P + 1, "frames": P - N,
                                "seconds": round((P - N) / NES_FPS, 3)}
                s = (P - N) / NES_FPS
                rep["clock"]["time"] = f"{int(s // 60)}:{s % 60:06.3f}"

    # pictures
    pics = {}
    for f in SHOTS:
        p = work / f"f{f:05d}.png"
        if not p.exists():
            fails.append(f"no screenshot of frame {f}")
            continue
        pics[f] = {"medal_blue_pixels_in_hud_box": hud_medal_pixels(p)}
        rp = ref / f"f{f:05d}.png"
        if rp.exists():
            pics[f]["identical_to_reference"] = same_picture(p, rp)
            if not pics[f]["identical_to_reference"]:
                fails.append(f"frame {f} picture differs from {rp.name}")
    rep["pictures"] = pics
    if pics:
        pre = [pics[f]["medal_blue_pixels_in_hud_box"] for f in (590, 591, 592, 593) if f in pics]
        if any(pre) or not pics.get(594, {}).get("medal_blue_pixels_in_hud_box"):
            fails.append(f"medal pixels: {pre} on 590-593, {pics.get(594)} on 594")
        if 34508 in pics and 34509 in pics and same_picture(work / "f34508.png", work / "f34509.png"):
            fails.append("frames 34508 and 34509 look the same (no pose change)")

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

"""u17v_replay.py - the up17 verifier's OWN replay loop (does not import assemble.py or any builder / u16v script).

    python u17v_replay.py <inputs.txt> <tag> [plan.json]

Feeds the input list to a fresh EmuHawk from power-on, one bridge `step` per frame, controller 1 only, and saves
the whole 2 KB console RAM after every frame to logs/fix/u17v_<tag>.ram (2,048 bytes per frame, frame 1 first).
No savestate is loaded and no memory is written unless the plan asks for a no-input branch (msave / mload), and
a run with branches is never used for the route's numbers.

plan.json (all optional):
  "shots":    {"<frame>": "<name>", ...}   screenshot after that frame was stepped -> logs/fix/u17v_shots/<tag>_<name>.png
  "post":     N                            after the last input: N more frames with no input, a picture after each
  "stop_at":  F                            stop feeding the list after frame F (then "post" no-input frames); no final hash claim
  "branches": [{"frame": F, "n": N, "every": K, "name": "x"}]   msave after frame F, N no-input frames with a picture
                                           every K, then mload and go on with the list
"""
import hashlib
import json
import sys
import time
from pathlib import Path

from toads.emulator import BizHawk, ROM

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
SHOTS = FIX / "u17v_shots"
LEGAL = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


def read_inputs(path):
    raw = Path(path).read_bytes()
    text = raw.decode("ascii")                       # anything non-ASCII is an error
    lines = text.split("\n")
    assert lines[0].startswith("# frames="), lines[0]
    declared = int(lines[0].split("frames=")[1].split()[0])
    body = lines[1:]
    if body and body[-1] == "":
        body = body[:-1]
    frames = []
    for n, ln in enumerate(body, 1):
        ln = ln.rstrip("\r")
        toks = tuple(t for t in ln.split(",") if t) if ln else ()
        for t in toks:
            if t not in LEGAL:
                raise SystemExit(f"frame {n}: illegal token {t!r}")
        if "Left" in toks and "Right" in toks:
            raise SystemExit(f"frame {n}: Left+Right")
        if "Up" in toks and "Down" in toks:
            raise SystemExit(f"frame {n}: Up+Down")
        if len(set(toks)) != len(toks):
            raise SystemExit(f"frame {n}: repeated token")
        frames.append(toks)
    assert declared == len(frames), (declared, len(frames))
    return frames, hashlib.sha1(raw).hexdigest()


def main():
    inp, tag = sys.argv[1], sys.argv[2]
    plan = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else {}
    shots = {int(k): v for k, v in plan.get("shots", {}).items()}
    post = int(plan.get("post", 0))
    stop_at = plan.get("stop_at")
    branches = {int(b["frame"]): b for b in plan.get("branches", [])}
    SHOTS.mkdir(parents=True, exist_ok=True)
    frames, in_sha = read_inputs(inp)
    rom_sha = hashlib.sha1(Path(ROM).read_bytes()).hexdigest()
    print(f"{tag}: inputs {inp} sha1 {in_sha} frames {len(frames)}; ROM sha1 {rom_sha}", flush=True)
    t0 = time.time()
    e = BizHawk(log_name=f"fix/u17v_{tag}_emu.log", fields={"level": 16})
    first = e.state()
    print(f"{tag}: emulator pid {e.proc.pid}, frame counter at start {first.frame}", flush=True)
    base = first.frame        # EmuHawk has emulated this many frames (1, no input) before the bridge takes over;
    assert base in (0, 1), first   # "frame N" everywhere in my files = the Nth line of the input list
    ram_path = FIX / f"u17v_{tag}.ram"
    cap = hashlib.sha1()
    lags = []
    last = None
    n_feed = len(frames) if stop_at is None else int(stop_at)
    with open(ram_path, "wb") as f:
        for i in range(1, n_feed + 1):
            s = e.step(frames[i - 1], 1)
            if s.frame != base + i:
                raise SystemExit(f"{tag}: frame counter {s.frame} after input {i}")
            last = e.ram_all()
            assert len(last) == 2048
            f.write(last)
            cap.update(last)
            lags.append(s.lag)
            if i in shots:
                e.cmd(f"screenshot {SHOTS / (tag + '_' + shots[i] + '.png')}")
            if i in branches:
                b = branches[i]
                sid = e.msave()
                for k in range(1, int(b["n"]) + 1):
                    e.step((), 1)
                    if k % int(b.get("every", 1)) == 0:
                        e.cmd(f"screenshot {SHOTS / (tag + '_' + b['name'] + '_p%03d.png' % k)}")
                e.mload(sid)
                e.mfree(sid)
            if i % 5000 == 0:
                print(f"{tag}: frame {i} ({time.time() - t0:.0f}s)", flush=True)
    final = hashlib.sha1(last).hexdigest()
    res = {"tag": tag, "emu_frames_before_first_input": base, "inputs": str(inp), "input_sha1": in_sha, "rom_sha1": rom_sha, "frames_fed": n_feed,
           "frames_in_list": len(frames), "final_ram_sha1": final, "capture_sha1": cap.hexdigest(),
           "capture": str(ram_path), "branches": len(branches), "stop_at": stop_at, "seconds": None}
    print(f"{tag}: fed {n_feed} frames; FINAL RAM sha1 {final}; capture sha1 {cap.hexdigest()}", flush=True)
    if post:
        with open(FIX / f"u17v_{tag}_post.ram", "wb") as f:
            for k in range(1, post + 1):
                e.step((), 1)
                f.write(e.ram_all())
                e.cmd(f"screenshot {SHOTS / (tag + '_post_p%03d.png' % k)}")
        print(f"{tag}: {post} no-input frames after the list, pictures {tag}_post_pNNN.png", flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    res["lag_total"] = lags[-1] if lags else None
    (FIX / f"u17v_{tag}.json").write_text(json.dumps(res, indent=1))
    (FIX / f"u17v_{tag}_lag.json").write_text(json.dumps(lags))
    e.close()
    print(f"{tag}: done in {res['seconds']}s", flush=True)


if __name__ == "__main__":
    main()

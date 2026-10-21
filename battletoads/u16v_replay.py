"""Independent replay of a route's input list from power-on (verifier's own loop; no assemble.py, no builder code).

    python u16v_replay.py <inputs file> <tag> [shots]

- reads the input list itself (one line per frame, buttons separated by ',' or '+'),
- one fresh EmuHawk (toads.emulator.BizHawk, default core), one bridge `step` per frame, controller 1 only,
- after every frame the whole 2 KB of console RAM is appended to logs/fix/u16v_<tag>.ram (frame k = bytes [2048(k-1), 2048k)),
- SHA-1 of the RAM after the LAST input line (what assemble.py hashes) -> logs/fix/u16v_<tag>.json,
- with `shots`: screenshots into logs/fix/u16v_shots/<tag>_*.png (landing window, after every level-byte change, around the
  last hit, both 13->254 cuts), idle frames stepped AFTER the input list ends (the hash is taken before them), and a
  no-input branch from an in-memory state taken on the first cut (shows what the first cut leads to when nothing is pressed).
No memory writes anywhere (the bridge's `poke` is never called).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

from toads.emulator import BizHawk, BUTTONS

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
SHOTS = FIX / "u16v_shots"

FIELDS = {"level": 0x10, "lives": 0x11, "anim": 0x3B5, "hp": 0x51A, "id3": 0x3C4, "qctr": 0x586}


def read_inputs(path):
    raw = Path(path).read_text(encoding="utf-8").split("\n")
    assert raw[0].startswith("#"), raw[0]
    if raw[-1] == "":
        raw = raw[:-1]
    lines = raw[1:]
    out = []
    for n, ln in enumerate(lines, 1):
        toks = tuple(t for t in ln.replace("+", ",").split(",") if t)
        for t in toks:
            if t not in BUTTONS:
                raise SystemExit(f"line {n}: unknown token {t!r}")
        out.append(toks)
    return raw[0], out


def main():
    path, tag = sys.argv[1], sys.argv[2]
    shots = len(sys.argv) > 3 and sys.argv[3] == "shots"
    header, ins = read_inputs(path)
    FIX.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    log = open(FIX / f"u16v_{tag}.stdout.txt", "w", encoding="utf-8")

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"inputs {path}: header {header!r}, {len(ins)} frames, file sha1 {hashlib.sha1(Path(path).read_bytes()).hexdigest()}")
    e = BizHawk(log_name=f"u16v_{tag}_emu.log", fields=FIELDS)
    say("emulator pid", e.proc.pid, "state at power-on:", e.state())
    ramf = open(FIX / f"u16v_{tag}.ram", "wb")

    def shot(name):
        p = SHOTS / f"{tag}_{name}.png"
        e.cmd(f"screenshot {p}")
        return p

    todo = {}                                            # frame -> [label]

    def plan(frame, label):
        todo.setdefault(frame, []).append(label)

    if shots:
        for f in range(2060, 2086):
            plan(f, f"land_f{f:05d}")
    prev = None
    events = []
    cuts = []
    landing = None
    lasthit = None
    cut1_state = None
    t0 = time.time()
    n = len(ins)
    extra = 60 if shots else 0
    final_sha = None
    final_state = None
    for i in range(n + extra):
        f = i + 1
        btn = ins[i] if i < n else ()
        s = e.step(btn, 1)
        ram = e.ram_all()
        assert len(ram) == 0x800
        if i < n:
            ramf.write(ram)
        if prev is not None:
            if s.level != prev.level:
                events.append((f, "level", prev.level, s.level))
                say(f"frame {f}: level byte {prev.level} -> {s.level} (lives {s.lives} hp {s.hp} emu frame {s.frame})")
                if shots:
                    for k in (0, 1, 2, 5, 10, 20, 40, 80, 150, 250, 400, 600):
                        plan(f + k, f"lv_f{f:05d}_{prev.level}to{s.level}_p{k:03d}")
                if prev.level == 13 and s.level == 254:
                    cuts.append(f)
                    if shots:
                        for k in list(range(0, 41)) + [50, 59]:
                            plan(f + k, f"cut{len(cuts)}_f{f:05d}_p{k:02d}")
                        for k in (3, 2, 1):
                            pass
                        if len(cuts) == 1:
                            cut1_state = e.msave()
            if s.lives != prev.lives:
                events.append((f, "lives", prev.lives, s.lives))
                say(f"frame {f}: lives {prev.lives} -> {s.lives} (level {s.level} hp {s.hp})")
            if landing is None and s.level == 1 and prev.anim == 5 and s.anim == 4:
                landing = f
                say(f"frame {f}: $3B5 5 -> 4 in level 1 (landing)")
            if s.level == 13 and prev.id3 == 0x7E and s.id3 == 0x46 and lasthit is None:
                lasthit = f
                say(f"frame {f}: object slot 3 id 0x7e -> 0x46 (Queen's last hit), counter $586 {s.qctr}, hp {s.hp}")
                if shots:
                    for k in (0, 5, 30, 100, 200, 400, 600, 650):
                        plan(f + k, f"lasthit_f{f:05d}_p{k:03d}")
        if shots and f in todo:
            for label in todo[f]:
                shot(label)
        if f == n:
            final_sha = hashlib.sha1(ram).hexdigest()
            final_state = str(e.state())
            say(f"after the last input (frame {f}): RAM sha1 {final_sha}; state {final_state}")
        prev = s
        if f % 5000 == 0:
            say(f"  .. frame {f} level {s.level} lives {s.lives} hp {s.hp} ({time.time() - t0:.0f}s)")
    ramf.close()
    branch = None
    if shots and cut1_state is not None:
        # what the FIRST cut leads to when nothing is pressed (the route itself skips this screen with one press)
        e.mload(cut1_state)
        c1 = cuts[0]
        branch = []
        for k in range(1, 241):
            s = e.step((), 1)
            if k in (1, 5, 9, 10, 11, 12, 15, 20, 25, 30, 40, 60, 90, 120, 180, 240):
                shot(f"cut1noinput_f{c1:05d}_p{k:03d}")
                branch.append((k, s.level))
        say("no-input branch from the first cut: (frames after cut, level byte)", branch)
    res = {"inputs": str(path), "frames": n, "ram_sha1": final_sha, "landing": landing, "cuts_13_to_254": cuts,
           "last_hit": lasthit, "events": events, "final_state": final_state, "seconds": round(time.time() - t0, 1),
           "noinput_branch": branch}
    (FIX / f"u16v_{tag}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    say("done", json.dumps({k: res[k] for k in ("frames", "ram_sha1", "landing", "cuts_13_to_254", "last_hit", "seconds")}))
    e.close()


if __name__ == "__main__":
    main()

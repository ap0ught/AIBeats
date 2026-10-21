"""Verifier, pictures only: replay the list, photograph the frames before each level is left, and at each change of the
level byte from a real level to 254 run a NO-INPUT branch from an in-memory state (what the game shows between the levels
when nothing is pressed: the warp card / the next level's title), then return to the main line. The hash after the last
input is printed so the main line can be compared with the two plain replays.

    python u16v_cards.py <inputs file> <tag>
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
FIELDS = {"level": 0x10, "lives": 0x11, "anim": 0x3B5, "hp": 0x51A}

path, tag = sys.argv[1], sys.argv[2]
rows = Path(path).read_text(encoding="utf-8").split("\n")
if rows[-1] == "":
    rows = rows[:-1]
ins = [tuple(t for t in x.replace("+", ",").split(",") if t) for x in rows[1:]]
assert all(b in BUTTONS for f in ins for b in f)
prior = json.loads((FIX / "u16v_run1.json").read_text())
exits = [f for f, kind, a, b in prior["events"] if kind == "level" and a not in (0, 254, 255) and f > 1500]
want = {}
for f in exits:
    for k in (300, 240, 180, 120, 90, 60, 40, 20, 10, 5, 2, 1):
        want.setdefault(f - k, []).append(f"exit_f{f:05d}_m{k:03d}")
out = open(FIX / f"u16v_{tag}.stdout.txt", "w", encoding="utf-8")


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.write(s + "\n")
    out.flush()


e = BizHawk(log_name=f"u16v_{tag}_emu.log", fields=FIELDS)
say("emulator pid", e.proc.pid)


def shot(name):
    e.cmd(f"screenshot {SHOTS / (tag + '_' + name + '.png')}")


prev = None
t0 = time.time()
for i, btn in enumerate(ins):
    f = i + 1
    s = e.step(btn, 1)
    for label in want.get(f, []):
        shot(label)
    if prev is not None and prev.level not in (0, 254, 255) and s.level != prev.level and f > 1500:
        say(f"frame {f}: level byte {prev.level} -> {s.level}; no-input branch")
        sid = e.msave()
        seq = []
        for k in range(1, 901):
            b = e.step((), 1)
            if k % 15 == 0:
                shot(f"card_f{f:05d}_{prev.level}to{s.level}_n{k:03d}")
            if not seq or seq[-1][1] != b.level:
                seq.append((k, b.level))
        say("   level byte with no input (frames after the change, value):", seq)
        e.mload(sid)
        e.mfree(sid)
    prev = s
h = hashlib.sha1(e.ram_all()).hexdigest()
say(f"after the last input: RAM sha1 {h} ({time.time() - t0:.0f}s)")
e.close()

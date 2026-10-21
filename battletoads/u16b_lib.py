"""u16b (chain B) helpers.  up14 frame f (1-based input count); cap14.ram row f-1 = RAM after input f; bookmark cap14_f<N> = state after N inputs.
Level 8: L8c index i = up14 frame 12484 + i; the placement is frame 12488 (bookmark early_L8_p0)."""
import json
import os

import numpy as np

from toads.emulator import BizHawk, LOGS_DIR, STATES_DIR

FIX = LOGS_DIR / "fix"
P0 = 12488                       # up14 frame of the Level 8 placement
L8_FIRST = 12484                 # up14 frame of L8c's first input
L9_FIRST = 17367                 # up14 frame of L9c's first input (the placement in Terra Tubes is 17366)
F8 = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "st": 0x4B1,
      "hp": 0x51A, "face": 0x4A2, "lives": 0x11, "camlo": 0x89, "camhi": 0x8A}
for _k in range(6):
    F8[f"sc{_k}"] = 0x5F4 + _k
for _q in range(1, 15):
    F8[f"id{_q}"] = 0x3C1 + _q
    F8[f"ox{_q}"] = 0x3FD + _q
    F8[f"oh{_q}"] = 0x439 + _q


def up14_inputs():
    return [l.strip().replace(",", "+") for l in open(LOGS_DIR / "up14.inputs.txt") if not l.startswith("#")]


def bt(l):
    return tuple(x for x in l.replace(",", "+").split("+") if x)


def cap():
    return np.memmap(LOGS_DIR / "cap14.ram", dtype=np.uint8, mode="r").reshape(-1, 2048)


def banned(b):
    s = set(bt(b))
    return ("Left" in s and "Right" in s) or ("Up" in s and "Down" in s) or "Start" in s


def score(s):
    return int("".join(str(s[f"sc{k}"] & 15) for k in range(6)))


def boss(s):
    for q in range(1, 15):
        if s[f"id{q}"] == 0x7D:
            return s[f"ox{q}"], s[f"oh{q}"]
    return None


def seg(name):
    return json.load(open(LOGS_DIR / f"pbeam_{name}.json"))


def write_json(path, obj, indent=None):
    """utf-8, temp file + rename, keep a .backup copy of what was there"""
    path = str(path)
    if os.path.exists(path):
        bak = path + ".backup"
        try:
            if os.path.exists(bak):
                os.remove(bak)
            os.replace(path, bak)
        except OSError:
            pass
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent)
    os.replace(tmp, path)


def diff(a, b, skip_stack=False):
    return [i for i in range(0x800) if a[i] != b[i] and not (skip_stack and 0x100 <= i < 0x200)]

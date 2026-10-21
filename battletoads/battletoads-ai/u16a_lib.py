"""Chain A (up16a) helpers, 2026-10-10.  Nothing here writes memory; everything is inputs on savestates.

    seg(name)            -> the input list of logs/pbeam_<name>.json ('+'-joined buttons, '' = nothing)
    bt(s)                -> tuple of buttons
    banned(inputs)       -> (Left+Right, Up+Down, Start, total frames with Select)
    write_seg(name, d)   -> logs/pbeam_<name>.json via a temp file + rename (never overwrites silently: keeps .backup)
"""
import json
import os
import shutil

from toads.emulator import BizHawk, LOGS_DIR, STATES_DIR, PROJECT  # noqa: F401

FIX = LOGS_DIR / "fix"

INTRO = [("Right", 1170), ("Start", 4), ("A", 727), ("", 16)]          # assemble.py's fixed intro (1,917 frames)


def bt(s):
    return tuple(x for x in s.replace(",", "+").split("+") if x)


def seg(name):
    return [b.replace(",", "+") for b in json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["inputs"]]


def segj(name):
    return json.load(open(LOGS_DIR / f"pbeam_{name}.json"))


def route_inputs(names):
    ins = []
    for b, n in INTRO:
        ins += [b] * n
    for nm in names:
        ins += seg(nm)
    return ins


def banned(inputs):
    lr = ud = st = sel = 0
    for b in inputs:
        t = set(bt(b))
        lr += {"Left", "Right"} <= t
        ud += {"Up", "Down"} <= t
        st += "Start" in t
        sel += "Select" in t
    return lr, ud, st, sel


def write_json(path, d, indent=None):
    path = str(path)
    if os.path.exists(path):
        shutil.copyfile(path, path + ".backup")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=indent)
    os.replace(tmp, path)


def write_seg(name, d):
    write_json(LOGS_DIR / f"pbeam_{name}.json", d)


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, h=m[0x439], depth=m[0x41B], z=m[0x475], hp=m[0x51A], lives=m[0x11],
                score=int("".join(str(m[0x5F4 + k] & 15) for k in range(6))), t0b=m[0x0B], t0c=m[0x0C], rng=bytes(m[0x25:0x29]).hex())


def diff(a, b, skip_stack=True):
    return [i for i in range(0x800) if a[i] != b[i] and not (skip_stack and 0x100 <= i < 0x200)]

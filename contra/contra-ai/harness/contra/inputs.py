"""The harness's input format, and conversions.

One frame = a tuple of button names, e.g. ("Right", "B"). On disk (logs/<name>.inputs.txt): a header line
"# frames=N ..." then one line per frame, buttons joined by "+" (empty line = nothing held). "," is accepted
on read for compatibility with the toads logs. Frame k (1-based) is the input held while the emulator advances
from framecount k-1 to k, when the list is played from power-on.

Mask byte (same layout as the game's own controller byte at $F1):
    A=0x80 B=0x40 Select=0x20 Start=0x10 Up=0x08 Down=0x04 Left=0x02 Right=0x01
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
BIT = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 0x08, "Down": 0x04, "Left": 0x02, "Right": 0x01}
ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


def to_mask(btn: Iterable[str]) -> int:
    m = 0
    for b in btn:
        m |= BIT[b]
    return m


def from_mask(m: int) -> tuple[str, ...]:
    return tuple(b for b in ORDER if m & BIT[b])


def parse_line(line: str) -> tuple[str, ...]:
    out = tuple(x for x in line.strip().replace(",", "+").split("+") if x)
    for b in out:
        if b not in BIT:
            raise ValueError(f"unknown button {b!r}")
    return out


def read_inputs(path: str | Path) -> list[tuple[str, ...]]:
    rows = []
    # splitlines(): "a\n\n" -> ["a", ""], so trailing empty-input frames survive and the final newline adds nothing
    for l in Path(path).read_text(encoding="utf-8").splitlines():
        if l.startswith("#"):
            continue
        rows.append(parse_line(l))
    return rows


def write_inputs(path: str | Path, rows: Sequence[Iterable[str]], comment: str = "") -> Path:
    """utf-8, temp file then rename, keeps <name>.backup of what it replaces."""
    path = Path(path)
    body = f"# frames={len(rows)} {comment}".rstrip() + "\n" + "\n".join("+".join(r) for r in rows) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    if path.exists():
        bak = path.with_name(path.name + ".backup")
        try:
            os.replace(path, bak)
        except OSError:
            pass
    os.replace(tmp, path)
    return path


def to_hex(rows: Sequence[Iterable[str]]) -> str:
    return "".join(f"{to_mask(r):02x}" for r in rows)

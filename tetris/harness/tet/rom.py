"""The owner's Tetris ROM, read in memory straight from their zip (never copied, never written to disk).

    from tet.rom import prg, chr_, rd, rd16
    prg()            -> the 32 KB of PRG; CPU address a (>= $8000) is prg()[a - 0x8000]
    rd(a), rd16(a)   -> byte / little-endian word at CPU address a

Identity (checked on every load): PRG+CHR sha1 FD9079CB5E8479EB06D93C2AE5175BFCE871746A, crc32 1394F57E =
"Tetris", Nintendo, NES-EI-USA, 1989-11, NES-NTSC, board NES-SEROM (MMC1), dump "ok" in BizHawk's
gamedb/NesCarts.xml (bootgod). PRG NES-EI-0 crc 943DFBBE, CHR NES-EI-0 crc 251AF21C.
The file in the zip has a NES 2.0 header (4E 45 53 1A 02 02 10 08 50 00 00 00 00 00 00 01), so whole-file
hashes differ from lists made with an iNES 1.0 header; only the headerless hash identifies the game.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from functools import lru_cache
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
ZIP = PROJECT / "Tetris (USA).zip"
HEADERLESS_SHA1 = "fd9079cb5e8479eb06d93c2ae5175bfce871746a"


@lru_cache(maxsize=1)
def _load() -> tuple[bytes, bytes]:
    raw = ZIP.read_bytes()
    zf = zipfile.ZipFile(io.BytesIO(raw))
    names = [zi.filename for zi in zf.infolist() if not zi.is_dir()]
    if len(names) != 1:
        raise RuntimeError(f"expected one file in {ZIP.name}, found {names}")
    data = zf.read(names[0])
    if data[:4] != b"NES\x1a":
        raise RuntimeError("not an iNES file")
    body = data[16:]
    if hashlib.sha1(body).hexdigest() != HEADERLESS_SHA1:
        raise RuntimeError("this is not Tetris (USA) NES-EI-USA: headerless sha1 " + hashlib.sha1(body).hexdigest())
    n_prg = data[4] * 16384
    return body[:n_prg], body[n_prg:n_prg + data[5] * 8192]


def prg() -> bytes:
    return _load()[0]


def chr_() -> bytes:
    return _load()[1]


def rd(a: int) -> int:
    return prg()[a - 0x8000]


def rd16(a: int) -> int:
    p = prg()
    return p[a - 0x8000] | (p[a - 0x8000 + 1] << 8)


def table(a: int, n: int) -> list[int]:
    p = prg()
    return list(p[a - 0x8000:a - 0x8000 + n])

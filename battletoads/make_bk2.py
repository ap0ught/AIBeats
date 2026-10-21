"""Write a BizHawk .bk2 movie from a per-frame input log (one line per frame, buttons joined by , or +).

    python make_bk2.py logs/up14.inputs.txt out.bk2
Then BizHawk: load your own Battletoads (USA) ROM, File > Movie > Play Movie."""
import hashlib
import sys
import zipfile
from pathlib import Path

from toads.emulator import ROM

ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
MNEMONIC = {"Up": "U", "Down": "D", "Left": "L", "Right": "R", "Select": "s", "Start": "S", "B": "B", "A": "A"}
LOG_KEY = "LogKey:#Reset|Power|#P1 Up|P1 Down|P1 Left|P1 Right|P1 Select|P1 Start|P1 B|P1 A|"


def rom_sha1(rom=ROM):
    data = Path(rom).read_bytes()
    if data[:4] == b"NES\x1a":
        data = data[16:]          # BizHawk hashes the ROM without the iNES header
    return hashlib.sha1(data).hexdigest().upper()


def write_bk2(frames, out, comment=""):
    header = "\n".join(["MovieVersion BizHawk v2.0.0", "Author Claude (Anthropic), via Claude Code",
                        "emuVersion Version 2.11.1", "OriginalEmuVersion Version 2.11.1", "Platform NES", "SystemID NES",
                        "GameName Battletoads", f"SHA1 {rom_sha1()}", "rerecordCount 0", "Core quickerNES"]) + "\n"
    held = lambda f: "|..|" + "".join(MNEMONIC[b] if b in f else "." for b in ORDER) + "|"
    log = "[Input]\n" + LOG_KEY + "\n" + "\n".join(held(set(f)) for f in frames) + "\n[/Input]\n"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Header.txt", header)
        z.writestr("Input Log.txt", log)
        z.writestr("Comments.txt", comment + "\n")
        z.writestr("Subtitles.txt", "")
    return out


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    lead = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    frames = [()] * lead + [tuple(b for b in l.replace("+", ",").split(",") if b)
                            for l in open(src).read().splitlines() if not l.startswith("#")]
    write_bk2(frames, out, "AI vs Battletoads: Any% (No Credits Warp), 12:23.393 on the speedrun clock, "
                           f"{len(frames)} frames from power-on")
    print("wrote", out, len(frames), "frames")

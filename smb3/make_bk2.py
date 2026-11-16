"""Write the BizHawk movie (.bk2) of the Super Mario Bros. 3 run from its plain input file.

    python make_bk2.py smb3_ai_10m39s.inputs.txt smb3_ai_10m39s.bk2 [--tail 120] [--rom "Super Mario Bros. 3 (USA).nes"]

The input file has one line per frame (buttons joined by '+', an empty line = no buttons, '#' lines are comments).
Line k of the file (1-based) is the input of emulator frame k from power-on. The run was BUILT on Mesen; on BizHawk's
NesHawk core the power-on comes one frame earlier, so NesHawk plays the file WITHOUT its first line (which is empty).
In a BizHawk movie input-log line k is played on frame k, and BizHawk's frame 1 is the frame NesHawk emulates before
the file's second line, so the movie is simply the file itself, line for line: movie line k = file line k (line 1 is
the empty lead-in that NesHawk "drops"). `--tail` idle lines are added after the last line so the fade after Bowser's
door is part of the movie (the run ends on line 38,502; the fade's first darker picture is frame 38,507).

The header names the NesHawk core and the ROM hash BizHawk reports for the cartridge (gameinfo.getromhash(), the SHA-1
of the whole .nes file including its 16-byte iNES header). No savestate: the movie starts from power-on. No
SyncSettings.json: the run was checked with NesHawk's default sync settings.
"""
import argparse
import hashlib
import zipfile
from pathlib import Path

ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
MNEMONIC = {"Up": "U", "Down": "D", "Left": "L", "Right": "R", "Select": "s", "Start": "S", "B": "B", "A": "A"}
LOG_KEY = "LogKey:#Reset|Power|#P1 Up|P1 Down|P1 Left|P1 Right|P1 Select|P1 Start|P1 B|P1 A|"
ROM_SHA1_WHOLE = "5F9019040FE23CB412A484E1EF430E59E589F9B4"      # Super Mario Bros. 3 (USA) PRG0, whole file (BizHawk's hash)


def read_rows(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        btn = tuple(b for b in line.replace(",", "+").split("+") if b.strip())
        for b in btn:
            if b not in MNEMONIC:
                raise SystemExit(f"unknown button {b!r} in {path}")
        rows.append(set(btn))
    return rows


def movie_line(held):
    return "|..|" + "".join(MNEMONIC[b] if b in held else "." for b in ORDER) + "|"


def write_bk2(rows, out, comment, board=None):
    header = [
        "MovieVersion BizHawk v2.0.0",
        "Author Claude (Anthropic), via Claude Code",
        "emuVersion Version 2.11.1",
        "OriginalEmuVersion Version 2.11.1",
        "Platform NES",
        "SystemID NES",
        "GameName Super Mario Bros. 3 (USA)",
        f"SHA1 {ROM_SHA1_WHOLE}",
        "rerecordCount 0",
        "Core NesHawk",
    ] + ([f"BoardName {board}"] if board else [])
    lines = [movie_line(r) for r in rows]
    log = "[Input]\n" + LOG_KEY + "\n" + "\n".join(lines) + "\n[/Input]\n"
    tmp = Path(str(out) + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Header.txt", "\n".join(header) + "\n")
        z.writestr("Input Log.txt", log)
        z.writestr("Comments.txt", comment + "\n")
        z.writestr("Subtitles.txt", "")
    tmp.replace(out)
    return len(lines)


def check_roundtrip(rows, out):
    """read the movie back: its input log must be the rows exactly"""
    with zipfile.ZipFile(out) as z:
        log = z.read("Input Log.txt").decode("utf-8").splitlines()
    assert log[0] == "[Input]" and log[1] == LOG_KEY and log[-1] == "[/Input]"
    body = log[2:-1]
    assert len(body) == len(rows), (len(body), len(rows))
    back = [{b for b, c in zip(ORDER, l[4:12]) if c != "."} for l in body]
    assert back == rows, "input log differs from the file"
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs")
    ap.add_argument("out")
    ap.add_argument("--tail", type=int, default=120)
    ap.add_argument("--board", default=None, help="BoardName for the header (what BizHawk reports; optional)")
    ap.add_argument("--rom", help="optional: check the ROM's hash against the header")
    a = ap.parse_args()
    if a.rom:
        sha = hashlib.sha1(Path(a.rom).read_bytes()).hexdigest().upper()
        print("ROM whole-file SHA-1", sha, "OK" if sha == ROM_SHA1_WHOLE else "DIFFERENT from the header's")
    rows = read_rows(a.inputs)
    if rows[0]:
        raise SystemExit("the file's first line must be empty (it is the frame NesHawk emulates before the movie's input)")
    n_file = len(rows)
    rows = rows + [set()] * a.tail
    src_sha = hashlib.sha1(Path(a.inputs).read_bytes()).hexdigest()
    comment = (f"Super Mario Bros. 3 (NES, USA PRG0), Any% (No Wrong Warp), an AI-built run under human input rules. "
               f"{n_file} input lines from power-on (input file sha1 {src_sha}) + {a.tail} idle lines; movie line k = "
               f"file line k. Timing: Start press on line 68, Level_ExitToMap on Bowser's door on frame 38502 (5 frames "
               f"before the fade): 38,434 frames = 10:39.514 at 60.0988 fps. Core NesHawk, BizHawk 2.11.1.")
    n = write_bk2(rows, a.out, comment, a.board)
    check_roundtrip(rows, a.out)
    print(f"wrote {a.out}: {n} movie frames ({n_file} file lines + {a.tail} idle), input log == file: OK")


if __name__ == "__main__":
    main()

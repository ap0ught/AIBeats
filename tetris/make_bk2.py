"""Write the BizHawk movie (.bk2) of a Tetris run from its plain input list, and read it back to check it.

    python make_bk2.py tetris_ai_2m14s_any_piece.inputs.txt tetris_ai_2m14s_any_piece.bk2 [--rom "Tetris (USA).nes"]

The input list has one line per frame (buttons joined by '+', an empty line = no buttons, '#' lines are comments).
Row k (1-based) of the list is the input of emulator frame k from power-on: the harness power-cycles the core
(frame counter 0) and then plays row 1 on frame 1, row 2 on frame 2, and so on. In a BizHawk movie, input-log line k
is also played on frame k, so the movie is the list unchanged, with no lead-in line. verify_bk2.py confirms this
frame by frame: BizHawk's own playback of the movie gives the same RAM on every frame as the harness's replay.

The header names the NesHawk core and the SHA-1 of the whole Tetris (USA) .nes file (with its 16-byte iNES header).
No savestate, no SyncSettings: the runs were made and checked with NesHawk's default settings.
"""
import argparse
import hashlib
import zipfile
from pathlib import Path

ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
MNEMONIC = {"Up": "U", "Down": "D", "Left": "L", "Right": "R", "Select": "s", "Start": "S", "B": "B", "A": "A"}
LOG_KEY = "LogKey:#Reset|Power|#P1 Up|P1 Down|P1 Left|P1 Right|P1 Select|P1 Start|P1 B|P1 A|"
ROM_SHA1_WHOLE = "3026D28B63D94C921FE58364F8B0659D10B5A0AC"      # Tetris (USA).nes, whole file
ROM_SHA1_DATA = "FD9079CB5E8479EB06D93C2AE5175BFCE871746A"       # the same without the 16-byte header (PRG + CHR)
BOARD = "SxROM"                                                     # BizHawk's board name for this cartridge (MMC1)
LEAD_IN = 0

RUNS = {
    "any": "100 Lines, A-Type, level 19 start, any piece: 2:14.91 (8,108 frames from the Start press on level select "
           "to the first frame the LINES counter shows 100). Cheez's world record time is 2:43.54.",
    "tetrises": "100 Lines, A-Type, level 19 start, tetrises only (25 clears, every one 4 rows): 2:16.24 (8,188 "
                "frames from the Start press on level select to the first frame the LINES counter shows 100). "
                "Cheez's world record time (any clears) is 2:43.54.",
}


def read_rows(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        btn = tuple(b.strip() for b in line.replace(",", "+").split("+") if b.strip())
        for b in btn:
            if b not in MNEMONIC:
                raise SystemExit(f"unknown button {b!r} in {path}")
        rows.append(set(btn))
    return rows


def movie_line(held):
    return "|..|" + "".join(MNEMONIC[b] if b in held else "." for b in ORDER) + "|"


def write_bk2(rows, out, comment):
    head = ["MovieVersion BizHawk v2.0.0", "Author Claude (Anthropic), via Claude Code", "emuVersion Version 2.11.1",
            "OriginalEmuVersion Version 2.11.1", "Platform NES", "SystemID NES", "GameName Tetris (USA)",
            f"SHA1 {ROM_SHA1_WHOLE}", "rerecordCount 0", "Core NesHawk"]
    if not BOARD.startswith("{"):
        head.append(f"BoardName {BOARD}")
    lines = [movie_line(set())] * LEAD_IN + [movie_line(r) for r in rows]
    log = "[Input]\n" + LOG_KEY + "\n" + "\n".join(lines) + "\n[/Input]\n"
    tmp = Path(str(out) + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Header.txt", "\n".join(head) + "\n")
        z.writestr("Input Log.txt", log)
        z.writestr("Comments.txt", comment + "\n")
        z.writestr("Subtitles.txt", "")
    tmp.replace(out)
    return len(lines)


def check_roundtrip(rows, out):
    """Read the movie back and confirm its input log is the list exactly."""
    with zipfile.ZipFile(out) as z:
        log = z.read("Input Log.txt").decode("utf-8").splitlines()
    assert log[0] == "[Input]" and log[1] == LOG_KEY and log[-1] == "[/Input]"
    body = log[2:-1]
    assert len(body) == LEAD_IN + len(rows), (len(body), len(rows))
    back = [{b for b, c in zip(ORDER, l[4:12]) if c != "."} for l in body[LEAD_IN:]]
    assert back == rows, "input log differs from the list"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs")
    ap.add_argument("out")
    ap.add_argument("--rom", help="optional: check your ROM's hash against the header")
    a = ap.parse_args()
    if a.rom:
        data = Path(a.rom).read_bytes()
        whole = hashlib.sha1(data).hexdigest().upper()
        body = hashlib.sha1(data[16:]).hexdigest().upper()
        print("ROM whole-file SHA-1", whole, "OK" if whole == ROM_SHA1_WHOLE else
              ("(header differs, game data OK)" if body == ROM_SHA1_DATA else "DIFFERENT GAME DATA"))
    rows = read_rows(a.inputs)
    kind = "tetrises" if "tetrises" in Path(a.inputs).name else "any"
    src_sha = hashlib.sha1(Path(a.inputs).read_bytes()).hexdigest()
    comment = (f"Tetris (NES, USA), an AI-built tool-assisted run under human input rules (no turbo: a new press of "
               f"a button at most every 2 frames = 30 per second; no Left+Right, no Up+Down; controller 1 only). "
               f"{RUNS[kind]} {len(rows)} input rows from power-on (input list sha1 {src_sha}); movie line k = list "
               f"row k = frame k. Core NesHawk, BizHawk 2.11.1.")
    n = write_bk2(rows, a.out, comment)
    check_roundtrip(rows, a.out)
    print(f"wrote {a.out}: {n} movie frames ({LEAD_IN} lead-in + {len(rows)} rows), input log == list: OK")


if __name__ == "__main__":
    main()

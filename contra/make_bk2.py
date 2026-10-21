"""Write the BizHawk movie (.bk2) of the Contra run from its plain input list.

    python make_bk2.py run_chain2.inputs.txt contra_ai_9m24s.bk2 [--rom "Contra (USA).nes"] [--sync SyncSettings.json]

The input list has one line per frame (buttons joined by '+', an empty line = no buttons, '#' lines are comments).
Row i (0-based) of the list is played on emulator frame i + 2 of a fresh power-on: BizHawk emulates frame 1 before
a Lua script gets control, so the harness's first input lands on frame 2. In a BizHawk movie, input-log line k is
played on frame k + 1 (the first line is frame 1). So the movie is ONE empty line followed by the list, unchanged:
movie line k + 1 = list row k, both on frame k + 2.

The header names the NesHawk core and the ROM hash BizHawk reports for the US cartridge (gameinfo.getromhash(), the
SHA-1 of the whole .nes file including its 16-byte iNES header). No savestate: the movie starts from power-on.
No SyncSettings.json: the run was made and checked with NesHawk's default sync settings, so BizHawk plays the movie
with the player's own NesHawk settings, which must be the defaults (--sync can embed a settings file if needed).
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
MNEMONIC = {"Up": "U", "Down": "D", "Left": "L", "Right": "R", "Select": "s", "Start": "S", "B": "B", "A": "A"}
LOG_KEY = "LogKey:#Reset|Power|#P1 Up|P1 Down|P1 Left|P1 Right|P1 Select|P1 Start|P1 B|P1 A|"
ROM_SHA1_WHOLE = "C9EA66BB7CB30AD5343F1721B1D4D3219859319B"      # Contra (USA).nes, whole file (BizHawk's hash)
LEAD_IN = 1                                                        # empty movie lines before list row 0


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


def write_bk2(rows, out, comment, sync=None):
    header = "\n".join([
        "MovieVersion BizHawk v2.0.0",
        "Author Claude (Anthropic), via Claude Code",
        "emuVersion Version 2.11.1",
        "OriginalEmuVersion Version 2.11.1",
        "Platform NES",
        "SystemID NES",
        "GameName Contra",
        f"SHA1 {ROM_SHA1_WHOLE}",
        "rerecordCount 0",
        "Core NesHawk",
        "BoardName UNROM",
    ]) + "\n"
    lines = [movie_line(set())] * LEAD_IN + [movie_line(r) for r in rows]
    log = "[Input]\n" + LOG_KEY + "\n" + "\n".join(lines) + "\n[/Input]\n"
    tmp = Path(str(out) + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Header.txt", header)
        z.writestr("Input Log.txt", log)
        z.writestr("Comments.txt", comment + "\n")
        z.writestr("Subtitles.txt", "")
        if sync:
            z.writestr("SyncSettings.json", Path(sync).read_text(encoding="utf-8-sig"))
    tmp.replace(out)
    return len(lines)


def check_roundtrip(rows, out):
    """Read the movie back and confirm its input log is the list exactly (after the lead-in)."""
    with zipfile.ZipFile(out) as z:
        log = z.read("Input Log.txt").decode("utf-8").splitlines()
    assert log[0] == "[Input]" and log[1] == LOG_KEY and log[-1] == "[/Input]"
    body = log[2:-1]
    assert len(body) == LEAD_IN + len(rows), (len(body), len(rows))
    assert all(l == "|..|........|" for l in body[:LEAD_IN])
    back = [{b for b, c in zip(ORDER, l[4:12]) if c != "."} for l in body[LEAD_IN:]]
    assert back == rows, "input log differs from the list"
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs")
    ap.add_argument("out")
    ap.add_argument("--rom", help="optional: check the ROM's hash against the header")
    ap.add_argument("--sync", help="optional: SyncSettings.json to embed")
    a = ap.parse_args()
    if a.rom:
        sha = hashlib.sha1(Path(a.rom).read_bytes()).hexdigest().upper()
        print("ROM whole-file SHA-1", sha, "OK" if sha == ROM_SHA1_WHOLE else "DIFFERENT from the header's")
    rows = read_rows(a.inputs)
    src_sha = hashlib.sha1(Path(a.inputs).read_bytes()).hexdigest()
    comment = (f"Contra (NES, USA), Any% 1 player, an AI-built tool-assisted run under the human 'No Turbo' "
               f"category's input rules. {len(rows)} input rows from power-on (input list sha1 {src_sha}); "
               f"movie line k+1 = list row k (one empty lead-in frame). Clock: medals seen frame 594, Bill stands "
               f"frame 34509: 33,915 frames = 9:24.321 at 60.0988 fps. Core NesHawk, BizHawk 2.11.1.")
    n = write_bk2(rows, a.out, comment, a.sync)
    check_roundtrip(rows, a.out)
    print(f"wrote {a.out}: {n} movie frames ({LEAD_IN} lead-in + {len(rows)} rows), input log == list: OK")


if __name__ == "__main__":
    main()

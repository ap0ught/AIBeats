"""Convert a downloaded TAS input log (.fm2 FCEUX text, .fmv Famtasia binary) to this harness's input format.
The movie file is DATA: this script only parses bytes. Self-contained on purpose; run it isolated:

    python -I tools/tas_convert.py <movie.fm2|.fmv> <out.inputs.txt> [--stats]

Output: "# frames=N ..." then one line per frame, buttons joined by "+" (controller 1 only).
Controller 2 input and reset commands are counted and reported, never written.
"""
import os
import sys
from pathlib import Path

FM2_ORDER = "RLDUTSBA"
FM2_NAME = {"R": "Right", "L": "Left", "D": "Down", "U": "Up", "T": "Start", "S": "Select", "B": "B", "A": "A"}
OUT_ORDER = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
# Famtasia .fmv controller byte (tasvideos.org EmulatorResources/Famtasia/FMV)
FMV_BITS = ((0x01, "Right"), (0x02, "Left"), (0x04, "Up"), (0x08, "Down"), (0x10, "B"), (0x20, "A"),
            (0x40, "Select"), (0x80, "Start"))


def parse_fm2(data: bytes):
    header, rows, p2, cmds = {}, [], 0, 0
    for raw in data.decode("utf-8", "replace").splitlines():
        if not raw.startswith("|"):
            k, _, v = raw.partition(" ")
            if k:
                header.setdefault(k, v)
            continue
        parts = raw.split("|")
        # ['', commands, pad1, pad2, pad3?, '']
        if parts[1].strip() not in ("", "0"):
            cmds += 1
        pad1 = parts[2] if len(parts) > 2 else ""
        pad2 = parts[3] if len(parts) > 3 else ""
        btn = set()
        for i, ch in enumerate(pad1[:8]):
            if ch not in ". ":
                btn.add(FM2_NAME[FM2_ORDER[i]])
        if any(ch not in ". " for ch in pad2[:8]):
            p2 += 1
        rows.append(tuple(b for b in OUT_ORDER if b in btn))
    return header, rows, p2, cmds


def parse_fmv(data: bytes):
    assert data[:4] == b"FMV\x1a", "not a Famtasia movie"
    f4, f5 = data[4], data[5]
    header = {"from_savestate": bool(f4 & 0x80), "pad1": bool(f5 & 0x80), "pad2": bool(f5 & 0x40),
              "fds": bool(f5 & 0x20), "rerecords": int.from_bytes(data[0x0A:0x0E], "little") + 1,
              "emulator": data[0x10:0x50].split(b"\0")[0].decode("latin-1"),
              "title": data[0x50:0x90].split(b"\0")[0].decode("latin-1")}
    per = int(header["pad1"]) + int(header["pad2"]) + int(header["fds"])
    body = data[0x90:]
    rows, p2 = [], 0
    for i in range(0, len(body) - per + 1, per):
        j = i
        btn = set()
        if header["pad1"]:
            b = body[j]; j += 1
            btn = {n for m, n in FMV_BITS if b & m}
        if header["pad2"]:
            if body[j]:
                p2 += 1
            j += 1
        rows.append(tuple(b for b in OUT_ORDER if b in btn))
    return header, rows, p2, 0


def stats(rows):
    lr = sum(1 for r in rows if "Left" in r and "Right" in r)
    ud = sum(1 for r in rows if "Up" in r and "Down" in r)
    out = {"frames": len(rows), "left+right_frames": lr, "up+down_frames": ud}
    for b in OUT_ORDER:
        held = [b in r for r in rows]
        out[f"{b}_held"] = sum(held)
        out[f"{b}_presses"] = sum(1 for i, h in enumerate(held) if h and (i == 0 or not held[i - 1]))
    return out


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    data = src.read_bytes()
    header, rows, p2, cmds = parse_fmv(data) if src.suffix.lower() == ".fmv" else parse_fm2(data)
    keep = {k: header[k] for k in list(header)[:40] if k not in ("comment", "subtitle")}
    print("header:", keep)
    print("controller-2 frames:", p2, " command (reset) frames:", cmds)
    print("stats:", stats(rows))
    first = next((i + 1 for i, r in enumerate(rows) if r), None)
    print("first input on movie frame", first, rows[first - 1] if first else None)
    body = (f"# frames={len(rows)} source={src.name} p2_frames_dropped={p2} cmd_frames={cmds}\n"
            + "\n".join("+".join(r) for r in rows) + "\n")
    tmp = dst.with_name(dst.name + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    if dst.exists():
        os.replace(dst, dst.with_name(dst.name + ".backup"))
    os.replace(tmp, dst)
    print("wrote", dst)

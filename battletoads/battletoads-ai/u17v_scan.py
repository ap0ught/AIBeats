"""u17v_scan.py - the up17 verifier's own scan of an input list (reads the raw bytes; no emulator).

    python u17v_scan.py <inputs.txt> [segment names in route order]

Checks every line: only the 8 controller-1 button names, no Left+Right, no Up+Down, no repeated token, no stray
characters. Lists every Start frame, every Select frame (as ranges), the A/B statistics, and - when segments are
given - whether the list equals the fixed intro + logs/pbeam_<segment>.json inputs, and the frame range of each.
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEGAL = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
INTRO = [("Right", 1170), ("Start", 4), ("A", 727), ("", 16)]      # the fixed power-on intro (1,917 frames)


def ranges(fr):
    out = []
    for f in fr:
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def main():
    path = Path(sys.argv[1])
    segs = sys.argv[2:]
    raw = path.read_bytes()
    print(f"file {path}  bytes {len(raw)}  sha1 {hashlib.sha1(raw).hexdigest()}")
    odd = sorted(set(raw) - set(b"\r\n,# =") - set(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    print("bytes outside letters/digits/comma/CR/LF/#/space/=:", odd)
    lines = raw.decode("ascii").split("\n")
    head, body = lines[0], lines[1:]
    if body and body[-1] == "":
        body = body[:-1]
    print("header:", repr(head), " input lines:", len(body))
    crlf = sum(1 for ln in body if ln.endswith("\r"))
    print(f"line endings: {crlf} CRLF, {len(body) - crlf} LF")
    frames = []
    bad = []
    lr, ud, rep = [], [], []
    per = collections.defaultdict(list)
    combos = collections.Counter()
    for n, ln in enumerate(body, 1):
        ln = ln.rstrip("\r")
        if ln != ln.strip() or " " in ln or "\t" in ln:
            bad.append((n, repr(ln)))
        toks = [t for t in ln.split(",")] if ln else []
        for t in toks:
            if t not in LEGAL:
                bad.append((n, repr(ln)))
        if "Left" in toks and "Right" in toks:
            lr.append(n)
        if "Up" in toks and "Down" in toks:
            ud.append(n)
        if len(set(toks)) != len(toks):
            rep.append(n)
        for t in set(toks):
            per[t].append(n)
        key = frozenset(toks)
        combos[key] += 1
        frames.append(key)
    declared = int(head.split("frames=")[1].split()[0])
    print(f"declared frames {declared}, counted {len(frames)}: {'OK' if declared == len(frames) else 'MISMATCH'}")
    print(f"lines with a token outside {LEGAL} or stray blanks: {len(bad)} {bad[:10]}")
    print(f"Left+Right frames: {len(lr)} {lr[:20]}")
    print(f"Up+Down frames: {len(ud)} {ud[:20]}")
    print(f"repeated-token frames: {len(rep)} {rep[:20]}")
    print("frames per button:", {b: len(per[b]) for b in LEGAL})
    print(f"Start frames ({len(per['Start'])}): {ranges(per['Start'])}")
    print(f"Select frames ({len(per['Select'])}): {ranges(per['Select'])}")
    print(f"empty frames: {combos[frozenset()]}")
    print("distinct button sets:", len(combos))
    for k, v in sorted(combos.items(), key=lambda kv: -kv[1]):
        print(f"   {'+'.join(sorted(k)) or '(none)':24s} {v}")
    # frames with A and B both down, and A/B alternation stretches (turbo-like)
    ab = [n for n, k in enumerate(frames, 1) if "A" in k and "B" in k]
    print(f"A+B together: {len(ab)} frames: {ranges(ab)}")
    if segs:
        ref = []
        for b, n in INTRO:
            ref += [frozenset([b]) if b else frozenset()] * n
        print(f"intro: frames 1-{len(ref)}")
        bounds = []
        for name in segs:
            j = json.loads((HERE / "logs" / f"pbeam_{name}.json").read_text())
            a = len(ref) + 1
            for s in j["inputs"]:
                ref.append(frozenset(t for t in s.replace("+", ",").split(",") if t))
            bounds.append((name, a, len(ref)))
            sel = [f for f in range(a, len(ref) + 1) if "Select" in ref[f - 1]]
            st = [f for f in range(a, len(ref) + 1) if "Start" in ref[f - 1]]
            print(f"segment {name:14s} frames {a}-{len(ref)} ({len(ref) - a + 1} inputs)  Select {len(sel)}  Start {len(st)}")
        same = ref == frames
        print(f"list == intro + segments, frame for frame: {same} (reference {len(ref)} frames, list {len(frames)})")
        if not same:
            for i, (x, y) in enumerate(zip(ref, frames), 1):
                if x != y:
                    print("   first difference at frame", i, sorted(x), sorted(y))
                    break
        (HERE / "logs" / "fix" / "u17v_segments.json").write_text(json.dumps(bounds))
    ok = not bad and not lr and not ud and not rep and declared == len(frames)
    print("SCAN", "CLEAN" if ok else "FAILED")


if __name__ == "__main__":
    main()

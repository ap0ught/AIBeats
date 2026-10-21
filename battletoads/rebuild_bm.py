"""Rebuild bookmarks by replaying a recorded segment: the emulator's savestate.save can lag behind the frame it was
called on when the run is busy (2026-09-27: the L4 script's later bookmarks held states hundreds of frames late),
so the recorded input list is the source of truth.

    python rebuild_bm.py logs/pbeam_L4a.json NAME1=FRAME1 [NAME2=FRAME2 ...]

Loads the segment's bookmark, replays inputs[:FRAME] and saves NAME (frames must be ascending). A 'verify' idle
step after each save re-loads the file and compares the toad's position."""
import json
import sys

from toads.emulator import BizHawk


def toad(r):
    return (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x51A], r[0x11])


def main():
    seg = json.load(open(sys.argv[1]))
    marks = sorted((a.split("=")[0], int(a.split("=")[1])) for a in sys.argv[2:])
    e = BizHawk(log_name="rebuild_bm.log")
    e.load(seg["bookmark"])
    f = 0
    for name, frame in marks:
        for s in seg["inputs"][f:frame]:
            e.step(tuple(b for b in s.split("+") if b), 1)
        f = frame
        t = toad(e.ram_all())
        e.save(name)
        sid = e.msave()
        e.load(name); e.step((), 1)
        t2 = toad(e.ram_all())
        print(f"{name} @ f{frame}: {t} saved, reloads as {t2} {'OK' if t2 == t else 'MISMATCH'}", flush=True)
        e.mload(sid)
    e.close()


if __name__ == "__main__":
    main()

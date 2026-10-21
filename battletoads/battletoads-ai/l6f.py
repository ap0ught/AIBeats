"""Level 6 segment with a faster room 2 spliced in: pbeam_L6a.json's inputs up to the room-2 entry (index 1984),
the fast room-2 line (knowledge/<file>, inputs from the entry until the warp engages), then the old warp
cutscene mash. Checked by replaying from a Karnath's Lair start bookmark: must end at Level 8's placement.

    python l6f.py <start bookmark> [room-2 file, default l6_room2_fast.json]  -> logs/pbeam_L6b.json
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR


def main(start, fn="l6_room2_fast.json"):
    d = json.load(open(LOGS_DIR / "pbeam_L6a.json"))
    old = d["inputs"]
    fast = json.load(open(f"knowledge/{fn}"))
    ins = old[:1984] + fast + old[2390:]
    e = BizHawk(log_name="l6f.log")
    e.load(start)
    warp = None
    for k, b in enumerate(ins):
        e.step(tuple(v for v in b.replace("+", ",").split(",") if v), 1)
        m = e.ram(0, 0x800)
        if warp is None and (m[0x23], m[0x24]) == (0x0D, 0xE5):
            warp = k + 1
    print("warp engaged at input", warp, "(old 2390); end: level", m[0x10], "toad", m[0x3FD] | m[0x3EE] << 8, m[0x439], "hp", m[0x51A], "lives", m[0x11], "inputs", len(ins))
    if m[0x10] == 7 and (m[0x3FD], m[0x439], m[0x51A]) == (128, 94, 47):
        json.dump({"bookmark": d["bookmark"], "inputs": ins, "note": d.get("note", "")}, open(LOGS_DIR / "pbeam_L6b.json", "w"))
        print("saved logs/pbeam_L6b.json")
    e.close()


if __name__ == "__main__":
    main(*sys.argv[1:])

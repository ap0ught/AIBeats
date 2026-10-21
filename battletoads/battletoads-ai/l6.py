"""Level 6, Karnath's Lair, room 1: a scripted policy from `L6_start` (the first frame of control after the
Level 4 Mega Warp, written by l4.py). Journal 007 has the room's geometry; in short: the room is three screens
tall (the height byte wraps twice - unwrap by continuity), three snakes at 2 px/f come out of holes one after
another, their heads pause at corners and lift a toad standing on them up the vertical legs, and the exit is a
ledge at (366,691) beside the marker object 0x4f that you reach with a double jump off the third snake's head.

    python l6.py   -> logs/pbeam_L6a.json (segment for assemble.py), bookmark L6_room2
"""
import json
import time

from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens


def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], hp=r[0x51A], lives=r[0x11],
                lvl=r[0x10], cam=r[0x87] + 256 * r[0x88])


def head(r):
    for s in range(2, 15):
        if r[0x3C1 + s] == 0x4c:
            return dict(x=r[0x3FD + s] + 256 * r[0x3EE + s], h=r[0x439 + s])
    return None


class Unwrap:
    """Track a height byte across its 256 wraps by continuity."""

    def __init__(self, value=None):
        self.v, self.prev = value, None

    def __call__(self, h, anchor=None):
        if self.prev is None:
            self.v = h if anchor is None else anchor
        else:
            self.v += ((h - self.prev + 128) % 256) - 128
        self.prev = h
        return self.v

    def reset(self):
        self.v, self.prev = None, None


class Rec:
    def __init__(self, emu, sampler=None):
        self.emu, self.inputs, self.f, self.sampler = emu, [], 0, sampler

    def step(self, btn=(), n=1):
        """one frame at a time so the height unwrappers see every frame (a 20-frame press can hide a wrap)"""
        for _ in range(n):
            self.inputs.append("+".join(btn))
            self.f += 1
            self.emu.step(btn, 1)
            if self.sampler:
                self.sampler()


def run(emu, bookmark="L6_start", log=print):
    emu.load(bookmark)
    tu, hu = Unwrap(), Unwrap()                              # toad / head heights, unwrapped
    rec = Rec(emu)
    snakes = 0                                               # how many heads have appeared (anchors 80, 304, 496)
    anchors = {1: 80, 2: 304, 3: 496}
    had_head = False

    def read():
        nonlocal snakes, had_head
        r = emu.ram_all(); t = toad(r); h = head(r)
        t["H"] = tu(t["h"], 30 if tu.prev is None else None)
        if h and not had_head:
            snakes += 1; hu.reset(); h["H"] = hu(h["h"], anchors.get(snakes, h["h"]))
        elif h:
            h["H"] = hu(h["h"])
        had_head = h is not None
        return t, h
    rec.sampler = lambda: read()

    def track(t, h, off=0, slack=2):
        """walk toward x = head.x + off"""
        if h is None:
            rec.step((), 1); return
        tx = h["x"] + off
        rec.step(("Right",) if t["x"] < tx - slack else ("Left",) if t["x"] > tx + slack else (), 1)

    # --- snake 1: jump on at 44 px, ride up the x-336 column and along the top to the right wall ------------
    for _ in range(200):
        t, h = read()
        if t["x"] >= 300:
            break
        rec.step(("Right",), 1)
    for _ in range(600):
        t, h = read()
        if h and t["x"] - h["x"] <= 44:
            break
        rec.step((), 1)
    rec.step(("A",), 32)
    for k in range(160):                                     # the probe's ride: 160 frames, x 449 once the head is gone
        t, h = read()
        tx = (h["x"] - 2) if h else 449
        rec.step(("Right",) if t["x"] < tx - 1 else ("Left",) if t["x"] > tx + 1 else (), 1)
    t, h = read()
    log(f"top right at f{rec.f}: {t}")
    emu.save("L6_topright")
    rec.step((), 133)                                        # snake 2 leaves the top-right hole ~22 f after the jump
    # --- snake 2: land on its nose, ride up the x-304 column (beam line), park, drop, hop, into the hole ------
    rec.step(("Left", "A"), 20)
    for _ in range(12):                                      # the probe's 12 tracking frames before its bookmark
        t, h = read()
        tx = (h["x"] + 2) if h else t["x"]
        rec.step(("Left",) if t["x"] > tx + 1 else ("Right",) if t["x"] < tx - 1 else (), 1)
    t, h = read()
    log(f"on snake 2 at f{rec.f}: {t} head {h}")
    emu.save("L6_onhead2")
    seg1 = PROJECT / "knowledge" / "l4s_L6_seg1.json"
    rec.step((), 2)
    for s in json.loads(seg1.read_text()):
        rec.step(tuple(b for b in s.split("+") if b), 1)
    t, h = read()
    log(f"column top at f{rec.f}: {t} head {h}")
    emu.save("L6_seg1_solved")
    for _ in range(300):                                     # trail the head by 10 px along the 400-run
        t, h = read()
        if h and h["x"] <= 222:
            break
        if h:
            rec.step(("Left",) if t["x"] > h["x"] + 12 else ("Right",) if t["x"] < h["x"] + 8 else (), 1)
        else:
            rec.step((), 1)
    for _ in range(300):                                     # park at 220 until the head, descending, is at h 250
        t, h = read()
        if t["x"] > 222:
            rec.step(("Left",), 1); continue
        if t["x"] < 218:
            rec.step(("Right",), 1); continue
        if h and h["H"] <= 250:
            break
        rec.step((), 1)
    log(f"parked at f{rec.f}: {t} head {h}")
    k0 = rec.f
    for _ in range(200):                                     # drop when the head has passed x 204 on the 240-run
        t, h = read()
        if h and h["x"] <= 204:
            break
        rec.step((), 1)
    for _ in range(40):
        t, h = read()
        if t["z"] == 8:
            break
        rec.step(("Left",), 1)
    fall0 = rec.f
    for _ in range(120):                                     # Left for the first 20 frames of the fall
        t, h = read()
        if t["z"] == 0:
            break
        rec.step(("Left",) if rec.f - fall0 < 20 else (), 1)
    log(f"on the 240-run at f{rec.f}: {t} head {h}")
    lifted = False
    for _ in range(300):                                     # walk to 124; hop 80 frames after the parked frame
        t, h = read()
        if t["H"] >= 440 and t["z"] == 0:
            lifted = True; break
        k = rec.f - k0
        if 80 <= k < 82:
            rec.step(("Left", "A"), 1); continue
        rec.step(("Left",) if t["x"] > 124 else (), 1)
    log(f"lifted at x 112 at f{rec.f}: {t} lifted {lifted}")
    emu.save("L6_lifted112")
    k1 = rec.f
    for _ in range(147):                                     # into the hole; snake 3 leaves the hole below at ~+170
        t, h = read()
        rec.step(("Left",) if t["x"] > 64 else (), 1)
    log(f"in the hole at f{rec.f}: {t}")
    # --- snake 3: board it, ride to the 496-body's end, catch the head climbing x 400, the 560-run ------------
    rec.step(("Right", "A"), 20)
    for _ in range(400):                                     # track its centre along 496 to x 308
        t, h = read()
        if t["x"] >= 308 and t["H"] > 500:
            break
        track(t, h, 0, 2)
    log(f"on snake 3 at f{rec.f}: {t} head {h}")
    emu.save("L6_onsnake3")
    for _ in range(400):                                     # park at 312 until the head has dived below 440
        t, h = read()
        if h and h["H"] < 440:
            break
        rec.step(("Right",) if t["x"] < 310 else ("Left",) if t["x"] > 314 else (), 1)
    for _ in range(400):                                     # to the body's end; jump when the climbing head reaches 470
        t, h = read()
        if h and h["x"] >= 396 and h["H"] >= 470:
            break
        rec.step(("Right",) if t["x"] < 330 else ("Left",) if t["x"] > 334 else (), 1)
    rec.step(("Right", "A"), 20)
    for _ in range(200):
        t, h = read()
        if t["z"] == 0 and t["H"] >= 560:
            break
        track(t, h, 0, 2)
    log(f"on the 560-run at f{rec.f}: {t} head {h}")
    emu.save("L6_on560")
    for _ in range(300):                                     # track the head left; the toad drifts to (126,574)
        t, h = read()
        if t["x"] <= 182:
            break
        track(t, h, 0, 2)
    for _ in range(400):                                     # the head returns along 624: jump as it passes overhead
        t, h = read()
        if h and h["H"] >= 620 and h["x"] - t["x"] >= -8:
            break
        rec.step((), 1)
    rec.step(("A",), 32)
    for _ in range(60):
        t, h = read()
        if t["z"] == 0 and t["H"] >= 630:
            break
        rec.step((), 1)
    log(f"on snake 3's head on 624 at f{rec.f}: {t} head {h}")
    for _ in range(200):                                     # ride right to x 270, then jump to the ledge
        t, h = read()
        if t["x"] >= 270:
            break
        track(t, h, 0, 2)
    rec.step(("Right", "A"), 32)
    for _ in range(80):
        t, h = read()
        if t["z"] == 0 and t["H"] >= 680:
            break
        rec.step(("Right",), 1)
    log(f"on the exit ledge at f{rec.f}: {t}")
    emu.save("L6_ledge")
    px = t["x"]
    for _ in range(400):                                     # stand until the room changes
        t, h = read()
        if abs(t["x"] - px) > 100 or t["lvl"] != 8:
            break
        px = t["x"]; rec.step((), 1)
    log(f"room 2 at f{rec.f}: {t}")
    emu.save("L6_room2")
    room2(emu, rec, read, log)
    return rec


def room2(emu, rec, read, log):
    """Room 2 = the warp to Level 8. The toad drops to the floor at (76,30); the portal 0x22 sits at (432,104)
    from the first frame and vanishes at f449; a snake rises from the floor hole at (112,32) at f70, reaches
    h 336 at f220 and runs right to x 176, then down. Spikes: the floor from x~160, single tiles in the air at
    (128/224/320, 238-254), a block at (336-352, <=94). Route (journal 007): stand beside the column at x 103-105
    and CLIMB it - Left+A / Right+A alternating every 4 frames (the toad climbs snake bodies, anim 88/89) - to
    the 336-run's top, trail the head by 24 px until it turns down at 176, then from x 154 Right+A held 8 and
    Right: the arc clears the tiles and the toad slides down the right wall into the portal."""
    tu, hu = Unwrap(), Unwrap()
    def rd():
        r = emu.ram_all(); t = toad(r); h = head(r)
        t["H"] = tu(t["h"], 62 if tu.prev is None else None)
        if h:
            h["H"] = hu(h["h"], 32 if hu.prev is None else None)
        return t, h, r
    for _ in range(300):                                     # beside the column until the head is well up
        t, h, r = rd()
        if h and h["H"] >= 120 and 101 <= t["x"] <= 106:
            break
        rec.step(("Right",) if t["x"] < 103 else ("Left",) if t["x"] > 105 else (), 1)
    kc = rec.f
    for _ in range(200):                                     # climb
        t, h, r = rd()
        if t["H"] >= 346:
            break
        k = rec.f - kc
        rec.step(("Left", "A") if (k // 4) % 2 else ("Right", "A"), 1)
    for _ in range(60):                                      # land on the 336-run
        t, h, r = rd()
        if t["z"] == 0 and t["H"] >= 340:
            break
        rec.step((), 1)
    log(f"room 2: on the 336-run at f{rec.f}: {t} head {h}")
    emu.save("L6_r2_onrun")
    rec.step((), 1)
    for _ in range(300):                                     # trail the head by 24 px until it turns down at 176
        t, h, r = rd()
        if h and h["x"] >= 176 and h["H"] < 326:
            break
        if h:
            rec.step(("Right",) if t["x"] < h["x"] - 28 else ("Left",) if t["x"] > h["x"] - 22 else (), 1)
        else:
            rec.step((), 1)
    for _ in range(60):
        t, h, r = rd()
        if t["x"] >= 154:                                   # knife-edge: (154, 8) from the script's own on-run state
            break
        rec.step(("Right",), 1)
    rec.step(("Right", "A"), 8)
    for _ in range(300):                                     # hold Right: the arc ends sliding down the wall into the portal
        t, h, r = rd()
        if (r[0x23], r[0x24]) == (0x0D, 0xE5) or t["lvl"] != 8:
            break
        rec.step(("Right",), 1)
    log(f"L6 WARP engaged at f{rec.f}: {t}")
    emu.save("L6_warp")
    # the warp card: the level byte reads 254/255 ~155 f later; mash Start until Intruder Excluder (level byte 7)
    # has loaded with the toad at (128,94), hp 47
    for _ in range(120):
        t, h, r = rd()
        if t["lvl"] == 7 and t["hp"] == 47 and t["x"] == 128:   # the toad is placed ~60 f after the level byte flips
            break
        rec.step(("Start",), 2); rec.step((), 18)
    rec.step((), 30)
    t, h, r = rd()
    log(f"Intruder Excluder at f{rec.f}: {t}")
    emu.save("L8_start")


if __name__ == "__main__":
    emu = BizHawk(log_name="l6.log")
    t0 = time.time()
    rec = run(emu)
    t = toad(emu.ram_all())
    emu.close()
    print("segment", rec.f, "frames, end", t, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L6a.json").write_text(json.dumps({
        "bookmark": "L6_start", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "KARNATH'S LAIR room 1: three snakes, their heads pause at corners and lift you; the exit is a ledge "
                "three screens up, reached with a double jump off the third snake's head.||" f"{rec.f} frames"}))
    tokens.mark("L6 room 1 segment", {"frames": rec.f, "hp": t["hp"], "lives": t["lives"]})

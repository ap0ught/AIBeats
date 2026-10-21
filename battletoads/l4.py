"""Level 4, Arctic Caverns: a scripted policy from the tunnel's end (bookmark L3t_end).

Recipe (measured): wait 30 frames, dash (the icicles fall behind you); hop the ice step at x 360; the ice ball
rolls down at you - punch it within 34 px to STOP it, step within 10 px, B lifts it, walk to x 538 (the slope
stops you) and B throws it (speed 241) into the checkpoint barrier at x 640. Jump the ball rolling back (50 px).
On the platform, the snowball pile (0x3b) at x 784: face left, B throws a snowball that kills the snowman (0x33).
Drop off the platform's left end, run right along the floor, drop again: floor 2, same snowman/pile pair.

    python l4.py   -> logs/pbeam_L4a.json (segment for assemble.py), bookmark L4_seg_end
"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens


def find(r, idv, near=None):
    best = None
    for s in range(2, 15):
        if r[0x3C1 + s] == idv:
            d = dict(s=s, x=r[0x3FD + s] + 256 * r[0x3EE + s], h=r[0x439 + s], st=r[0x4B1 + s], hp=r[0x51A + s], spd=r[0x565 + s])
            if near is None or best is None or abs(d["h"] - near) < abs(best["h"] - near):
                best = d
    return best


def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], hp=r[0x51A], spd=r[0x565],
                cam=r[0x87] + 256 * r[0x88], lvl=r[0x10], lives=r[0x11], anim=r[0x3B5])


class Rec:
    def __init__(self, emu):
        self.emu, self.inputs, self.f = emu, [], 0

    def step(self, btn=(), n=1):
        self.inputs += ["+".join(btn)] * n
        self.f += n
        return self.emu.step(btn, n)

    def until(self, cond, btn=(), limit=600):
        for _ in range(limit):
            r = self.emu.ram_all()
            if cond(r):
                return True
            self.step(btn, 1)
        return False


def run(emu, bookmark="L3t_end", explore=800, log=print):
    emu.load(bookmark)
    rec = Rec(emu)
    # the level-clear cutscene: mash Start until level 4 loads, then wait for control (the toad starts to slide)
    while toad(emu.ram_all())["lvl"] != 4:
        rec.step(("Start",), 2); rec.step((), 18)
    rec.until(lambda r: toad(r)["x"] == 32 and toad(r)["z"] == 0 and 0 < toad(r)["h"] <= 143, (), 600)
    log(f"control at f{rec.f}: {toad(emu.ram_all())}")
    rec.step((), 30)
    rec.step(("Right",), 1); rec.step((), 1)                                   # dash past the icicles
    rec.until(lambda r: toad(r)["x"] >= 360 and toad(r)["st"] == 0, ("Right",))
    log(f"  at the step f{rec.f}: {toad(emu.ram_all())}")
    rec.step(("Right", "A"), 20); rec.step(("Right",), 20)                     # hop the ice step
    log(f"  after the hop f{rec.f}: {toad(emu.ram_all())} ball {find(emu.ram_all(), 0x38)}")
    # the ball: stop it, lift it, carry it up, throw it at the barrier
    # let the ball come down to the flat: a ball stopped on the slope rolls back before it can be lifted
    rec.until(lambda r: toad(r)["x"] >= 445, ("Right",), 100)                  # the ice slides you on to ~490
    rec.until(lambda r: (b := find(r, 0x38)) and b["h"] <= 44 and 0 < b["x"] - toad(r)["x"] <= 34, (), 300)
    log(f"  ball in reach at f{rec.f}: toad {toad(emu.ram_all())} ball {find(emu.ram_all(), 0x38)}")
    rec.step(("B",), 2); rec.step((), 12)
    log(f"  after the stop punch f{rec.f}: toad {toad(emu.ram_all())} ball {find(emu.ram_all(), 0x38)}")
    rec.until(lambda r: find(r, 0x38)["x"] - toad(r)["x"] <= 10, ("Right",), 60)
    rec.step((), 3); rec.step(("B",), 2); rec.step((), 10)
    log(f"  after the lift f{rec.f}: toad {toad(emu.ram_all())} anim {emu.ram_all()[0x3B5]} ball {find(emu.ram_all(), 0x38)}")
    rec.until(lambda r: toad(r)["x"] >= 538, ("Right",), 150)
    log(f"  throw at f{rec.f}: toad {toad(emu.ram_all())} ball {find(emu.ram_all(), 0x38)}")
    rec.step(("B",), 2)
    rec.until(lambda r: (w := find(r, 0x3c)) is not None and w["hp"] == 0, (), 90)     # it despawns offscreen: check hp
    log(f"barrier down at f{rec.f}: {toad(emu.ram_all())}")
    # dash on; jump the ball rolling back
    prev, jumped = None, False
    for _ in range(600):
        r = emu.ram_all(); t = toad(r); b = find(r, 0x38)
        if t["x"] >= 750 and t["h"] >= 150 and t["z"] == 0:
            break
        if b and prev is not None and b["x"] < prev and b["x"] > t["x"] and b["x"] - t["x"] <= 50 and not jumped and t["st"] == 0 and t["z"] == 0:
            log(f"  jump the ball at f{rec.f}: dx {b['x'] - t['x']} ball h {b['h']} toad {t}")
            rec.step(("Right", "A"), 20); jumped = True; prev = None; continue
        if t["st"] == 64 and not jumped:
            log(f"  HIT by the ball at f{rec.f}: {t} ball {b}")
            jumped = True
        prev = b["x"] if b else None
        rec.step(("Right",), 1)
    log(f"platform at f{rec.f}: {toad(emu.ram_all())}")
    # snowman 1 from the pile
    rec.until(lambda r: abs(find(r, 0x3b, near=toad(r)["h"])["x"] - toad(r)["x"]) <= 12, ("Left",), 60)
    rec.step(("Left",), 1); rec.step((), 2); rec.step(("B",), 2)
    rec.until(lambda r: (s := find(r, 0x33, near=toad(r)["h"])) is None or s["hp"] == 0, (), 120)
    # down: off the platform's left end, right along the floor, down again
    rec.until(lambda r: toad(r)["h"] < 140, ("Left",), 300)
    rec.until(lambda r: toad(r)["h"] >= 200 and toad(r)["z"] == 0, ("Right",), 400)
    log(f"floor 2 at f{rec.f}: {toad(emu.ram_all())}")
    rec.until(lambda r: abs(find(r, 0x3b, near=toad(r)["h"])["x"] - toad(r)["x"]) <= 12, ("Left",), 60)
    rec.step(("Left",), 1); rec.step((), 2); rec.step(("B",), 2)
    rec.until(lambda r: (s := find(r, 0x33, near=toad(r)["h"])) is None or s["hp"] == 0, (), 120)
    log(f"snowman 2 at f{rec.f}: {toad(emu.ram_all())}")

    # the descent to checkpoint 2: floor 2 -> (left) ledge h126 -> (right) floor h30 -> (left) pit h222 -> (right)
    # slope up to the block's floor h62. The bouncing ice ball (0x38, HP 143) crosses every floor: jump it.
    def go(direction, done, limit=500, label="", dodge=True):
        for _ in range(limit):
            r = emu.ram_all(); t = toad(r); b = find(r, 0x38, near=t["h"])
            if done(t):
                break
            if dodge and b and abs(b["h"] - t["h"]) <= 40 and t["st"] == 0 and t["z"] == 0 and 0 < (b["x"] - t["x"]) * (1 if direction == "Right" else -1) <= 70                     and abs(b["spd"]) > 0:
                log(f"  jump the ball at f{rec.f} ({label}): toad {t['x']},{t['h']} ball {b['x']},{b['h']}")
                rec.step((direction, "A"), 18); continue
            rec.step((direction,), 1)
        log(f"  {label}: f{rec.f} {toad(emu.ram_all())}")
    go("Left", lambda t: t["h"] == 126 and t["z"] == 0, 400, "ledge")
    go("Right", lambda t: t["h"] == 30 and t["z"] == 0, 400, "floor")
    rec.step((), 10)                                        # let the bouncing ball pass: leaving at once walks into it
    go("Left", lambda t: t["h"] == 222 and t["z"] == 0, 400, "pit", dodge=False)
    go("Right", lambda t: t["h"] == 62 and t["z"] == 0 and t["x"] >= 790, 500, "block floor")
    # the block breaks the snowball stack (0x3c, HP 31) by itself; dodge it until then, then leave left
    for _ in range(900):
        r = emu.ram_all(); t = toad(r); b = find(r, 0x38, near=62); w = find(r, 0x3c)
        if w is not None and w["hp"] == 0:
            break
        if b and b["h"] == 62 and t["st"] == 0 and t["z"] == 0 and 0 < t["x"] - b["x"] <= 80:
            rec.step(("A",), 18); continue
        rec.step((), 1)
    log(f"barrier 2 down at f{rec.f}: {toad(emu.ram_all())}")
    go("Left", lambda t: t["x"] <= 560, 600, "past the stack")
    # the bowl: a snowman at x 304 (two punches), then from the slope top (x <= 258) a jump with Right held lands
    # on the lip of the ramp that leads up and out
    for _ in range(600):
        r = emu.ram_all(); t = toad(r); sm = find(r, 0x33, near=t["h"])
        if sm is not None and sm["hp"] == 0:
            break
        if sm is None:
            rec.step(("Left",), 1); continue
        dx = sm["x"] - t["x"]
        if abs(dx) > 30:
            rec.step(("Left",) if dx < 0 else ("Right",), 1)
        elif t["st"] == 0:
            rec.step(("Left" if dx < 0 else "Right", "B"), 2); rec.step((), 14)
        else:
            rec.step((), 1)
    log(f"snowman 3 at f{rec.f}: {toad(emu.ram_all())}")
    rec.until(lambda r: toad(r)["x"] <= 256, ("Left",), 400)
    rec.step((), 12)
    rec.step(("Right", "A"), 30)
    rec.until(lambda r: toad(r)["z"] == 0 and toad(r)["h"] > 150, ("Right",), 60)
    log(f"on the ramp at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_ramp2")
    # the climb past the bouncing snowballs: inputs found by l4s.py from this exact state
    climb = PROJECT / "knowledge" / "l4s_L4_ramp2.json"
    if climb.exists():
        rec.step((), 2)
        for s in json.loads(climb.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"climb done at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_climbed")
    # checkpoint 3: a snowball stack (0x3c, HP 31) on the left ledge. Stand right of the dead snowman's pile at
    # x 540 and throw left (Left held WITH B; on ice the slide flips your facing otherwise): 8 damage per hit,
    # every other throw connects. Then the searched landing on the ledge's tip.
    rec.until(lambda r: toad(r)["x"] >= 540 and toad(r)["z"] == 0, ("Right",), 400)
    for _ in range(12):
        w = find(emu.ram_all(), 0x3c)
        if w is None or w["hp"] == 0:
            break
        rec.step(("Left", "B"), 2); rec.step((), 40)
    log(f"barrier 3 down at f{rec.f}: {toad(emu.ram_all())}")
    rec.step((), 30)
    land = PROJECT / "knowledge" / "l4s_L4_cp3_open2.json"
    if land.exists():
        for s in json.loads(land.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"on the ledge at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_cp3_ledge")
    pillar = PROJECT / "knowledge" / "l4s_L4_cp3_ledge.json"       # over the ice pillar (a trap object spawns behind it)
    if pillar.exists():
        rec.step((), 2)                                          # the search idles 2 frames after loading its bookmark
        for s in json.loads(pillar.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"past the pillar at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_past_pillar")
    # checkpoint 4: the toad slides down the zig-zag shaft by itself (a 4-frame A press at frame 160 dodges the
    # bouncing block) onto the 158 ledge; stop the block, lift it, throw it right from x 190 and keep holding Right
    # (the throw's momentum carries the toad past the wall at x 223 to x 264). There the snowman at the bottom-left
    # throws snowballs over the toad's head into the barrier (8 damage each); the searched tail dodges the block.
    rec.step((), 2)
    for f in range(620):
        t = toad(emu.ram_all())
        if t["h"] == 158 and t["z"] == 0 and 128 <= t["x"] <= 230:
            break
        rec.step(("A",) if 160 <= f < 164 else (), 1)
    log(f"on the 158 ledge at f{rec.f}: {toad(emu.ram_all())}")
    rec.step((), 1)
    for f in range(600):
        r = emu.ram_all(); t = toad(r); b = find(r, 0x38)
        if b and b["h"] == 158 and 0 < abs(b["x"] - t["x"]) <= 34 and t["st"] == 0:
            rec.step(("Right" if b["x"] > t["x"] else "Left", "B"), 2); rec.step((), 12)
            break
        rec.step((), 1)
    for f in range(60):
        r = emu.ram_all(); b = find(r, 0x38); t = toad(r)
        if b and abs(b["x"] - t["x"]) <= 10:
            break
        rec.step(("Right",) if b and b["x"] > t["x"] else ("Left",), 1)
    rec.step((), 3); rec.step(("B",), 2); rec.step((), 20)
    log(f"lifted the block at f{rec.f}: {toad(emu.ram_all())} block {find(emu.ram_all(), 0x38)}")
    rec.step((), 1)
    rec.until(lambda r: toad(r)["x"] >= 190, ("Right",), 200)
    rec.step(("Right", "B"), 2); rec.step(("Right",), 120)
    log(f"past the 223 wall at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_past223b")
    tail = PROJECT / "knowledge" / "l4s_L4_past223.json"
    if tail.exists():
        rec.step((), 2)
        for s in json.loads(tail.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"barrier 4 down at f{rec.f}: {toad(emu.ram_all())} wall {find(emu.ram_all(), 0x3c)}")
        emu.save("L4_cp4_done")
    past = PROJECT / "knowledge" / "l4s_L4_past223_solved.json"   # past the loose block on the ramp beyond the barrier
    if past.exists():
        rec.step((), 2)
        for s in json.loads(past.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"past the block at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_past_block")
    # the floating platform over the spike pit (period ~290 f, peak at f 230): crouch through the snowball that
    # arrives at f 144-190 (it flies at h 168; a crouching toad is under it, a jumping one leaves the platform),
    # then jump right at f 222 from the peak to land on the right ledge at (609, 158) - and stop there
    rec.step((), 2)
    for f in range(250):
        if 150 <= f < 195:
            btn = ("Down",)
        elif 222 <= f < 238:
            btn = ("Right", "A")
        elif 238 <= f < 246:
            btn = ("Right",)
        else:
            btn = ()
        rec.step(btn, 1)
    log(f"on the right ledge at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_ledge_right")
    # the ledge is an icy ramp down to a spike cluster under a hanging icicle (top at h 208, reaches ~155): a
    # short hop from its end (x 722, A for 2 frames) stays under the icicle, clears the spikes and drops down a
    # shaft at x 799 to the floor ~130 px below
    rec.step((), 1)
    rec.until(lambda r: toad(r)["x"] >= 722, ("Right",), 200)
    rec.step(("Right", "A"), 2)
    for f in range(120):
        t = toad(emu.ram_all())
        if f > 6 and t["z"] == 0 and t["h"] < 140:
            break
        rec.step(("Right",), 1)
    log(f"down the shaft at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_shaft2")
    # the icicle above x 784 drops the moment the toad steps under it: bait it with one Left frame, step back
    rec.step((), 1); rec.step(("Left",), 1); rec.step(("Right",), 1); rec.step((), 24)
    log(f"icicle baited at f{rec.f}: {toad(emu.ram_all())} icicles {[o for o in [find(emu.ram_all(), 0x39)] if o]}")
    emu.save("L4_baited")
    pillars = PROJECT / "knowledge" / "l4s_L4_baited.json"        # hops over the pillar row between the snowballs
    if pillars.exists():
        rec.step((), 2)
        for s in json.loads(pillars.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"past the pillars at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_past_pillars")
    sm5 = PROJECT / "knowledge" / "l4s_L4_past_pillars.json"      # the ledge snowman at x 512: one headbutt
    if sm5.exists():
        rec.step((), 2)
        for s in json.loads(sm5.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"ledge snowman dead at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_sm5_dead")
    hop2 = PROJECT / "knowledge" / "l4s_L4_sm5_dead.json"         # over the pillar at x 468 to the second snowman
    if hop2.exists():
        rec.step((), 2)
        for s in json.loads(hop2.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"at the second snowman at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_at_sm6")
    sm6 = PROJECT / "knowledge" / "l4s_L4_sm5_dead_solved.json"   # the second ledge snowman (x 244): one headbutt
    if sm6.exists():
        rec.step((), 2)
        for s in json.loads(sm6.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"second snowman dead at f{rec.f}: {toad(emu.ram_all())} wall {find(emu.ram_all(), 0x3c)}")
        emu.save("L4_sm6_dead")
    # checkpoint 5: the barrier (0x3c at 188,214) takes four snowballs thrown Left+B from the dead snowman at 244
    rec.step((), 1)
    rec.until(lambda r: toad(r)["x"] <= 254, ("Left",), 60)
    rec.step((), 4)
    for _ in range(6):
        w = find(emu.ram_all(), 0x3c)
        if w is None or w["hp"] == 0:
            break
        rec.step(("Left", "B"), 2); rec.step((), 40)
    log(f"barrier 5 down at f{rec.f}: {toad(emu.ram_all())} wall {find(emu.ram_all(), 0x3c)}")
    emu.save("L4_cp5_done")
    desc = PROJECT / "knowledge" / "l4s_L4_cp5_done.json"         # down the ramp to the bottom-left corner (33,46)
    if desc.exists():
        rec.step((), 2)
        for s in json.loads(desc.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"bottom-left corner at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_corner6")
    # CP6 (journal 006): a new ice ball rolls down the zigzag shaft 30 frames behind the toad and can't be outrun.
    # Walk Right down the second leg to its bowl (x 115), wait, punch-stop the ball as it arrives (<=34 px), lift it
    # 20 f later (the stun lasts ~40 f), carry it Left to the leg-3 corner (32,143), slide Right down to the floor
    # (h 94) and throw it Right off the floor's end into the spike pit: nothing across the pit needs it. The pit:
    # floating platform 1 (0x3e, h 104) shuttles 205..360 at 1 px/f - hop on from x ~176 as it heads back left past
    # 215; crouch (Down) under the hanging spike 0x43 at x 288, which scrapes a standing rider off; then the
    # searched hop to platform 2 (h 136, shuttles 398..548).
    rec.until(lambda r: toad(r)["x"] >= 110, ("Right",), limit=200)
    rec.step((), 2)

    def ball_close(r):
        t, b = toad(r), find(r, 0x38)
        return bool(b) and abs(((b["h"] - t["h"] + 128) % 256) - 128) <= 24 and 0 < abs(b["x"] - t["x"]) <= 34 and t["st"] == 0 and t["z"] == 0
    if rec.until(ball_close, (), limit=400):
        b, t = find(emu.ram_all(), 0x38), toad(emu.ram_all())
        rec.step(("Right" if b["x"] > t["x"] else "Left", "B"), 2); rec.step((), 12)
    log(f"ball 6 stopped at f{rec.f}: {find(emu.ram_all(), 0x38)} toad {toad(emu.ram_all())}")
    emu.save("L4_cp6_stop")
    rec.step((), 1); rec.step(("Right",), 20); rec.step(("B",), 2)      # lift (carry anims 11/13, then 16-18)
    rec.step(("Left",), 120)                                            # carry it down to (32,143)
    rec.until(lambda r: toad(r)["x"] >= 150, ("Right",), limit=300)     # slide down leg 4 and along the floor
    for _ in range(40):                                                 # settle on the ice: oppose the slide until x holds
        x0 = toad(emu.ram_all())["x"]; rec.step((), 1); x1 = toad(emu.ram_all())["x"]
        if x1 == x0:
            break
        rec.step(("Left",) if x1 > x0 else ("Right",), 1)
    rec.step(("Right", "B"), 2)                                         # throw: the ball flies off the floor's end
    rec.until(lambda r: find(r, 0x38) is None, (), limit=200)
    log(f"ball 6 disposed at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_cp6_free")
    last = [None]
    for _ in range(400):                                                # platform 1 heading back left past 215
        r = emu.ram_all(); t = toad(r); p = find(r, 0x3e, near=104)
        if p and last[0] is not None and p["x"] < last[0] and p["x"] <= 215:
            break
        last[0] = p and p["x"]
        rec.step(("Right",) if t["x"] < 174 else ("Left",) if t["x"] > 178 else (), 1)
    rec.step(("Right", "A"), 6); rec.step(("Right",), 4)
    rec.until(lambda r: toad(r)["st"] & 16, (), limit=60)
    log(f"on platform 1 at f{rec.f}: {toad(emu.ram_all())} p1 {find(emu.ram_all(), 0x3e, near=104)}")
    emu.save("L4_cp6_onp1")
    rec.step((), 66); rec.step(("Down",), 40)                          # ride; crouch under the hanging spike
    emu.save("L4_cp6_p1_past")
    hop = PROJECT / "knowledge" / "l4s_L4_cp6_p1_past.json"           # the hop to platform 2 near the platforms' meeting
    if hop.exists():
        rec.step((), 2)
        for s in json.loads(hop.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        t = toad(emu.ram_all())
        log(f"platform 2 hop at f{rec.f}: {t} {'OK' if t['st'] & 16 and t['h'] >= 130 else 'MISSED'}")
        emu.save("L4_cp6_onp2")
        # the line ends mid-punch (inputs are ignored for 19 frames); at platform 2's right end jump Right onto the
        # top of the ice pillar (h 190) that stands on the ledge (h 158) beyond the gap
        rec.step((), 19); rec.step(("Right", "A"), 14)
        rec.until(lambda r: toad(r)["z"] == 0 and not (toad(r)["st"] & 16) and toad(r)["h"] > 145, ("Right",), limit=40)
        t = toad(emu.ram_all())
        log(f"pillar top at f{rec.f}: {t} {'OK' if t['h'] == 190 else 'MISSED'}")
        emu.save("L4_cp6_pillar")
        spiky = PROJECT / "knowledge" / "l4s_L4_cp6_pillar.json"     # past the spiky ball patrolling the ledge
        if spiky.exists():
            rec.step((), 2)
            for s in json.loads(spiky.read_text()):
                rec.step(tuple(b for b in s.split("+") if b), 1)
            log(f"past the spiky ball at f{rec.f}: {toad(emu.ram_all())}")
            emu.save("L4_cp6_past_spiky")
            # the upper ledge ends at the level's right wall (x 799): drop off its end onto the lower ledge (h 62,
            # its own pillar at x~650 and a faster spiky ball) and run it LEFT - a switchback
            lower = PROJECT / "knowledge" / "l4s_L4_cp6_best_end.json"
            if lower.exists():
                rec.step((), 2)
                for s in json.loads(lower.read_text()):
                    rec.step(tuple(b for b in s.split("+") if b), 1)
                log(f"lower ledge run at f{rec.f}: {toad(emu.ram_all())}")
                emu.save("L4_cp6_lower")
                # ledge 3 (h 222, a third spiky ball) runs right to a pillar at x 745; the search ends on its top,
                # from where the toad slides off the level's right wall down a slope into the bottom bowl
                l3 = PROJECT / "knowledge" / "l4s_L4_cp6_lower.json"
                if l3.exists():
                    rec.step((), 2)
                    for s in json.loads(l3.read_text()):
                        rec.step(tuple(b for b in s.split("+") if b), 1)
                    log(f"ledge 3 pillar at f{rec.f}: {toad(emu.ram_all())}")
                    rec.until(lambda r: toad(r)["z"] > 0, (), limit=40)    # slide off the pillar (icy)...
                    rec.until(lambda r: toad(r)["z"] == 0, (), limit=80)   # ...and land at (799,143), the slope's top
                    log(f"bottom slope at f{rec.f}: {toad(emu.ram_all())}")
                    emu.save("L4_cp6_bottom")
                    cp6_bowl(emu, rec, log)
    return rec


def cp7_stack(emu, rec, log):
    """CP7 = a short snowball stack (0x3c at 672,150, HP 79) at the right end of an icy ledge (h 126). Two snowmen
    shoot at the toad from the left once it stands near the stack: an unkillable one at x 440 fires fast snowballs
    (0x3a, spd 3) rightward at h 149 every ~32-41 f - each passes THROUGH the stack for 8 damage and would hit a
    standing toad, but flies over a crouching one; the big snowman at 328 throws rightward at h 130 (spd 4), which
    hits even a crouching toad - hop those (A 2 frames) when they are 36-48 px away. ~10 shots empty the stack."""
    hops = 0; arrived = False
    for _ in range(2000):
        r = emu.ram_all(); t = toad(r); w = find(r, 0x3c)
        if w is None or w["hp"] == 0:
            break
        balls = [(r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s], r[0x565 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x3a]
        low = [b for b in balls if 120 <= b[1] <= 138 and b[2] == 4 and 36 <= t["x"] - b[0] <= 48]
        high_near = [b for b in balls if 140 <= b[1] <= 158 and b[2] == 3 and 0 <= t["x"] - b[0] <= 70]
        if low and t["z"] == 0:
            rec.step(("A",), 2); hops += 1; continue
        arrived = arrived or t["x"] >= 655
        if not arrived and not high_near and t["z"] == 0:
            rec.step(("Right",), 1); continue                            # bring the stack on screen (cam >= 416)
        rec.step(("Down",) if t["z"] == 0 else (), 1)
    log(f"barrier 7 down at f{rec.f}: {toad(emu.ram_all())} wall {find(emu.ram_all(), 0x3c)} hops {hops}")
    emu.save("L4_cp7_done")
    warp_platform(emu, rec, log)


def warp_platform(emu, rec, log):
    """The Level 4 -> 6 warp ("Mega Warp, advance 2 levels"). Past the broken stack the ledge slopes down onto the
    falling platform (ID 0x35 at 768,96): it sinks under the toad (h 96 -> ... wrapping past 0), the portal (0x22)
    appears at (776,152) once it is low enough (its HP byte is a countdown, but it stays after reaching 0), and
    jumping on the platform pushes it back up; touch the portal -> routine pointer $E50D = warp engaged, the
    level byte reads 254/255 during the cutscene and 8 (Karnath's Lair) afterwards."""
    rec.until(lambda r: toad(r)["st"] & 16 and toad(r)["x"] >= 760, ("Right",), limit=200)
    log(f"on the falling platform at f{rec.f}: {toad(emu.ram_all())}")
    jumps = 0
    for _ in range(1200):
        r = emu.ram_all(); t = toad(r)
        if (r[0x23], r[0x24]) == (0x0D, 0xE5) or t["lvl"] != 4:
            break
        plat = find(r, 0x35); port = find(r, 0x22)
        if port and t["z"] == 0 and (t["st"] & 16):
            rec.step(("A",), 10); jumps += 1; continue
        px = plat["x"] if plat else t["x"]
        rec.step(("Right",) if t["x"] < px - 4 else ("Left",) if t["x"] > px + 4 else (), 1)
    log(f"WARP engaged at f{rec.f}: {toad(emu.ram_all())} jumps {jumps}")
    emu.save("L4_warp")
    # the warp cutscene: mash Start until Karnath's Lair (level byte 8) has loaded and the toad has control
    for _ in range(80):                                                  # the toad spawns at (120,30) with full hp 47
        t = toad(emu.ram_all())
        if t["lvl"] == 8 and t["hp"] == 47:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    rec.step((), 30)
    log(f"Karnath's Lair at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L6_start")


def cp6_bowl(emu, rec, log):
    """CP6 = a 255-HP snowball stack (0x3c at 392,118) at the left end of the bowl below the switchback, behind an
    ice pillar (x~436, top h 126). A spiky ball follows the toad down the slope and patrols the bowl 444<->796
    (turns at the pillar); an ice ball (0x38) oscillates in it. Walk Left to the pillar, hop straight up onto it
    when the spiky ball arrives, wait for the ice ball to come back left while the spiky ball is far right, drop
    off the pillar's right side, punch-stop the ball at <=24 px, lift it (taps: the floor is icy and short), walk
    Left to the pillar's face and throw Left: the ball bounces between pillar and stack and grinds its 255 HP down
    16 per bounce (~200 f) while the throw-hop leaves the toad on the pillar top, out of the spiky ball's lap."""
    CARRY = {11, 13, 16, 17, 18}
    def dh(a, b): return ((a - b + 128) % 256) - 128
    def spiky_near(r):
        t, sp = toad(r), find(r, 0x40)
        return sp and t["z"] == 0 and abs(sp["x"] - t["x"]) <= 44 and abs(dh(sp["h"], t["h"])) <= 20
    for _ in range(600):                                                 # Left to the pillar, hop the spiky ball
        r = emu.ram_all(); t = toad(r)
        if spiky_near(r):
            rec.step(("A",), 16); continue
        if t["x"] <= 440 and t["h"] == 126:
            break
        rec.step(("Left",) if t["x"] > 440 else (), 1)
    log(f"pillar top at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L4_cp6_block")
    last = None
    for _ in range(4000):                                                # ice ball coming back left, spiky far right
        r = emu.ram_all(); b = find(r, 0x38); sp = find(r, 0x40)
        if b and last is not None and b["x"] < last and b["x"] <= 540 and sp and sp["x"] > 640:
            break
        last = b and b["x"]; rec.step((), 1)
    rec.step(("Right",), 4)                                              # off the pillar's right side
    rec.until(lambda r: toad(r)["z"] == 0 and toad(r)["h"] != 126, (), limit=40)
    stopped = False
    for _ in range(300):                                                 # a punch at <=20 px stops AND lifts the ball
        r = emu.ram_all(); t = toad(r); b = find(r, 0x38)
        if b and 0 < abs(b["x"] - t["x"]) <= 20 and abs(dh(b["h"], t["h"])) <= 24 and t["z"] == 0:
            rec.step(("Right" if b["x"] > t["x"] else "Left", "B"), 2); rec.step((), 12)
            b2 = find(emu.ram_all(), 0x38); stopped = bool(b2) and b2["spd"] == 0
            break
        rec.step((), 1)
    log(f"ball 7 punch at f{rec.f}: stopped {stopped} {find(emu.ram_all(), 0x38)} toad {toad(emu.ram_all())}")
    # the ball is pulled in over ~20 frames (anim 13/11 -> 17, ball at h+34); an extra B here would throw it
    rec.until(lambda r: (lambda t, b: t["anim"] in (16, 17, 18) and b and b["x"] == t["x"] and 30 <= (b["h"] - t["h"]) % 256 <= 40)(toad(r), find(r, 0x38)), (), limit=40)
    log(f"ball 7 carried at f{rec.f}: {toad(emu.ram_all())} ball {find(emu.ram_all(), 0x38)}")
    rec.step(("Left",), 4)                                               # turn to face the stack (throws go toward facing)
    rec.step(("Left", "B"), 2)
    log(f"ball 7 thrown at f{rec.f}: {toad(emu.ram_all())}")
    rec.until(lambda r: (lambda w: w is None or w["hp"] == 0)(find(r, 0x3c)), (), limit=400)
    log(f"barrier 6 down at f{rec.f}: {toad(emu.ram_all())} wall {find(emu.ram_all(), 0x3c)} ball {find(emu.ram_all(), 0x38)}")
    emu.save("L4_cp6_done")
    left2 = PROJECT / "knowledge" / "l4s_L4_cp6_done.json"             # past the second pillar and its spiky ball
    if left2.exists():
        rec.step((), 2)
        for s in json.loads(left2.read_text()):
            rec.step(tuple(b for b in s.split("+") if b), 1)
        log(f"past pillar 2 at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_cp6_left2")
        # pillar 3 (x~170) ends the floor; left of it a column of urchins (x~100-110, up to h~100). From the
        # pillar top a Left+A held 14 clears it (shorter/longer holds land in it) and drops into the far-left
        # shaft onto a long down-right slope (landing ~(47,0)); a snowman above throws snowballs down it
        rec.until(lambda r: toad(r)["x"] <= 181 and toad(r)["spd"] == 0, ("Left",), limit=60)
        rec.step(("A",), 16)
        rec.step((), 6); rec.until(lambda r: toad(r)["z"] == 0, (), limit=40)
        log(f"pillar 3 top at f{rec.f}: {toad(emu.ram_all())}")
        rec.step(("Left", "A"), 14)
        rec.step(("Left",), 9); rec.until(lambda r: toad(r)["z"] == 0, ("Left",), limit=80)
        log(f"shaft landing at f{rec.f}: {toad(emu.ram_all())}")
        emu.save("L4_cp7_shaft")
        slope = PROJECT / "knowledge" / "l4s_L4_cp7_shaft.json"        # down the snowball slope
        if not slope.exists():
            slope = PROJECT / "knowledge" / "l4s_L4_cp7_jump14.json"   # (same line searched from the probe's bookmark)
        if slope.exists():
            rec.step((), 2)
            for s in json.loads(slope.read_text()):
                rec.step(tuple(b for b in s.split("+") if b), 1)
            log(f"down the slope at f{rec.f}: {toad(emu.ram_all())}")
            emu.save("L4_cp7_slope")
            # the slope lands on a small ice ledge (x 230-350, h 126) over spikes with a big snowman (0x33, HP 31)
            # that throws left; more small ledges lead right under a hanging icicle
            plats = PROJECT / "knowledge" / "l4s_L4_cp7_slope.json"
            if plats.exists():
                rec.step((), 2)
                for s in json.loads(plats.read_text()):
                    rec.step(tuple(b for b in s.split("+") if b), 1)
                log(f"across the ledges at f{rec.f}: {toad(emu.ram_all())}")
                emu.save("L4_cp7_plats")
                cp7_stack(emu, rec, log)


if __name__ == "__main__":
    emu = BizHawk(log_name="l4.log")
    rec = run(emu)
    t = toad(emu.ram_all())
    emu.save("L4_seg_end")
    emu.close()
    print("segment", rec.f, "frames, end", t)
    (LOGS_DIR / "pbeam_L4a.json").write_text(json.dumps({
        "bookmark": "L3t_end", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "ARCTIC CAVERNS: stop the ice ball with a punch, lift it, carry it up the slope, throw it through the barrier; snowballs from the pile kill the snowmen.||"
                f"{rec.f} frames"}))
    tokens.mark("L4 segment A (barrier + two snowmen)", {"frames": rec.f, "hp": t["hp"]})

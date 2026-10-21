"""Check contra/stages/s3_model.py against the emulator, frame by frame, on random jumps up the waterfall.

    python tools/s3_verify_model.py [state=dbg/s3_pre] [jumps=80] [seed=1] [--inv]

--inv pokes the new-life invincibility timer every frame (DEBUG; physics are untouched) so that enemies do not end
the test. Prints the first mismatch of (X, Y, sub, A) per jump, and the per-jump scroll totals.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402
from contra.stages.s3_model import Map, St, air_frame, jump_start  # noqa: E402

args = sys.argv[1:]
inv = "--inv" in args
if inv:
    args.remove("--inv")
pokey = "--pokey" in args          # DEBUG: after the A frame, set Y and $94 to random values (tests the scroll phase)
if pokey:
    args.remove("--pokey")
state = args[0] if args else "dbg/s3_pre"
njump = int(args[1]) if len(args) > 1 else 80
seed = int(args[2]) if len(args) > 2 else 1
rng = random.Random(seed)
mp = Map()


def A_of(r):
    return r.screen * 240 + r.scroll


with Game(log_name="s3_verify.log") as g:
    r = g.load(state)
    while not (r.pstate == 1 and not r.airborne):
        r = g.step(())
    print("standing", r.desc(), "A", A_of(r))
    bad = 0
    done = 0
    safe = g.snap()
    while done < njump:
        if inv:
            g.e.poke(0xAE, 100)
        # walk a little at random, then jump
        for _ in range(rng.choice((0, 0, 1, 3, 8, 20))):
            d = rng.choice(("Right", "Left"))
            if inv:
                g.e.poke(0xAE, 100)
            r = g.step((d,))
            if r.airborne or r.dead:
                break
        if r.dead or r.y > 215:
            print("dead/fell: reload")
            r = g.restore(safe)
            continue
        if r.airborne:
            # walked off a ledge: let it land, not part of the test
            while r.airborne and not r.dead:
                if inv:
                    g.e.poke(0xAE, 100)
                r = g.step(())
            continue
        first = rng.choice(((), ("Right",), ("Left",), ("Right",), ("Right",)))
        s = St(r.x, r.y, r.sub, A_of(r))
        if inv:
            g.e.poke(0xAE, 100)
        r = g.step(first + ("A",))
        if not (r.jump & 15):
            continue                                   # lost press
        if pokey:
            ny, nsub = rng.randrange(56, 112), rng.randrange(256)
            g.e.poke(0x31A, ny)
            g.e.poke(0x94, nsub)
            s = St(r.x, ny, nsub, A_of(r))
        jump_start(s)
        mode = rng.choice(("right", "left", "wiggle", "wiggle", "random", "none"))
        cur = first
        k = 0
        S0 = s.A
        ok = True
        dirs = ""
        while True:
            k += 1
            if mode == "right":
                cur = ("Right",)
            elif mode == "left":
                cur = ("Left",)
            elif mode == "none":
                cur = cur if k < 12 else rng.choice(((), ("Right",), ("Left",)))
            elif mode == "wiggle":
                if rng.random() < 0.3:
                    cur = rng.choice((("Right",), ("Left",)))
            else:
                if rng.random() < 0.15:
                    cur = rng.choice((("Right",), ("Left",), ()))
            if inv:
                g.e.poke(0xAE, 100)
            pj = r.jump
            r = g.step(cur)
            # effective direction: what the game latched (bits $20 right / $40 left of the jump status)
            js = r.jump if r.jump else None
            padb = r.pad
            if padb & 2:
                d = -1
            elif padb & 1:
                d = 1
            else:
                d = 1 if pj & 0x20 else (-1 if pj & 0x40 else 0)
            dirs += "R" if d > 0 else ("L" if d < 0 else ".")
            landed = air_frame(s, d, mp)
            if ok and (s.X, s.Y, s.sub, s.A) != (r.x, r.y, r.sub, A_of(r)):
                print(f"  MISMATCH jump {done} frame {k}: model {s} emu x={r.x} y={r.y} sub={r.sub:02x} A={A_of(r)} "
                      f"jump={r.jump:02x} pad={r.pad:02x} mode={mode}")
                ok = False
                bad += 1
            if landed != (not r.airborne):
                if ok:
                    print(f"  LANDING MISMATCH jump {done} frame {k}: model landed={landed} emu airborne={r.airborne} {s} {r.desc()}")
                    bad += 1
                    ok = False
            if not r.airborne or r.dead or k > 150:
                break
            if not ok:
                # resync the model to the emulator and go on
                while r.airborne and not r.dead:
                    r = g.step(cur)
                break
        done += 1
        print(f"jump {done:3d} {mode:6s} {'ok ' if ok else 'BAD'} frames {k + 1:3d} scroll {A_of(r) - S0:3d} -> {r.desc()} A={A_of(r)} row {(r.y + 16 - A_of(r)) // 16} {dirs}")
        if not r.dead and not r.airborne and r.y < 200 and done % 5 == 0:
            g.free(safe)
            safe = g.snap()
    print("mismatching jumps:", bad, "of", done)

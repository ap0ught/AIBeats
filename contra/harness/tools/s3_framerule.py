"""Measure the dragon's timers against the frame the boss scroll starts (DEBUG: Bill is kept alive by poking the
new-life invincibility timer; nothing here is part of a run).

    python tools/s3_framerule.py <state on the top floor> [delays=0,1,2,3,4,5,6,7,8,9] [--fire]

For each delay d: wait d frames, jump (A), then stand still. Prints the row of: scroll start, scroll end, palette
fade end, hands appear, arm extension complete, mouth open, mouth closed, second opening; and the frame counter
at the scroll start. --fire: also fire straight up all the time (to see what lag does to the count).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

args = sys.argv[1:]
fire = "--fire" in args
if fire:
    args.remove("--fire")
state = args[0]
delays = [int(x) for x in (args[1] if len(args) > 1 else "0,1,2,3,4,5,6,7,8,9").split(",")]
with Game(log_name="s3_framerule.log") as g:
    for d in delays:
        r = g.load(state)
        ev = {}
        prev = r
        lag = 0
        for i in range(1250):
            g.e.poke(0xAE, 100)
            want = set()
            if i == d or i == d + 1:
                want.add("A")
            if fire and i > d + 90:
                want.add("Up")
                p = g.pad
                if p.down["B"]:
                    if p.t - p.start["B"] < 2:
                        want.add("B")
                elif p.can_press("B"):
                    want.add("B")
            r = g.step(want)
            lag += r.lagged
            m, pm = r.m, prev.m
            if m[0x75] and not pm[0x75] and "scroll" not in ev:
                ev["scroll"] = i
                ev["fc"] = m[0x1A]
            if m[0x84] and not pm[0x84]:
                ev["scroll_end"] = i
            if "scroll_end" in ev and not m[0x74] and pm[0x74]:
                ev.setdefault("fade_end", i)
            for s in range(16):
                if m[0x4B8 + s] and m[0x528 + s] == 0x15 and m[0x578 + s] < 0xF0 and "hands" not in ev:
                    ev["hands"] = i
                if m[0x528 + s] == 0x15 and m[0x578 + s] < 0xF0 and m[0x4B8 + s] == 4 and pm[0x4B8 + s] == 3:
                    ev.setdefault("arms_out", i)
                if m[0x4B8 + s] and m[0x528 + s] == 0x14:
                    op = m[0x578 + s] < 0xF0 and not (m[0x598 + s] & 0x80)
                    was = pm[0x578 + s] < 0xF0 and not (pm[0x598 + s] & 0x80)
                    if op and not was:
                        ev.setdefault("open1" if "open1" not in ev else "open2", i)
                    if was and not op:
                        ev.setdefault("close1", i)
            prev = r
            if "open2" in ev:
                break
        rel = {k: (v - ev["scroll"] if k not in ("fc", "scroll") else v) for k, v in ev.items()}
        print(f"delay {d}: {rel} lag {lag}", flush=True)

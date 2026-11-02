"""Clock proofs: RAM vs PPU OAM vs screenshots at START and END (knowledge/clock.md).

    python tools/clock_evidence.py start      power-on with logs/intro_fastest.inputs.txt (fresh launch), frames
                                             around the first $33 == $97 frame N: OAM sprites + screenshots
    python tools/clock_evidence.py end <state>   from a 6-5 state after the demon's HP display reached 0
                                             (default ref4751/21_6-5_boss0): every frame until 12 frames after
                                             the first $63 == 0 frame P; HUD timer crops in shots/clock/
Writes knowledge/clock_evidence.json.
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, KNOWLEDGE_DIR, SHOTS_DIR  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

HUD_TIMER_BOX = (16, 23, 104, 32)   # "TIMER-nnn" in a 256x240 screenshot (row 2 of the status bar)


def visible_sprites(e):
    o = e.oam()
    return [(o[i + 3], o[i], o[i + 1]) for i in range(4, 256, 4) if o[i] < 0xEF]   # sprite 0 = the status-bar split


def start():
    rows = read_inputs(Path(__file__).resolve().parent.parent / "logs" / "intro_fastest.inputs.txt")
    e = BizHawk(log_name="clock_start.log")
    out = []
    try:
        e.tick(TICKS)
        e.run(rows[:-6])
        for k in range(10):
            s = e.step((), 1)
            p = e.screenshot(f"clock/start_{s.frame}")
            out.append({"frame": s.frame, "ctl": s.ctl, "gm": s.gm, "timer": s.timer, "subtimer": s.subtimer,
                        "oam_sprites": len(visible_sprites(e)), "shot": p.name})
            print(out[-1], flush=True)
    finally:
        e.close()
    n = next(r["frame"] for r in out if r["ctl"] == 0x97)
    drawn = next(r["frame"] for r in out if r["oam_sprites"])
    return {"N_first_ctl97": n, "first_frame_with_sprites": drawn, "offset": drawn - n, "frames": out}


def end(state):
    e = BizHawk(log_name="clock_end.log")
    out = []
    try:
        e.tick(TICKS)
        e.load(state)
        p_frame = None
        for k in range(3000):
            s = e.step((), 1)
            rec = {"frame": s.frame, "stage": s.stage, "timer": s.timer, "bosshp": s.bosshp, "stk": s.stk, "lagged": s.lagged}
            if s.timer <= 3 or p_frame:
                shot = e.screenshot(f"clock/end_{s.frame}")
                Image.open(shot).crop(HUD_TIMER_BOX).resize((416, 40)).save(SHOTS_DIR / "clock" / f"end_timer_{s.frame}.png")
                rec["shot"] = shot.name
                out.append(rec)
            if s.timer == 0 and p_frame is None:
                p_frame = s.frame
            if p_frame and s.frame >= p_frame + 12:
                break
        print("\n".join(str(r) for r in out))
    finally:
        e.close()
    return {"P_first_timer0": p_frame, "frames": out}


if __name__ == "__main__":
    what = sys.argv[1]
    p = KNOWLEDGE_DIR / "clock_evidence.json"
    j = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if what == "start":
        j["start"] = start()
    else:
        j["end"] = end(sys.argv[2] if len(sys.argv) > 2 else "ref4751/21_6-5_boss0")
    p.write_text(json.dumps(j, indent=1), encoding="utf-8")

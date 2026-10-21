"""Clock END evidence: on which frame does Bill "revert to his normal position" after the heart dies, in RAM,
in the PPU's sprite memory and in the picture - with Up held, Down held, nothing held, and Up held while airborne?

    python tools/clock_end_evidence.py <stage-8 state> <seg.json with the stage-8 rows> [tag]

The state is one frame before stage 8's first playable frame; the rows are a fitted stage 8 (tools/repair.py).
The rows are replayed up to 60 frames before BOSS_DEFEATED_FLAG ($3B) is set; from there four variants are played:
the fitted rows until the flag is set, then  U: Up held   D: Down held   N: nothing   J: Up held, and a jump timed
so that Bill is in the air when control is lost.  For the frames around A (first frame with $2C == 9) each variant
records RAM, the PPU OAM's sprite tiles in Bill's box, and a screenshot (shots/clock_end/<tag>_<variant>_f<frame>.png).
Writes logs/clock_end_evidence_<tag>.json.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra import clock  # noqa: E402
from contra.emulator import BizHawk, LOGS_DIR, SHOTS_DIR  # noqa: E402

state, segp = sys.argv[1], Path(sys.argv[2])
tag = sys.argv[3] if len(sys.argv) > 3 else "s8"
rows = [tuple(x for x in r.split("+") if x) for r in json.loads(segp.read_text(encoding="utf-8"))["rows"]]
F = dict(clock.FIELDS)
F.update({"x": 0x334, "y": 0x31A, "delay": 0x2A, "sprattr": 0x34E, "fc": 0x1A, "flip": 0xD8})
(SHOTS_DIR / "clock_end").mkdir(parents=True, exist_ok=True)


def box_tiles(oam: bytes, x: int, y: int):
    """Sprite tiles the PPU has inside Bill's box, as sorted (dx, dy, tile, attr)."""
    out = []
    for i in range(0, 256, 4):
        sy, tile, attr, sx = oam[i:i + 4]
        if sy >= 0xEF:
            continue
        dx, dy = sx - x, sy - y
        if -20 <= dx <= 20 and -40 <= dy <= 10:
            out.append((dx, dy, tile, attr & 0xE3))
    return sorted(out)


def crop_hash(png: Path, x: int, y: int):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    top = 8 if im.size[1] == 224 else 0
    box = (max(0, x - 20), max(0, y - 40 - top), min(256, x + 20), min(im.size[1], y + 10 - top))
    return hashlib.sha1(im.crop(box).tobytes()).hexdigest()[:10]


out = {"state": state, "rows": str(segp), "variants": {}}
with BizHawk(log_name="clock_end.log", fields=F) as e:
    e.load(state)
    e.trace(True)
    e.run(rows)
    tr = e.last_trace
    b = next(i for i, s in enumerate(tr) if s["bossdef"] == 1 and s["level"] == 7)      # row index where the flag reads 1
    a0 = next(i for i, s in enumerate(tr) if s["lroutine"] == 9 and s["level"] == 7)
    print(f"fitted rows: $3B = 1 after row {b} (frame {tr[b]['frame']}); $2C = 9 after row {a0} (frame {tr[a0]['frame']}); "
          f"{a0 - b} frames between")
    out["fitted"] = {"bossdef_row": b, "bossdef_frame": tr[b]["frame"], "A_row": a0, "A_frame": tr[a0]["frame"]}
    e.trace(False)
    e.load(state)
    e.run(rows[:b - 60])
    e.save("dbg/clock_end_base")
    for var in ("U", "D", "N", "J"):
        hold = {"U": ("Up",), "D": ("Down",), "N": (), "J": ("Up",)}[var]
        tail = list(rows[b - 60:b + 1]) + [hold] * 900
        if var == "J":
            # a jump so that Bill is airborne on frame A (A is (a0 - b) rows after the flag); a jump lasts ~45 frames
            j = (b + 1 - (b - 60)) + (a0 - b) - 20
            for k in range(j, j + 3):
                tail[k] = hold + ("A",)
        e.load("dbg/clock_end_base")
        e.trace(True)
        e.run(tail[:61 + (a0 - b) - 6])
        pre = e.last_trace
        e.trace(False)
        frames = []
        a_seen = None
        for k in range(70 if var == "J" else 16):
            s = e.step(tail[len(pre) + k], 1)
            f = s["frame"]
            png = e.screenshot(f"clock_end/{tag}_{var}_f{f}")
            oam = e.oam()
            buf = e.ram(0x200, 256)
            rec = {k2: s[k2] for k2 in ("frame", "lroutine", "elr", "bossdef", "delay", "pad", "pseq", "aim", "jump", "psprite",
                                        "spr0", "x", "y", "lagged")}
            rec["oam_box"] = hashlib.sha1(repr(box_tiles(oam, s["x"], s["y"])).encode()).hexdigest()[:10]
            rec["oam_tiles"] = [t[2] for t in box_tiles(oam, s["x"], s["y"])]
            rec["buf_box"] = hashlib.sha1(repr(box_tiles(buf, s["x"], s["y"])).encode()).hexdigest()[:10]
            rec["picture_box"] = crop_hash(png, s["x"], s["y"])
            rec["screenshot"] = png.name
            frames.append(rec)
        full = pre + [dict(r) for r in frames]
        en = clock.end_frame([dict(s, groutine=5, demo=0, level=7) for s in full])
        A = next(r["frame"] for r in frames if r["lroutine"] == 9)
        # first frame whose PPU sprite box / picture box differs from the frame before, at or after A
        chg_oam = next((frames[i]["frame"] for i in range(1, len(frames)) if frames[i]["frame"] >= A and frames[i]["oam_box"] != frames[i - 1]["oam_box"]), None)
        chg_pic = next((frames[i]["frame"] for i in range(1, len(frames)) if frames[i]["frame"] >= A and frames[i]["picture_box"] != frames[i - 1]["picture_box"]), None)
        chg_ram = next((frames[i]["frame"] for i in range(1, len(frames)) if frames[i]["frame"] >= A and (frames[i]["pseq"], frames[i]["psprite"]) != (frames[i - 1]["pseq"], frames[i - 1]["psprite"])), None)
        out["variants"][var] = {"held": "+".join(hold), "A_first_frame_2C_is_9": A, "clock_end_frame": en,
                                "first_change_of_pose_in_RAM_from_A": chg_ram, "first_change_in_PPU_OAM_from_A": chg_oam,
                                "first_change_in_picture_from_A": chg_pic, "frames": frames}
        print(f"--- {var} (held: {'+'.join(hold) or 'nothing'}): A = {A}; clock.end_frame = {en}")
        print(f"    first change from A: pose in RAM {chg_ram}, PPU OAM {chg_oam}, picture {chg_pic}")
        for r in frames[:14] if var != "J" else frames:
            if var == "J" and not (A - 3 <= r["frame"] <= A + 3 or (en and en["ram"] - 3 <= r["frame"] <= en["ram"] + 3)):
                continue
            print(f"    f{r['frame']}: $2C={r['lroutine']} $2D={r['elr']} $3B={r['bossdef']:3d} $2A={r['delay']:3d} pad={r['pad']:3d} "
                  f"$BC={r['pseq']} $C2={r['aim']} $A0={r['jump']} $D6={r['psprite']:3d} $0300={r['spr0']:3d} y={r['y']} "
                  f"buf {r['buf_box']} oam {r['oam_box']} pic {r['picture_box']} lag={r['lagged']}")
(LOGS_DIR / f"clock_end_evidence_{tag}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

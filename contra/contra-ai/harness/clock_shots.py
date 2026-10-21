"""chain2 (carried from chain1): the two clock events on the REAL run, in RAM, in the PPU's sprite memory and in the picture.

    python clock_shots.py [run_chain2.inputs.txt]

Pass 1: replay from power-on with a trace, find N (START, RAM) and A / P (END, RAM) with contra/clock.py.
Pass 2: a second fresh emulator replays to just before each event and steps frame by frame, saving for every frame
around it a screenshot (shots/clock/start_f<frame>.png, end_f<frame>.png), the PPU OAM and the game's sprite
buffer ($0200). Writes clock_evidence.json. The claims checked:
    the medals are first in the picture on frame N + 1 (not on N);
    Bill's standing pose is first in the picture on frame P + 1 (not on P).
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from contra import clock  # noqa: E402
from contra.emulator import BizHawk, SHOTS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402

F = dict(clock.FIELDS)
F.update({"x": 0x334, "y": 0x31A, "delay": 0x2A, "fc": 0x1A, "lives": 0x32, "death": 0xB4, "weapon": 0xAA})


def medals(buf: bytes):
    return [{"slot": i // 4, "x": buf[i + 3], "attr": buf[i + 2]} for i in range(0, 256, 4)
            if buf[i + 1] == 0x0A and buf[i] == 0x10]


def blue_pixels(png: Path):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    w, h = im.size
    sx, sy = w / 256.0, h / (240.0 if h >= 240 else 224.0)
    top = 0 if h >= 240 else 8
    crop = im.crop((int(16 * sx), int((17 - top) * sy), int(68 * sx), int((33 - top) * sy)))
    return sum(1 for p in crop.getdata() if p[2] > 150 and p[0] < 120)


def box_tiles(oam: bytes, x: int, y: int):
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


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "run_chain2.inputs.txt"
    rows = read_inputs(path)
    with BizHawk(log_name="chain/clock_shots_1.log", fields=F) as e:
        e.trace(True)
        e.run(rows)
        tr = e.last_trace
    m = clock.measure(tr)
    assert m["finished"], m
    N, A, P = m["start"]["ram"], m["end"]["control_lost"], m["end"]["ram"]
    print(f"pass 1: N = {N} (seen {m['start']['seen']}), A = {A}, P = {P} (seen {m['end']['seen']}); "
          f"time {m['time']} = {m['frames']} frames")
    out = {"inputs": str(path), "rows": len(rows), "clock": m, "start_frames": [], "end_frames": []}
    (SHOTS_DIR / "clock").mkdir(parents=True, exist_ok=True)
    with BizHawk(log_name="chain/clock_shots_2.log", fields=F) as e:
        # frame f is produced by rows[f - 2]; after running rows[:k] the emulator is on frame k + 1
        e.run(rows[:N - 5])
        assert e.state()["frame"] == N - 4
        for _ in range(9):
            f = e.state()["frame"] + 1
            s = e.step(rows[f - 2], 1)
            assert s["frame"] == f
            png = e.screenshot(f"clock/start_f{f}")
            oam, buf = e.oam(), e.ram(0x200, 256)
            rec = {"frame": f, "lroutine": s["lroutine"], "hud_6A": s["hud"], "lagged": s["lagged"],
                   "medals_in_ram_buffer_0200": len(medals(buf)), "medals_in_ppu_oam": len(medals(oam)),
                   "blue_pixels_in_hud_box": blue_pixels(png), "screenshot": png.name}
            out["start_frames"].append(rec)
            print("  START", rec)
        e.run(rows[N + 4:A - 6])
        assert e.state()["frame"] == A - 5, (e.state()["frame"], A)
        for _ in range(12):
            f = e.state()["frame"] + 1
            row = rows[f - 2] if f - 2 < len(rows) else ()
            s = e.step(row, 1)
            png = e.screenshot(f"clock/end_f{f}")
            oam, buf = e.oam(), e.ram(0x200, 256)
            rec = {"frame": f, "row": "+".join(row), "lroutine": s["lroutine"], "elr": s["elr"], "bossdef": s["bossdef"],
                   "pad_F1": s["pad"], "pseq_BC": s["pseq"], "aim_C2": s["aim"], "jump_A0": s["jump"],
                   "psprite_D6": s["psprite"], "spr_0300": s["spr0"], "x": s["x"], "y": s["y"], "lagged": s["lagged"],
                   "buffer_box": hashlib.sha1(repr(box_tiles(buf, s["x"], s["y"])).encode()).hexdigest()[:10],
                   "oam_box": hashlib.sha1(repr(box_tiles(oam, s["x"], s["y"])).encode()).hexdigest()[:10],
                   "oam_tiles": [t[2] for t in box_tiles(oam, s["x"], s["y"])],
                   "picture_box": crop_hash(png, s["x"], s["y"]), "screenshot": png.name}
            out["end_frames"].append(rec)
            print("  END", rec)
    sf = {r["frame"]: r for r in out["start_frames"]}
    ef = {r["frame"]: r for r in out["end_frames"]}
    first_medals_pic = next((r["frame"] for r in out["start_frames"] if r["medals_in_ppu_oam"] > 0), None)
    first_blue = next((r["frame"] for r in out["start_frames"]
                       if r["blue_pixels_in_hud_box"] > sf[N - 1]["blue_pixels_in_hud_box"] + 20), None)
    fr = out["end_frames"]
    chg_oam = next((fr[i]["frame"] for i in range(1, len(fr)) if fr[i]["frame"] > A and fr[i]["oam_box"] != fr[i - 1]["oam_box"]), None)
    chg_buf = next((fr[i]["frame"] for i in range(1, len(fr)) if fr[i]["frame"] > A and fr[i]["buffer_box"] != fr[i - 1]["buffer_box"]), None)
    out["summary"] = {
        "N": N, "medals_first_in_ppu_oam": first_medals_pic, "medals_first_in_picture_by_blue_pixels": first_blue,
        "start_ok": first_medals_pic == N + 1 and first_blue == N + 1,
        "A": A, "P": P, "pose_first_changes_in_ram_buffer_after_A": chg_buf, "pose_first_changes_in_ppu_oam_after_A": chg_oam,
        "end_ok": chg_buf == P and chg_oam == P + 1,
        "held_at_A": ef[A]["row"], "pad_at_A": ef[A]["pad_F1"],
        "frames_P_minus_N": P - N, "seconds": (P - N) / clock.NES_FPS, "time": clock.fmt((P - N) / clock.NES_FPS)}
    print(json.dumps(out["summary"], indent=1))
    p = HERE / "clock_evidence.json"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(out, indent=1), encoding="utf-8")
    tmp.replace(p)


if __name__ == "__main__":
    main()

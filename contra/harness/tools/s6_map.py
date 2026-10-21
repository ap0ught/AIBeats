"""DEBUG mapping tool (uses RAM pokes; never part of a run): fly through a stage and record

  * the background collision grid by world column (16-px cells),
  * every enemy the screen tables create (type, world x, y, attribute),
  * one screenshot per 128 px of scroll.

    python tools/s6_map.py <stage 6|7>

Method: from states/dbg/s<stage>_pre, every frame the new-life invincibility timer ($AE) is poked to $80 (nothing
attacks, nothing can touch Bill) and Bill's Y is poked to a fixed row so he never falls; Right is held. When the
scroll stalls (a solid wall 8 px ahead) the row is changed. Writes knowledge/s<stage>_map.json and
shots/s<stage>map/*.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s6lib import Sim, FIELDS, collision_columns, write_json  # noqa: E402

stage = int(sys.argv[1])
ROWS_Y = [0x44, 0x64, 0x84, 0xA4, 0x24, 0xC4]
grid = {}
enemies = []
seen = {}
with Sim(f"s{stage}_map") as sim:
    e = sim.e
    s = sim.load(f"dbg/s{stage}_pre")
    yi = 0
    last_cam, stall, shot_at = -1, 0, -1
    n = 0
    while n < 9000:
        e.poke(0xAE, 0x80)
        e.poke(0x31A, ROWS_Y[yi])
        e.poke(0xC6, 0)
        e.poke(0xC4, 0)
        f = sim.run([("Right",)])[-1]
        n += 1
        if f["lroutine"] != 4:
            continue
        cam = f.cam
        if cam == last_cam and f["x"] >= 0x80:
            stall += 1
            if stall > 6:
                yi = (yi + 1) % len(ROWS_Y)
                stall = 0
        else:
            stall = 0
        last_cam = cam
        for en in f.enemies():
            k = en["slot"]
            sig = (en["type"], en["attr"])
            if seen.get(k) != sig:
                seen[k] = sig
                enemies.append({"frame": n, "slot": k, "type": en["type"], "attr": en["attr"], "wx": cam + en["x"],
                                "y": en["y"], "hp": en["hp"], "state": en["state"], "cam": cam})
        for k in list(seen):
            if not f.get(f"er{k}", 0):
                del seen[k]
        if cam // 64 != shot_at:
            shot_at = cam // 64
            ram = e.ram_all()
            for (wc, row), code in collision_columns(ram).items():
                grid[(wc, row)] = code
            if cam % 128 < 64:
                e.screenshot(f"s{stage}map/cam{cam:05d}")
        if f["stop"] == 0xFF and f["auto"] == 0 and f["bossdone"]:
            ram = e.ram_all()
            for (wc, row), code in collision_columns(ram).items():
                grid[(wc, row)] = code
            e.screenshot(f"s{stage}map/cam{cam:05d}_boss")
            break
    print("frames", n, "final cam", last_cam)
maxc = max(wc for wc, _ in grid)
rows = []
for row in range(15):
    rows.append("".join(".=~#"[grid.get((wc, row), 0)] for wc in range(maxc + 1)))
write_json(Path(__file__).resolve().parent.parent / "knowledge" / f"s{stage}_map.json",
           {"_about": "16-px collision cells by world column (x = col*16), rows top to bottom (y = row*16); "
                      ". empty, = floor (one-way), ~ water, # solid. enemies = screen-table spawns seen while "
                      "flying through with pokes (debug). Made by tools/s6_map.py",
            "grid": rows, "enemies": enemies})
for sc in range(0, (maxc + 16) // 16):
    print(f"--- screen {sc} (world x {sc * 256})")
    for row in range(15):
        print(f"{row * 16:3d} " + rows[row][sc * 16:sc * 16 + 16])

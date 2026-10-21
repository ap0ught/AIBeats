"""DEBUG ONLY (uses RAM pokes; never part of a run): get from the start of stage 8 to the heart so the END clock
event can be studied.

    python tools/dbg_to_heart.py [max frames]

From states/dbg/s8_pre (made by tools/mk_stage_state.py 8): plays the first 560 frames of the Mars608 movie's
stage 8 (it crosses the opening pit), then a crude closed-loop bot: hold Right, tap B every other frame, aim
up-right and hop while the first boss (enemy type $10) is alive, jump when the scroll stalls. The barrier timer
($B0) is poked to $80 every frame so nothing can kill Bill. Saves:
    states/dbg/s8_heart_room.State    when the scroll has reached the last screen
    states/dbg/s8_heart_last.State    a few frames before the heart's HP reaches 0 (found by a second pass)
and logs/dbg_to_heart.json with the frame numbers.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402

MAXF = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
movie = read_inputs(LOGS_DIR / "tas_4623M_raw.inputs.txt")
head = movie[28798 - 1:28798 - 1 + 560]
F = {"level": 0x30, "lroutine": 0x2C, "bossdef": 0x3B, "screen": 0x64, "scroll": 0x65, "x": 0x334, "y": 0x31A,
     "pstate": 0x90, "death": 0xB4, "jump": 0xA0, "stop": 0x58, "autodone": 0x84}


def enemies(r):
    out = []
    for s in range(16):
        if r[0x4B8 + s] and r[0x528 + s] != 1:
            out.append({"slot": s, "type": r[0x528 + s], "hp": r[0x578 + s], "x": r[0x33E + s], "y": r[0x324 + s],
                        "state": r[0x598 + s], "routine": r[0x4B8 + s]})
    return out


log = {}
with BizHawk(log_name="dbg_to_heart.log", fields=F) as e:
    e.load("dbg/s8_pre")
    for r in head:
        e.poke(0xB0, 0x80)
        s = e.step(r, 1)
    i = len(head)
    last_prog, last_gain = -1, i
    rows = list(head)
    saved_room = False
    heart_seen = None
    while i < MAXF:
        e.poke(0xB0, 0x80)
        ram = e.ram_all()
        en = enemies(ram)
        boss1 = any(x["type"] == 0x10 for x in en)
        prog = ram[0x64] * 256 + ram[0x65]
        if prog > last_prog:
            last_prog, last_gain = prog, i
        btn = {"Right"}
        if i % 2 == 0:
            btn.add("B")
        if boss1:
            btn.add("Up")
            if i % 48 < 3:
                btn.add("A")
        elif i - last_gain > 60 and (i // 30) % 2 == 0 and i % 30 < 4:
            btn.add("A")                                   # stuck: hop
        if i - last_gain > 200 and (i // 16) % 4 == 3:
            btn.add("Up")                                  # stuck for long (a boss room): also spray upward
        s = e.step(tuple(btn), 1)
        rows.append(tuple(btn))
        i += 1
        if i % 300 == 0 or (s["bossdef"] and "bossdef" not in log):
            big = [(x["slot"], hex(x["type"]), x["hp"], x["x"], x["y"], hex(x["state"])) for x in en if x["hp"] > 8]
            print(f"i={i} frame {s['frame']} screen {s['screen']}.{s['scroll']} x={s['x']} y={s['y']} pstate {s['pstate']} "
                  f"bossdef {s['bossdef']} lroutine {s['lroutine']} stop {s['stop']} big enemies {big}", flush=True)
        if not saved_room and i - last_gain > 150 and ram[0x64] >= 4:
            e.save("dbg/s8_heart_room")
            saved_room = True
            log["heart_room_i"] = i
            print("saved dbg/s8_heart_room at i", i, "enemies", [(hex(x['type']), x['hp'], x['x'], x['y']) for x in en], flush=True)
        if s["bossdef"] and "bossdef" not in log:
            log["bossdef"] = {"i": i, "frame": s["frame"]}
        if s["lroutine"] == 9 and "lr9" not in log:
            log["lr9"] = {"i": i, "frame": s["frame"]}
            break
        if s["level"] != 7:
            break
    log["rows"] = len(rows)
    print(log)
    (LOGS_DIR / "dbg_to_heart.rows.json").write_text(json.dumps(["+".join(r) for r in rows]), encoding="utf-8")
    if "bossdef" in log:
        # second pass: the same rows (same pokes) up to 40 frames before the heart dies, then save
        e.load("dbg/s8_pre")
        cut = log["bossdef"]["i"] - 40
        for r in rows[:cut]:
            e.poke(0xB0, 0x80)
            s = e.step(r, 1)
        e.save("dbg/s8_heart_last")
        log["heart_last"] = {"i": cut, "frame": s["frame"]}
        print("saved dbg/s8_heart_last at frame", s["frame"])
(LOGS_DIR / "dbg_to_heart.json").write_text(json.dumps(log, indent=1), encoding="utf-8")

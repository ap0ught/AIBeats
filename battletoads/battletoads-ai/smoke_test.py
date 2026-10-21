"""Day one, minute one: power the game on with the camera rolling, press Start, see what happens.

Records video/day1_first_boot.mkv (plus logs/day1_first_boot.{inputs,events,trace}.txt for the panel),
takes a screenshot every second, saves bookmarks at the title screen and after Start, and dumps the
whole 2 KB of RAM at each so the memory hunt has something to diff.
"""
import shutil
import sys
import time

from toads.emulator import BizHawk, SHOTS_DIR, LOGS_DIR
from toads import tokens

name = sys.argv[1] if len(sys.argv) > 1 else "day1_first_boot"
out = SHOTS_DIR / name
out.mkdir(parents=True, exist_ok=True)
t0 = time.time()
emu = BizHawk(log_name=f"{name}.log", record=name, fields={})
emu.note("POWER ON. The bridge knows nothing: no addresses, no map, no rules.||Watching what the game does on its own.")
k = 0


def shot(tag):
    global k
    shutil.copyfile(emu.screenshot("_tmp"), out / f"{k:03d}_{tag}.png")
    k += 1


for i in range(10):                 # ten seconds of attract / title
    emu.wait(60)
    shot(f"boot{i}")
(LOGS_DIR / f"{name}.ram_title.bin").write_bytes(emu.ram_all())
emu.save("day1_title")
emu.note("Pressing START.||No idea yet what Start does here; the first thing to learn is what changes in memory.")
for i in range(4):
    emu.press("Start", hold=4, release=56)
    shot(f"start{i}")
(LOGS_DIR / f"{name}.ram_after_start.bin").write_bytes(emu.ram_all())
emu.save("day1_after_start")
emu.note("Holding RIGHT for ten seconds.||If a byte climbs steadily, that is probably an X coordinate.")
for i in range(10):
    emu.step("Right", 60)
    shot(f"right{i}")
(LOGS_DIR / f"{name}.ram_after_right.bin").write_bytes(emu.ram_all())
emu.save("day1_after_right")
emu.note("Pressing A repeatedly.||Jump? Attack? Memory will say.")
for i in range(6):
    emu.press("A", hold=6, release=54)
    shot(f"a{i}")
emu.note("Doing nothing for ten seconds.||What kills a toad that stands still?")
for i in range(10):
    emu.wait(60)
    shot(f"idle{i}")
(LOGS_DIR / f"{name}.ram_end.bin").write_bytes(emu.ram_all())
emu.save("day1_end")
print("frames stepped:", len(emu.inputs), f"{time.time() - t0:.0f}s wall")
emu.close()
print(tokens.mark("first boot recorded", {"frames": len(emu.inputs)}))

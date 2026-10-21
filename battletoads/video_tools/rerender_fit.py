"""pieces re-rendered at the lengths the narration gives them"""
from sections import *
from gridshot import grid_frames
from sections import _grid_lead
if 0: p_slam_over("s05_slam", "DAY 1: POWER ON", cam_frames(V / "day1_first_arena.mkv", 6.0, 4.5, (128, 112), drift=0.1), dur=2.7, sub="September 26")
if 0: p_slam_over("s06_slam", "GOAL ONE: JUST BEAT IT", game_frames("capwip", 2200, 6.0), dur=4.3)
if 0: p_slam_over("s07_slam", "GOAL TWO: SHAVE SECONDS", game_frames("cap14", 2200, 6.0), dur=3.1,
            colors=((200, 255, 140), (40, 160, 30), (10, 50, 10)))
w, m = Writer(CLIPS / "s06_fails.mp4"), audio.Mix(10)
for im in grid_frames("grid_tower", lead=_grid_lead("grid_tower"), a0=0, a1=410, speed=1, survivor_tile=5,
                      cols=4, rows_=3, header="THE TOWER: ONE INPUT CHANGED PER ATTEMPT", fail_label="FELL", fail_count="FELL"):
    w.put(im)
for k in range(6):
    m.add_sfx(4.5 + k * 0.35, "crash", 0.25)
print("fails", done(w, m, "s06_fails"))

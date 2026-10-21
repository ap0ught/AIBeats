"""the section slams at their fitted lengths: no calendar date, titles sized to stay on screen"""
from sections import *
p_slam_over("s05_slam", "DAY 1: POWER ON", cam_frames(V / "day1_first_arena.mkv", 6.0, 4.5, (128, 112), drift=0.1), dur=2.7, size=130)
p_slam_over("s06_slam", "GOAL ONE: JUST BEAT IT", game_frames("capwip", 2200, 6.0), dur=4.3, size=118)
p_slam_over("s07_slam", "GOAL TWO: SHAVE SECONDS", game_frames("cap14", 2200, 6.0), dur=3.1, size=110,
            colors=((200, 255, 140), (40, 160, 30), (10, 50, 10)))
for t in ("GOAL ONE: JUST BEAT IT", "GOAL TWO: SHAVE SECONDS"):
    print(t, logo(t, 118 if "ONE" in t else 110).width, "px wide (screen 1920)")

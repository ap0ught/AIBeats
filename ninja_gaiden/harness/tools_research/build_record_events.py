"""Build knowledge/record_events.json from the measured video frames (work/vid) and the TAS RAM log (work/tasrun).
Frame numbers are VIDEO frame indices of dl/record_video/v1890225973.mp4 (frame n = time n/60 s)."""
import json, numpy as np, pathlib
P = pathlib.Path(r"G:\AI World Record\Ninja Gaiden")
V = P / "work" / "vid"
K = 60.0988 / 60.0
segs = np.load(V / "segs.npy").tolist()
START, END = 1707, 43238
def cum(f): return {"cum_f": f - START, "cum_s": round((f - START) / 60, 3), "cum_nes": round((f - START) * K, 1)}
stage_seg = {'1-1':0,'1-2':1,'2-1':2,'2-2':6,'2-3':9,'3-1':11,'3-2':12,'3-3':13,'4-1':15,'4-2':19,'4-3':20,'4-4':24,'5-1':25,
             '5-2':26,'5-3':30,'5-4':37,'6-1':39,'6-2':40,'6-3':45,'6-4a':49,'6-4b':50,'6-5':51}
timer_vis = {'1-1':1711,'1-2':4017,'2-1':4857,'2-2':7757,'2-3':10853,'3-1':11685,'3-2':13285,'3-3':15609,'4-1':16519,'4-2':18707,
             '4-3':21007,'4-4':23560,'5-1':24344,'5-2':26800,'5-3':29254,'5-4':32234,'6-1':33038,'6-2':34620,'6-3':37768,
             '6-4a':40676,'6-4b':41494,'6-5':42490}
bar_empty = {'1-2':4109,'2-3':10933,'3-3':15769,'4-4':23588,'5-4':32292,'6-4a':40744,'6-4b':41756,'6-5':42806}
timer_at_kill = {'1-2':148,'2-3':149,'3-3':147,'4-4':150,'5-4':149,'6-4a':148,'6-4b':146,'6-5':145}
tas = json.load(open(P / "work" / "tasrun" / "tas4751_stage_events.json"))
# substage rooms: every dark segment of exactly ~22 frames is an in-stage room change
order = list(stage_seg)
rooms = []
labels = {3:'2-1b',4:'2-1c',5:'2-1d',7:'2-2b',8:'2-2c',16:'4-1b',17:'4-1c',21:'4-3b',22:'4-3c',23:'4-3d',27:'5-2b',28:'5-2c',29:'5-2d',
          31:'5-3b',32:'5-3c',33:'5-3d',34:'5-3e',35:'5-3f',36:'5-3g',41:'6-2b',42:'6-2c',43:'6-2d',44:'6-2e',46:'6-3b',47:'6-3c',48:'6-3d'}
for i,(a,b) in enumerate(segs):
    if i in labels:
        rooms.append({"room": labels[i], "dark_first_f": a, "dark_last_f": b, "first_picture_f": b+1, "dark_len_f": b-a+1, **cum(b+1)})
stages = []
for n in order:
    a, b = segs[stage_seg[n]]
    e = {"stage": n, "black_before": [a, b], "first_picture_f": b+1, "timer_digits_first_f": timer_vis[n],
         "control_est_f": timer_vis[n]-6, **{"control_est_"+k: v for k, v in cum(timer_vis[n]-6).items()},
         "tas_control_nes": tas[n]["timer_running_first"]}
    if n in bar_empty:
        e["boss_bar_empty_f"] = bar_empty[n]; e.update({"boss_bar_empty_"+k: v for k, v in cum(bar_empty[n]).items()})
        e["hud_timer_at_bar_empty"] = timer_at_kill[n]; e["tas_boss_display_zero_nes"] = tas[n]["boss_display_zero"]
    stages.append(e)
TAS_START, TAS_END = 174, 39525
out = {
 "_about": "Frame-by-frame timing of the Ninja Gaiden (NES) Any% record: TheRetroRunner 11:32.183, speedrun.com run z5pwrgdm, Twitch VOD https://www.twitch.tv/videos/1890225973 (downloaded 1080p60 source, dl/record_video/v1890225973.mp4). All 'f' values are VIDEO frame indices (frame n = n/60 s). cum_* are from START. cum_nes = cum_f * 60.0988/60. See record_notes.md.",
 "video": {"file": "dl/record_video/v1890225973.mp4", "format": "1920x1080 h264, 86,340 frames, 1438.999 s",
   "container_fps": 60.0, "container_fps_evidence": "packet timestamps step 1530/1440 ticks of 1/90000 s (ms-rounded 1/60 s); 86,340 frames over 1,439.0 s; every frame-accurate seek (t=(n-0.5)/60) reproduced the sequential decode exactly (mean abs diff 0.00 at n=3980, 15000, 30001, 43230).",
   "content_rate": "30 distinct images per second. Each distinct image is ONE NES frame (no interlace comb: adjacent lines align at shift 0), shown for 2 video frames; the other NES frame of each pair is missing (scroll between distinct images = 3 NES px = 2 frames of running). Pair phase drifts (pairs start on odd frames at 3600, on even frames at 43238).",
   "game_area_px": {"x0": 600, "x1": 1800, "y0": 140, "y1": 1040, "note": "approx. Twitch chat lines are drawn over the top of the HUD; webcam at lower left; LiveSplit at upper left (attempt 1516/31808)."},
   "tolerance": "+/-1 video frame for start/end (events can fall on a missing NES frame, so the true NES event can be 1 NES frame earlier than seen)."},
 "claim": {"time_s": 692.183, "frames_at_60fps": 41531},
 "start": {"rule": "Timing starts when you gain control of Ryu.", "f": START, "t_s": round(START/60, 3),
   "detail": "1-1 playfield: black 1314-1602 (preceded by the TECMO PRESENTS 1989 screen ~1350-1560 and the previous attempt's reset), first picture 1603, fade complete ~1699. 1706 no Ryu; 1707 Ryu first visible at the left edge (pair 1707-1708). HUD TIMER digits are blank until 1711, where they appear already reading 149.",
   "tol_f": 1, "previous_attempt": "VOD starts mid-attempt (2-1 at 1:10); that attempt is reset around frame 1250 (blue screen, then TECMO PRESENTS)."},
 "end": {"rule": "Timing ends when the timer reaches 000 after defeating the demon statue.", "f": END, "t_s": round(END/60, 3),
   "detail": "6-5 demon: ENEMY bar empty at 42806 (HUD TIMER 145); timer tallies down by 2 every 6 video frames (odd values only seen); TIMER-001 shown 43232-43237, TIMER-000 first shown 43238. Screen goes black at 43264, ending cutscene follows.",
   "tol_f": 1},
 "span": {"video_frames": END-START, "seconds": round((END-START)/60, 4), "claimed_s": 692.183, "difference_frames": 0,
   "nes_frames_at_60_0988": round((END-START)*K, 1), "nes_frames_tolerance": 2,
   "note": "The moderators' number is exactly (first video frame with Ryu visible) to (first video frame showing TIMER-000), counted at 60 fps."},
 "stages": stages,
 "rooms_in_stage": rooms,
 "all_dark_segments": [{"first": a, "last": b, "len": b-a+1} for a, b in segs],
 "tas_4751_board_timed": {"start_ram_frame": TAS_START, "end_ram_frame": TAS_END, "frames": TAS_END-TAS_START,
   "seconds": round((TAS_END-TAS_START)/60.0988, 3),
   "note": "From the replay of 4751M in BizHawk 2.11.1 NesHawk (work/tasrun/tas4751_ram.csv): first frame $33==0x97 (control, Ryu moves next frame) to first frame $63==0 in stage $6D=21 after $66 reaches 0. The movie's last input frame is 39084 (demon display 0); the tally (147 s x 3 frames) continues without input."},
}
(P / "knowledge" / "record_events.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("ok", len(stages), len(rooms))

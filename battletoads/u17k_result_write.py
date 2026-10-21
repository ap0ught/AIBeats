"""Track K2: write knowledge/u17k_result.json (utf-8, temp file + rename)."""
import hashlib
import json
import os

from u17k_lib import rle_str

k7 = json.load(open("logs/pbeam_K7.json"))["inputs"]
k6 = json.load(open("logs/pbeam_K6.json"))["inputs"]
first = next(i for i in range(len(k7)) if k7[i] != k6[i])
res = {
    "verified": True,
    "segment": "K7",
    "inputs": len(k7),
    "frames_saved_vs_K6": len(k6) - len(k7),
    "entry_bookmark": "B4_end0",
    "l8_placement_frame": 12349,
    "l8_placement_frame_behind_L4c5": 12351,
    "k6_l8_placement_frame": {"behind_B4": 12353, "behind_L4c5": 12355},
    "parity": "saving 4 = even (K6 2467 -> K7 2463 inputs; placement 12353 -> 12349 behind B4, 12355 -> 12351 behind L4c5)",
    "end_bookmarks": {"power_on_replay_behind_B4": "K7_end0", "power_on_replay_behind_L4c5": "K7_end0_L4c5",
                      "bookmark_replay_from_B4_end0": "K7_end0b"},
    "K6_replays_from_B4_end0": ("yes: K6 from B4_end0 and from L4c5_end0 give the same RAM on every frame except frames 1, 2, 3, 5, 6 "
                                "(timer bytes), placement on input 2467 both times (logs/fix/u17k_trace_K6_*.sha)"),
    "verification": {
        "bookmark_replay": ("logs/fix/u17k_verify_K7.txt: one piece from B4_end0 AND from L4c5_end0: Level 8 placement on the last input "
                            "(2463), end state = K6 from the same bookmark (level 7, toad 128/3934, hp 47, lives 2, score 091600; the only "
                            "RAM byte that differs from the K6 end state is $1A, a timer); min hp 47 through the level"),
        "power_on": ("logs/fix/u17k_poweron_K7_B4.txt: INTRO + L1b L3u L3skipu B4 K7 replayed twice from power-on, RAM sha1 d1a87884 both "
                     "times, placement on frame 12349 = the last input. logs/fix/u17k_poweron_K7_L4c5.txt: the same behind L4c5, twice, "
                     "sha1 d1a87884, placement 12351"),
        "banned_presses": {"Start": 0, "Select": 0, "Left+Right": 0, "Up+Down": 0},
        "inputs_sha1": hashlib.sha1("\n".join(k7).encode()).hexdigest(),
        "first_input_differing_from_K6": first,
        "not_done": ("assemble.py was not run: no Level 8 segment is synced behind K7 yet (Level 8 starts 4 frames sooner than behind K6; "
                     "an even shift, so u16b_sync / u16a_sync8 apply as for K6). The power-on check is my own u17k_poweron.py (copy of "
                     "u16k_poweron.py, the INTRO of assemble.py, same stepping)."),
    },
    "line": ("K7 = K6[0:1473] + K6[1476:1508] (3 idle frames cut: the jump at the rising head of snake 3 starts on index 1505 instead of "
             "1508) + Right+A x20 + Right x42 (K6 43) + idle to 1725 + Left x2 + A x6 (K6 A x8) + idle to 1797 + Right, idle, Right+A x54 "
             "(capture in the exit hole on 1853, K6 1857) + idle (toad in room 2 on 1982, K6 1986) + the K6 warp-room inputs K6[1986:2252] "
             "+ idle x168 + page mash found by BFS over nothing/A/B: B on 2428, A on 2438, B on 2451, placement on 2463. "
             "Tail of K7 from 1473: " + rle_str(k7[1473:], 1473)),
    "mechanism": [
        ("WHAT A HEAD PAUSE IS (measured: logs/fix/u17k_ram_K6.bin): snake heads (object 0x4C) and tails (0x4D) draw / erase one "
         "background tile every 8 px of travel, on the frame they reach the first pixel of a new 8-px cell (moving up: H mod 8 = 2, down: "
         "0, left: x mod 8 = 6, right: 0). The camera scroll queues a tile row / column every 8 px too (RAM $94 changes = row, $93 = "
         "column). If the scroll queued one on the frame a head or tail has to draw, that object waits one frame ($EF = its object slot "
         "on that frame). The delayed draw of the head can in turn block the tail (no $EF then). Off-screen objects do not draw and are "
         "never blocked. It is not about the distance between toad and head: a toad falling 140 px below the head pauses it "
         "(logs/fix/u17k_ev_s2idle.txt, frames 605 / 610)."),
        ("RESONANCE: a camera that follows a jump moves about 1.6 px/f = one row every 5 frames; the head draws every 4 frames and loses "
         "one frame per hit, so once a row hits the head the next two rows hit it too (K6: 1539/1544/1549 and 329/334/339). Moving the "
         "jump by 1 frame mod 4 avoids all three."),
        ("THE NEXT SNAKE APPEARS THE FRAME AFTER THE TAIL OF THE PREVIOUS ONE IS GONE (K6: tail 1 gone 579 -> snake 2 on 580; tail 2 gone "
         "1203 -> snake 3 on 1204). The tail starts a fixed time after the head (174 frames snake 1, 154 snake 2) and has its OWN pauses. "
         "So for snakes 1 and 2 only TAIL pauses cost time (K6: 340, 349, 374 | 755, 776, 896-898, 903-904, 909-910, 1019, 1024, 1029, "
         "1185 = 3 + 13 frames; undisturbed tails are gone on 576 and 1190, i.e. snake 2 on 577 and snake 3 on 1191); head pauses of "
         "snakes 1 and 2 only matter through what they do to the tail. For snake 3 the HEAD pauses count (K6: 1211, 1539, 1544, 1549, "
         "1560-61, 1776, 1797)."),
        "Snake 1 starts on frame 120 whatever the toad does early (a dash to x 381 changes nothing); with the toad left at the spawn spot it starts on 1250.",
        ("The camera has memory: a 1-frame hop during the wait at (62, 7870) changes every later pause and breaks the open-loop line "
         "(u17k_shift.py). Phases can only be chained if the last approach of the toad to the waiting spot is unchanged."),
        ("Inputs while the toad is carried over the corner of snake 1 (indices about 341-351) do nothing at all; 185 valid single "
         "run-length mutations of the K6 room 1 between 255 and 410 all leave tail 1 gone on 579 (logs/fix/u17k_p1_a.txt, u17k_p1probe.py)."),
    ],
    "what_k7_changes": ("Only snake 3 from index 1473 on. Jump at the rising head 3 frames earlier and the Right hold 42: no head pause at "
                        "all up to the (112, 7984) corner, reached on 1704 instead of 1709 (the contact-free minimum track K measured). "
                        "Boarding the top run 4 frames earlier (Left on 1725), dash tap on 1797 (K6 1801): capture on 1853 instead of "
                        "1857, on the 2-frame grid of the exit. Two or three head pauses remain on the top run depending on the boarding; "
                        "about 45 boardings x 14 taps behind two pause-free jump lines all end on 1853 or 1855 (logs/fix/u17k_p3b_*.txt)."),
    "parity_trap": ("The page mash after the warp is NOT shift invariant: behind the first 1853 line (boarding A x8, tap 1796) the shortest "
                    "mash is 48 frames after the BFS root (segment 2464 = -3, odd; kept as logs/pbeam_K7.json.backup); behind boarding "
                    "A x6 / tap 1797 it is 47 (segment 2463 = -4, even). The level byte leaves 8 exactly 170 frames after the portal touch "
                    "in both. Always re-run the BFS (u17k_pick.py / u17k_build.py) after any room-1 change and check the parity of the "
                    "final length."),
    "not_done": ("About 19 more frames are still in room 1 by the same mechanism, none of them taken: (a) snake 1 tail pauses 340/349/374 "
                 "(3 frames: snake 2 on 577); (b) snake 2 tail pauses (13 frames: snake 3 on 1191), seven of them from the 160-px fall "
                 "onto the 7664 run (camera at 4 px/f, a row every 2 frames) - riding the descending body at x 208 down at 2 px/f "
                 "instead of falling, or re-timing the fall, is the idea to test; (c) the head of snake 3: 1211 (1 frame, from the jump "
                 "at 1180) and the top-run pauses (2 frames: capture 1851 or 1849). Every gain in (a)/(b) shifts all later inputs by the "
                 "same number of frames and needs the camera state at the two waiting spots to equal the K6 one. Any further saving must "
                 "keep the total even."),
    "downstream": ("Level 8 and everything behind it must be synced behind K7 exactly as for K6: entry bookmark states/K7_end0.State "
                   "(power-on replay behind B4; K7_end0_L4c5.State behind L4c5). RAM at the placement equals the K6 one except $1A. "
                   "Chain: L1b L3u L3skipu B4 K7 <Level 8 ...>."),
    "files": {
        "segment": "logs/pbeam_K7.json (2463 inputs, bookmark B4_end0; replays from L4c5_end0 too)",
        "scripts": ("u17k_lib.py, u17k_sim.py (snapshot simulator with head/tail pause tracking), u17k_ev.py (head + tail event list of "
                    "any script), u17k_trace.py, u17k_objs.py, u17k_ramdump.py, u17k_p1.py / u17k_p1probe.py (snake 1 mutations), "
                    "u17k_shift.py / u17k_shift2.py (shift tests), u17k_p3a.py (jump shift + hold sweep), u17k_p3b.py (boarding + dash tap "
                    "sweep), u17k_pick.py (page mash behind several room-1 variants), u17k_build.py, u17k_verify.py (bookmark replays, "
                    "writes the segment), u17k_poweron.py <segment> <B4|L4c5> [suffix]"),
        "logs": ("logs/fix/u17k_verify_K7.txt, u17k_poweron_K7_B4.txt, u17k_poweron_K7_L4c5.txt, u17k_p3a_1473.txt, u17k_p3a_1487.txt, "
                 "u17k_p3b_*.txt/.out, u17k_pick_B.txt, u17k_pick_B_21_6_1797.json (the chosen inputs), u17k_ev_*.txt, "
                 "u17k_trace_K6_*.txt"),
    },
    "notes": ("K7 verified from B4_end0, from L4c5_end0 and twice from power-on behind each (RAM sha1 d1a87884 all four times): Level 8 "
              "placement on frame 12349 behind B4 (K6 12353), 12351 behind L4c5 (K6 12355): 4 frames shorter than K6, an even shift, no "
              "Start, no Select, same end state (level 7, toad 128/3934, hp 47, lives 2, score 091600). Gain = the head of snake 3 is no "
              "longer paused by the camera rows of the toad's jump (5 pauses gone, 4 frames on the capture grid, page mash re-found). The "
              "premise of the task was partly wrong: pauses are not caused by the toad being near the head but by the camera scroll "
              "updates colliding with the snake's tile draws, and for snakes 1 and 2 it is the pauses of the TAIL that delay the next "
              "snake. About 19 frames remain (see not_done); stopped at the 2.5 h cap."),
    "status": "FINAL 2026-10-10 08:15",
}
p = "knowledge/u17k_result.json"
json.dump(res, open(p + ".tmp", "w", encoding="utf-8"), indent=1)
os.replace(p + ".tmp", p)
print("written", len(k7), first, res["verification"]["inputs_sha1"])
print(rle_str(k7[1473:], 1473))

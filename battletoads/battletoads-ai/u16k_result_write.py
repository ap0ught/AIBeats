"""Track K: write knowledge/u16k_result.json for the final K6 (= K6d).  Temp file + rename."""
import hashlib
import json
import os

res = json.load(open("knowledge/u16k_result.json"))
a = json.load(open("logs/pbeam_K6.json"))["inputs"]
b = json.load(open("logs/pbeam_K6d.json"))["inputs"]
res.update({
    "verified": True, "segment": "K6", "frames_saved": 128, "l8_placement_frame": 12355, "old_l8_placement_frame": 12483,
    "segment_len": 2467, "old_segment": "L6c", "old_segment_len": 2595, "bookmark": "L4c5_end0",
    "split": {"room_1": 36, "warp_room": 90, "warp_pages": 2, "total": 128},
    "status": "FINAL 2026-10-10 04:35",
})
res["verification"] = {
    "bookmark_replay": "logs/fix/u16k_build6c_K6d.txt (K6 is a byte copy of K6d): one-piece replay from L4c5_end0, Level 8 placement on the last input (2467), end state = L6c's (level 7, toad 128/3934, hp 47, lives 2, score 091600; only RAM $0B and $1A differ = timers); health 47 through the whole level",
    "power_on": "logs/fix/u16k_poweron_K6d.txt: INTRO + L1b L3u L3skipu L4c5 K6 replayed twice from power-on, RAM sha1 0f56db25 both times, Level 8 placement at frame 12355 (up14/up15h: 12483)",
    "banned_presses": {"Start": 0, "Left+Right": 0, "Up+Down": 0, "Select": 0},
    "K6_equals_K6d": a == b,
    "inputs_sha1": hashlib.sha1("\n".join(a).encode()).hexdigest(),
    "not_done": "assemble.py was not run (a route needs the re-fitted Levels 8-13 behind it); the power-on check is my own u16k_poweron.py with assemble.py's intro and the same stepping",
}
res["line"] = (
    "K6 = L6c[0:1576] + idle x154 (ride snake 3's 7984-run 10 px behind the head instead of walking up to it: the head never pauses), Left x2 (face the snake), "
    "A x8 (hop: grab the vertical body, come down on the head 7 frames after it turns onto the top run), idle x61 (ride), Right x1, idle x1, Right+A x54 (standstill dash jump, "
    "56 frames in the air, into the exit hole's capture zone at (369, 8099), index 1857), idle x223 (129 frames to room 2 + 94 in the warp room), Right x1, idle x1, Right+A x170 "
    "(warp room, portal touch at r+266, x 419), idle x180, A, idle x9, B, idle x12, A, idle x11. Indices are segment inputs; the warp room starts at index 1986 (L6c: 2022); r = frames since then.")
res["room1"] = [
    "HEAD PAUSES (the biggest lead left): a snake's head stops for single frames whenever the toad is in its way - clinging right under it, standing at or ahead of its coordinate, or flying close in front of it. "
    "With the toad kept 2+ px behind the coordinate (riding) or well below the head (clinging) it never pauses. L6c has 32 such single-frame pauses in room 1 (logs/fix/u16k_r1pauses_L6c.txt); "
    "K6 removes the six on snake 3's 7984-run by simply not walking up to the head (the head turns up at index 1708 instead of 1714).",
    "The room's exit is not a ledge to stand on but a capture zone: a toad that enters x >= ~366 at H ~8096..8130 (checked every 2 frames) freezes, and room 2 loads 129 frames later. "
    "L6c ran along the snake and jumped from x 272 (captured ~1893); K6 is captured at 1857.",
    "Snake 3's head carries a standing toad from about 30 px behind its coordinate to about 6 px ahead; further ahead it drops off.",
    "Boarding the top run: from the park spot (126, 7998) the toad must FACE the vertical body (Left x2) or A does not grab it; then a short hop (A x8) clings to the body at x 112 and lands on the head "
    "right at its coordinate just after the turn; the old A x32 hop landed 44 frames later with the head 80 px ahead.",
    "Dash jump from the head (tap Right, release, Right+A): 3 px/f, apex +73, A held to the end; it reaches the capture zone from x >= 199..203, i.e. when the head is at x ~196..200. "
    "Right, gap, Right on the head is a dash and runs off its front: walk with ONE hold only.",
    "Sweeps of the boarding (idle 22..36 x A 4..20) and of 0..12 walk frames all end on the same capture frame (2-frame grid).",
]
res["not_done"] = (
    "Room 1 before index 1576 is L6c's, unchanged. Remaining head pauses caused by the toad there (logs/fix/u16k_r1pauses_L6c.txt): snake 1 at 329/334/339 (toad clinging right under the head), "
    "snake 2 at 659, 664, 747-748, 814, 894, 899-900, 905-906, 911, 974, 1015, 1020, 1025, 1028, 1041 (each one also delays snake 3, released ~145 frames after snake 2's head enters its hole), "
    "snake 3 at 1539/1544/1549 (toad flying at the rising head; contact-free the head turns up at 1704, measured in u16k_r1ride2.py, but the lower run retracts under the toad at ~1550, "
    "so it has to cling BELOW the head instead). Up to ~20 more frames in room 1 if those rides are redone without touching the heads; every later input then has to be re-timed "
    "(open loop), as done here for the last 6. This is probably where the 2-player TAS's 5-13 frame lead on the third snake comes from.")
res["tried_and_dead"] = [t for t in res["tried_and_dead"] if "snake 3 is released a fixed" not in t and "capture at 1861" not in t]
res["tried_and_dead"] += [
    "room 1: K6c's later inputs simply shifted 4..8 frames behind the pause-free ride: no capture (the toad faces right after the ride and the hop does not grab the snake; needs the Left x2 tap) (u16k_r1shift.py)",
    "room 1: waiting at the park spot (334, 7934) and jumping straight up onto the 7984-run after the head has turned: the lower run retracts at ~1550 and the toad falls two floors (u16k_r1ride2.py)",
    "room 1: capture 2 frames sooner needs the toad 6 px ahead of the head's coordinate at the jump, the very edge of what the head carries; boardings and walks tried all end on the same capture frame",
    "warp room: head pauses there too (r+157, 166 in K6's line, while the toad waits at the head's top); they cost nothing: the crossing slot is set by the body tiles and the toad's own height "
    "(release needs toad H >= 7649 with the head at >= 7632, first possible at r+159/160), and none of ~150 variants crosses at r+167",
]
res["downstream"] = (
    "Level 8 and everything behind it must be re-fitted behind K6 (Level 8 starts 128 frames earlier; RAM at the placement equals L6c's except timers $0B/$1A, but the dice still roll differently). "
    "Level 6 itself has no re-rolls. Chain: L1b L3u L3skipu L4c5 K6 <Level 8 ...>. Level 8 entry bookmark: states/K6_end0.State (in place of L6c_end0).")
res["numbers"].update({"room2_appears_at": 1986, "old_room2_appears_at": 2022, "exit_capture_index": 1857, "touch_to_placement": 215})
res["files"]["segments"] = (
    "logs/pbeam_K6.json (final, 2467 inputs) = logs/pbeam_K6d.json. Earlier verified versions kept: logs/pbeam_K6c.json (2474: room-1 last jump + warp room; power-on logs/fix/u16k_poweron_K6c.txt, placement 12362), "
    "logs/pbeam_K6b.json (2503: warp room only; power-on logs/fix/u16k_poweron_K6b.txt, placement 12391); entry bookmarks states/K6c_end0.State, K6d_end0.State, K6_v2_end0.State.backup (K6b)")
res["files"]["logs"] = (
    "logs/fix/u16k_* : warp-room line u16k_line_rj94.json; room-1 line u16k_room1_v3.json; record video sheets u16k_wr_jump.jpg, u16k_wr_z1.jpg, u16k_wr_z2.jpg, u16k_wr_flight.jpg, measurements u16k_wr_meas.json; "
    "scans u16k_scan1/2/3, u16k_ledge, u16k_under, u16k_mash, u16k_mash2, u16k_stand, u16k_beam*, u16k_pokeprobe, u16k_r1trace, u16k_r1board*, u16k_r1scan5_*/7_*, u16k_r1ride*, u16k_r1pauses_*")
res["files"]["scripts"] = (
    "u16k_*.py: builder u16k_build6c.py <out> <room1 json> <line json> (u16k_build6b.py = warp room only behind L6c's room 1); power-on check + entry bookmark u16k_poweron.py <segment>; "
    "room 1: u16k_r1trace.py, u16k_r1run.py, u16k_r1pauses.py, u16k_r1ride.py, u16k_r1board3.py, u16k_r1scan7.py; warp room: u16k_sprint.py, u16k_scan1/2/3.py, u16k_ledge.py, u16k_under.py, u16k_mash*.py, u16k_pause.py; helpers u16k_lib.py")
res["notes"] = (
    "K6 verified from the bookmark and twice from power-on (RAM sha1 0f56db25): Level 8 placement on frame 12355 instead of 12483 (-128). "
    "Warp room (-90): the record's own line, started 16 frames earlier than he does - standstill dash jump at the snake (Right, release, Right+A on one frame keeps run speed 192 through the grab "
    "while Right+A stays held), climb at 3 px/f, over the rising head, 3 px/f flight over the first star to the ledge, portal touch at r+266 (up14 r+356; the record ~r+280). "
    "Room 1 (-36): ride the third snake behind its head so it never pauses (-6), board its head as it turns onto the top run and dash-jump from it straight into the exit hole's capture zone (-30). "
    "Warp pages by BFS, three presses, no Start (-2). Everything behind Level 6 has to be re-fitted. Open lead: ~20 more frames in room 1 by keeping the toad off the snakes' heads (see 'not_done').")
tmp = "knowledge/u16k_result.json.tmp"
json.dump(res, open(tmp, "w", encoding="utf-8"), indent=1)
os.replace(tmp, "knowledge/u16k_result.json")
print("written", os.path.getsize("knowledge/u16k_result.json"), res["frames_saved"], res["l8_placement_frame"], res["verification"]["K6_equals_K6d"], res["verification"]["inputs_sha1"])

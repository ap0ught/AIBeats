# The tower (Level 12, The Revolution): track L12's report, 2026-10-10

Saved verbatim from the recovery workflow's journal so later work can read it. Segment `logs/pbeam_L12h.json`
(8,411 inputs from bookmark `L11r_end0`; L12g was 8,880). Scripts `l12h_*.py`, pieces `logs/fix/L12h_*.json`.

## deliverables

- logs/pbeam_L12h.json: new tower segment, 8,411 frames from bookmark L11r_end0 (L12g 8,880: -469). Plain replay check (l12h_compose.py): level byte 13 on the last input, health never below 47, 4 lives, 0 Left+Right / Up+Down / Start presses. End bookmark L12h_end0.
- Best Armageddon behind it: logs/pbeam_L13_L12h_k0.json (l13solve2.py L12h_end0 0, width 800): kill at input 948, cut to Professor T. Bird 2,029 frames after the entry, VALID. Other dice: k1 2,039, k2 (width 600) 2,064.
- VERIFIED FROM POWER-ON: assemble.py fixL12h L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12h L13_L12h_k0 = 46,617 frames, two replays MATCH sha1 10722e85, clock start 2074, T. Bird cut at frame 46617 = 12:21.16, 8.09 s under the record (up14's true cut was 47253; goal was <= 47040). Log: logs/fix/assemble_fixL12h.txt.
- Also verified with the Terra Tubes track's segments as they stood at 02:40: assemble.py fixL12h_heli L1b L3u L3skipu L4c5 L6c L8c L9heli_s160_1 L9heli_L10 L9heli_L11 L12h L13_L12h_k0 = 46,440 frames, MATCH sha1 9a02f991, T. Bird cut 46440 = 12:18.22 (11.03 s under). L12h + L13_L12h_k0 replay unchanged from L9heli_L11_end0 (end RAM of L12h identical, 0 bytes differ). Log: logs/fix/assemble_fixL12h_heli.txt.
- Fallback: logs/pbeam_L12hb.json (8,533 frames, -347; older walker finish) with logs/pbeam_L13_L12hb_w4.json (T. Bird 2,028 after the entry, width 400) - not assembled from power-on.

## findings

- Where the 469 frames are (L12h frame vs L12g): pre-face-2 Hornhead kill 5323 (5329); face 2 spawn 5421 (5444); wide platform 5958 (6087); walker's ring 6276 (6442); walker dead 6460 (6669); face 3 spawn 6546 (6954); face 4 spawn 7123 (7545); spring ledge 7646 (8085); level byte 13 at 8411 (8880). L12h is identical to L12g for its first 5,140 frames.
- Legal replacement for the TAS's Left+Right instant sprint: tap the direction (up to ~13 frames), release 1-3 frames, hold it again from the launch/jump frame -> speed 192 (3 px/frame) at once. Works for jumps (tap on the last air frame, release on the landing frame, direction+A) and for spring launches (tap at launch-2, gap, hold from the launch frame). This is what made the TAS's face-2 exit, lift catch and platform launches reproducible.
- Spring (0x36) pump: a FRESH A press while standing on it (or up to 3 frames before landing) starts a 24-25 frame sink-and-throw; A held through a landing does nothing. A can be pressed during attack recovery (boot anim 30, ram anim 49) so the throw comes on the first free frame - used after the pre-face-2 boot and after the walker kill (launch 6501 instead of 6525).
- Wind faces: a pole cannot be released while the wind blows; release works from face spawn + 351 (earlier Down presses are ignored). Exposed to the wind the toad dies after ~110 frames. Face 2 (at x 48) blows Right, away from its poles; faces 1 and 3 (at x 244) blow Left, toward theirs. The floors at H 4382 and H 4766 are complete rings around the tower.
- From face 2 on nothing is locked to the frame counter: the lift (0x34 H 4488, appears at x 238 when the camera crosses 1496, moves Left 2 px/f), the circling platform (H 4632, x 382 at camera ~1438), the lower spring (H 4800, x ~376 at camera <= 1267) and the upper spring (x 322 at camera 1104) all spawn with the camera, so gains there carry 1:1. Only spring phases relative to the 449-frame face cycle matter (e.g. the lower spring must pass under the face-3 pole between spawn+387 and +440; with face 3 at 6546 it does, with 6614 it cost ~35 frames).
- Walker (0x62, 79 hp) is a juggle, not five separate fights: it flies in on a fixed arc ~38 frames after spawning; once hit it hangs stunned in the air. Line used: sprint Left, running kick (hit 6328), B held = second kick (6352), two dash-jump air kicks with a one-frame direction gap (anim 38), then hop Left and Right+B at sprint speed = ram (anim 35 -> 49) that kills at 6460 and carries the toad onto the lower spring at 6474. A standing kick from the spring also kills but its hop is in place and the spring leaves (boarding 6545 instead of 6474).
- The TAS's fast camera at faces 3/4 ('camera snap') is NOT legal: its Left+Right frames shift the toad's depth byte $41B from 216 to 125, so the game sees it higher on screen (found by copying TAS RAM into a snapshot and bisecting - debug only). Legal camera speed is 1 px/f for a small excess of H+cam over ~5992, up to 3-4 px/f for a large one. Face 4 now spawns 577 frames after face 3 (L12g 591).
- Top: sprinting the H-5694 floor and a dash jump saves 30; a shorter last hop saves 6. The level-end event (0x7F) needs A held on the top ledge and fires when the camera reaches 42; fresh jumps there never end the level.
- Queen portability: the Level 13 entry RAM of two tower variants differs only in $0B/$0C, yet L13y0 does not replay after any length change tried (+1, +2, +4 frames, or L12f's end) - the queen must be re-solved for each tower end. Poking $0B/$0C alone on the same savestate does not change her fight, so the cause is outside those bytes (+2 frames also changes $700-$709).
- L12h is sensitive to the random numbers from frame 5786 on (debug poke test, l12h_rngrob.py: first divergence at the pole release, which is frame-exact). It replays bit-identically from L11r_end0 and from L9heli_L11_end0; on an upstream that changes the Level 12 entry state it needs rngfit or a re-run of the stage scripts (s0b -> s1e -> s2r -> s2b2 -> s3a -> s3c -> w8a -> w10 -> s5 -> s6 -> s7 -> compose; they chain 'pieces' in logs/fix/L12h_*.json from bookmark L12h_g_f5000).
- Not done - the first 5,000 frames of the tower. The 1-player TAS reaches face 1 687 frames before us. Legal-looking parts: ~160 in the climb between frames 843 and 1343 (extra spring bounces), ~170 at the camera-4713 Hornhead (ours: three kicks, kill 264 frames after spawn, then 44 frames to the next ledge; TAS kills at +116 and is already pumping the spring when the body goes), ~48 at the big walker (one hit of the rhythm missed). These only pay in steps of 256: the green ledges after face 1 are solid on a frame-counter window and we wait 67 frames there (L12g 5044), so >= 189 frames gained before it give exactly 256, less gives nothing. Everything after would have to be rebuilt (tail is RNG-sensitive). One test from frame 850 showed the TAS's first Left+Right dash jump cannot be copied 1:1 (the toad faces the wrong way after the boot; the turn costs ~6 frames).

## notes

The tower segment is rebuilt from the Hornhead before wind face 2 to the end: L12h is 8,411 frames against L12g's 8,880, and the full route with it is verified from power-on at a T. Bird cut of 46617 (12:21.16, 8.09 s under the record). The same L12h and queen segment also verify on the Terra Tubes track's upstream at 46440 (12:18.22); that number depends on their segments as they stood when I ran it.

- **Queen:** the best behind L12h_end0 is 2,029 frames to the T. Bird cut (one width-800 solve). The L13 track's solver reached 2,021 from L12g_end0 with more seeds, so a few more dice here may shave ~10 frames; I did not run them.
- **Fallback segment:** L12hb (-347) passes the plain replay check but was not assembled from power-on.
- **Fragility:** L12h only replays on an upstream that leaves the Level 12 entry state unchanged. It is frame-exact at the face-2 pole release.
- **Part 1 of the tower (frames 0-5000) is untouched.** There is a plausible further 256 frames there, but it is a multi-hour rebuild followed by a full re-run of my stages and a new queen.
- **Process hygiene:** I stopped only my own python/EmuHawk processes, by PID. At the end one assemble.py run (route up16b0, another agent's, already using L12h and L13_L12h_k0) was still going; I left it alone.
- **Shared files touched outside my ownership:** assemble.py wrote logs/fixL12h*.inputs/.events/.trace.txt and video/fixL12h*.mkv and added two route marks to the token log; l13solve2.py wrote its usual knowledge/l4s_L13_L12h*_beam.json, logs/l13solve2_L13_L12h*.txt and states/L13_L12h*_end.State. I did not edit the journal, memory, or any other agent's scripts.
- **Debug pokes** were used only in probes on snapshots (l12h_campoke.py, l12h_q0c.py, l12h_rngrob.py); no run or segment contains one.

## files changed

- logs/pbeam_L12h.json
- logs/pbeam_L12hb.json
- logs/pbeam_L13_L12h_k0.json
- logs/pbeam_L13_L12h_k1.json
- logs/pbeam_L13_L12h_k2.json
- logs/pbeam_L13_L12hb_w4.json
- states/L12h_end0.State
- states/L12hb_end0.State
- states/L12h_*.State (stage bookmarks, incl. L12h_g_f0..f8750 probe bookmarks of L12g)
- l12h_lib.py
- l12h_compose.py
- l12h_s0.py, l12h_s0b.py, l12h_s1e.py (pre-face-2 fight + dash launch to the pole)
- l12h_s2r.py, l12h_s2b2.py (face-2 exit)
- l12h_s3a.py, l12h_s3c.py (wide-platform Hornhead, circling platform)
- l12h_w8a.py, l12h_w10.py (walker juggle and finish)
- l12h_s5.py, l12h_s5b.py, l12h_s6.py, l12h_s7.py, l12h_topref.py, l12h_top1.py, l12h_top2.py (faces 3/4, top)
- l12h_*.py (other probes: probe, events, dump, tascmp, tasev, tasrun, try, show, dash, dash2, campoke, parity, q0c, rngrob, w*.py, s1*.py, s2*.py, mkold, diffend)
- tas/l12h_dump_l12.lua
- logs/fix/L12h_*.json, L12h_*.txt, g.ram, tas_l12.ram, tas_l12_inputs.txt, tas_l12_events.txt, L12g_events.txt
- logs/fix/assemble_fixL12h.txt, assemble_fixL12h_heli.txt
- logs/fixL12h.inputs.txt (+ .events/.trace, video/fixL12h.mkv) and logs/fixL12h_heli.* written by assemble.py

# Contra (NES) Any% No Turbo record: frame timing notes

Run: Angrylanks, 9:48.183 (588.183 s), https://www.youtube.com/watch?v=YgtFCclM1jM, speedrun.com run z0nxpj9m, played on a PowerPak in a top-loader NES. Measured 2026-10-11 from the 720p60 stream. Machine-readable numbers are in `record_events.json`; this file explains them.

All frame numbers are video frame indices. Frame n covers video time n/60 to (n+1)/60 s.

## Headline

| | video frame | video time |
|---|---|---|
| START (medals first visible) | 720 | 12.000 s |
| END (Bill reverts to standing) | 36011 | 600.183 s |
| Span | 35291 frames | 588.1833 s |
| Claimed | 35291 frames at 60 fps | 588.183 s |

The span matches the leaderboard time to the frame. The moderators counted from the first video frame showing any medal to the first video frame showing any standing pose, at 60 fps.

In NES frames (60.0988 fps): 588.1833 x 60.0988 = **35349 +/- 2**.

## 1. Frame rate and what the video really contains

- **Container: exactly 60.000 fps, constant.** I seeked in 1 ms steps and found the frame boundaries at t = 30, 200, 400 and 690 s. They sit at n/60 with the same phase every time (x.017, x.034, x.050). A 59.94 stream would have drifted 0.69 s by then.
- **Content: about 30 distinct images per second.** Consecutive video frames come in identical pairs. Each distinct image is two consecutive NES frames woven together line by line (the capture device treated 240p as 480i). You can see the comb: on frame 720 the medals exist on alternate lines only.
- **Pairing is not perfectly regular.** In two 60-frame samples I saw a few single frames and a few 4-frame holds. That is capture jitter, a couple of frames either way.
- **Tolerances.**
  - Events first seen combed (one field only): +/-1 video frame. The new state belongs to the later of the two woven NES frames. START and END are both like this.
  - Other events: +/-2 video frames.
  - Events marked approximate carry their own tolerance in the JSON.
- **Assumption behind the NES-frame figure:** the recording PC's clock is right and the console runs at 60.0988 fps. I could not test either from the video. The JSON lists fixed in-game delays (see "Calibration") that the harness can measure in NES frames to check the ratio.

One reliability problem during measurement: after a lot of seeking the browser's buffer went bad and one 3.6 s block returned a frozen frame. I flushed the buffer and added a check that flags identical consecutive reads. Every sheet after that reported zero stale frames, and the scans done before it show normal frame-to-frame noise, so I do not believe any number here is affected.

## 2. START

- 719: no medals. 720-721: two medals, one field only. 722 onward: full.
- Anchors a RAM harness can find on its own:
  - Title screen: 144 to 469 (last frame). The "1 PLAYER" line is flashing for the whole of that span.
  - Black: 470-473.
  - Stage intro screen ("1P 0 / REST 3 / HI 24500 / STAGE 1 JUNGLE"): 474 to 663.
  - Black: 664-675.
  - Playfield first visible: 676. It is revealed left to right and is complete at 702.
  - Medals: 720. Bill first visible: 722 (somersaulting near the top).
  - Title last frame to medals: 251 video frames.
- **Not measurable:** the first frame Bill can be moved. His sprite is drifting right from about 724, so he has control more or less immediately, but that is an inference.
- LiveSplit reads 0.28 at frame 730, so the runner's own timer started at about frame 713.

## 3. END

- Heart: first explosion sprite at 35788. Bill was mid-jump right next to the heart and lands on that frame.
- Bill is prone afterwards, so the runner is **holding Down**. The handcam shows a hand on the controller but not which button.
- Prone through 36010. Frames 36011-36012 are one woven image with prone in one field and standing in the other. Fully standing from 36013.
- Heart explosion to automatic stand: 223 video frames.

## 4. Span against the claim

No discrepancy. 36011 - 720 = 35291 frames = 588.1833 s, and 588.183 x 60 = 35290.98.

Because both ends are half-field frames with the new state in the later field, the two ends have the same sub-frame bias and it cancels.

## 5. Splits

Cumulative seconds from START. "Black" is the first frame with the background blanked; sprites linger for one more captured image.

| Stage | Medals | Boss first explosion | Control lost | Black |
|---|---|---|---|---|
| 1 Jungle | 720 (0.00) | 3918 (53.30) | 4114 (56.57) | 4377 (60.95) |
| 2 Base 1 | 4621 (65.02) | 7548 (113.80) | ~7566 (114.10) | 8093 (122.88) |
| 3 Waterfall | 8331 (126.85) | 11600 (181.33) | ~11702 (183.03) | 12015 (188.25) |
| 4 Base 2 | 12259 (192.32) | 17214 (274.90) | ~17230 (275.17) | 17756 (283.93) |
| 5 Snow Field | 18011 (288.18) | 23493 (379.55) | ~23624 (381.73) | 23871 (385.85) |
| 6 Energy Zone | 24126 (390.10) | 27660 (449.00) | ~27762 (450.70), inferred | 28007 (454.78) |
| 7 Hangar | 28262 (459.03) | 32050 (522.17) | 32246 (525.43) | 32488 (529.47) |
| 8 Alien's Lair | 32743 (533.72) | 35788 (584.47) | 36011 (588.183) | none |

Playfield-first frames: 676, 4592, 8306, 12230, 17967, 24082, 28218, 32701.

What "control lost" means per stage, and how sure I am:

- **Stage 1 and 7 (wall bosses):** Bill's pose reverts and the automatic walk or jump starts 196 frames after the first explosion. Measured in both.
- **Stage 3 and 5:** automatic stand or walk 102 frames after the explosion (in stage 5, after the exit door starts exploding at 23522, not after the saucer). Measured in both.
- **Stage 2 and 4 (base bosses):** Bill starts walking left 16-18 frames after the explosion and the lift rises 190 frames after it. I cannot tell from video whether that walk is automatic.
- **Stage 6:** not observable. He walked to the gate himself during the explosions. The figure is explosion +102 by analogy.
- **Stage 5 boss death is soft.** Hit-explosion sprites cover the saucer from about 23468; the body breaks up at 23493. The lethal hit could be up to about 27 frames before 23493.

### Base rooms

"Onset" is the first frame of the wall-wide explosion after the core dies, found numerically from centre-screen brightness. The core's own first puff is 10-12 frames before onset in the rooms I checked by eye. "Dark" is the next room's dark interior appearing, "lit" is the next room fully drawn.

Base 1 (stage 2), room 1 lit at 4721:

| Room | Onset | Dark | Next lit | Lit to onset |
|---|---|---|---|---|
| 1 | 4992 | 5136 | 5216 | 271 |
| 2 | 5487 | 5631 | 5712 | 271 |
| 3 | 5977 | 6121 | 6198 | 265 |
| 4 | 6489 | 6631 | 6708 | 291 |
| 5 | ~7015 | 7157 (black) | boss room 7242 | ~307 |

Room 5's onset is inferred from the fixed dimming steps, +/-3.

Base 2 (stage 4), room 1 lit at 12361:

| Room | Onset | Dark | Next lit | Lit to onset |
|---|---|---|---|---|
| 1 | 12551 | 12693 | 12768 | 190 |
| 2 | 13257 | 13399 | 13470 | **489** |
| 3 | 13739 | 13881 | 13960 | 269 |
| 4 | 14286 | 14428 | 14503 | 326 |
| 5 | 15039 | 15181 | 15262 | **536** |
| 6 | 15533 | 15675 | 15749 | 271 |
| 7 | 16105 | 16245 | 16324 | 356 |
| 8 | 16658 | 16800 (black) | boss room 16867-16882 | 334 |

Onset to dark is 142 frames in 10 of 12 rooms (144 twice), which is a good check that the method is stable.

## 6. Route facts

### Lives and deaths
- No Konami code: the first intro screen says REST 3 and the HUD shows 2 medals.
- **No deaths, with good evidence.** REST and score on each stage intro screen: 3 / 0, 4 / 24000, 4 / 36800, 5 / 56200, 5 / 73500, 7 / 110400, 7 / 132400, 8 / 156000. That fits extra lives at 20k, 50k, 80k, 110k and 140k with nothing lost. The threshold rule is my inference from these numbers; the REST values are read off the screen.

### Weapons (stage 1 only was checked closely)
| Video frame | Time from START | Item | How |
|---|---|---|---|
| ~1029 | 5.2 s | M | First pillbox sensor, shot from the top ledge; the falcon pops up to him |
| ~1597 | 14.6 s | R | Flying capsule shot just before the first bridge; falcon lands on the far bank |
| ~2315 | 26.6 s | S | Ground-level flying capsule shot at ~2226; falcon flies up and drops on him |
| ~3377 | 44.3 s | unknown, probably R | Flying capsule destroyed point-blank mid-jump, just before the rotating wall cannon |

- M and R were read off the icon. S was not legible; a spread fan is on screen from about 2515.
- The fourth pickup is inferred twice over: the falcon never appears separately, and the letter is a guess (a second R after S). The harness should check in RAM what that capsule holds and whether S clears the rapid flag.
- Not taken: a pillbox item below the path (~2500) and a falcon left lower-left (~3300).
- **Stages 2-8 were not scanned for pickups.** Spread is visibly still in use at the stage 5 boss and the stage 6 boss, and with no deaths it cannot have been lost, but an extra pickup later (R, B) is not ruled out.

### Bosses and tricks
- **Stage 1 wall:** jumps onto the ledge directly in front of the core, goes prone at about 3886 and fires point-blank. Core dies at 3918, about 0.5 s later.
- **Stage 1 bridge:** jumps from the ledge onto the first bridge as it explodes (about 1430-1540) and collects R on landing.
- **Base 1 boss:** room appears 7242, dead 7548 (5.1 s).
- **Waterfall boss:** on screen from about 10916-10940, dead 11600 (about 11 s). Finishes prone right under the mouth.
- **Base 2 boss:** room at 16867-16882, dead 17214 (about 5.6 s).
- **Snow Field boss:** stands left of the exit door and fires straight up from about 23244 before the saucer exists, then jumps into it repeatedly to hit it point-blank. Appears about 23330, breaks up 23493 (about 2.7 s).
- **Energy Zone boss:** fires from the left from 27460, the giant lands about 27490, then Bill **jumps over it** (27560-27602) and finishes it from the right, facing left. Dead 27660 (2.8 s).
- **Hangar:** stands under the door target firing up-diagonal. Target gone 32048.
- **Alien's Lair:** alien head appears about 33263, dies about 33537 (4.4 s). Heart dies 35788, with Bill jumping right beside it.
- The stage 3 climb and the stage 5-8 running sections were not analysed for tricks.

### The two bad rooms in Base 2
The description says two rooms in base 2 went wrong. They are **room 2 and room 5**, the two rooms with a pair of side cores, and far the longest (489 and 536 frames against 190-356 for the rest).

- **Room 2:** centre panel destroyed ~12930, left core ~13020 (90 frames later), right core not until ~13210 (190 frames after that). He moved right and was missing it. Estimated loss about **1.7 s**.
- **Room 5:** centre destroyed ~14597, left core not until ~14831 (234 frames), right core ~14935 (104 frames later). Estimated loss about **2.3 s**.

Those estimates assume a clean core takes about 95 frames, which is what the good core in each room took. Treat them as +/-1 s. LiveSplit shows he dropped 2.9 s against his own previous splits in this stage, which is the same order of size.

### One thing the coordinator should know
The video's LiveSplit footer reads "World Record is 9:47.8 by k1ngk0opa", and the video's description says the run's mistakes cost him a world record. So at upload this run was not the fastest known time. The speedrun.com API today lists it first in Any% / No Turbo (second place 593.167), so the 9:47.8 is presumably in the Turbo subcategory or no longer on the board. I did not check which.

## 7. Fire rate

Bullets cannot be counted at the bosses themselves, because he fires point-blank and they vanish at once. I used two places where he fires at range while standing still, and plotted bullet position against time to get the interval between successive centre-line spread bullets.

| Sample | Frames | Interval between shots | Rate |
|---|---|---|---|
| Snow Field, straight up before the boss | 23248-23312 | 4.0-5.4 frames, mean 4.8 | 12.5 /s |
| Energy Zone, firing right before the boss | 27464-27486 | 4.0-6.1 frames, mean 4.7 | 12.8 /s |

- A cruder count on the first sample (bullets present divided by flight time) gives 10.7 /s, low because dim bullets get missed.
- Handcam: brightness spectra of the hand during the stage 1 boss and the heart have weak peaks at 11.5-13.5 Hz. Supportive, not a measurement.
- **Estimate: 12.5 +/- 1 shots per second.**
- **Suggested cap for the AI: 12 presses per second**, meaning at least 5 frames between press starts.
- Caveat: this counts presses that produced a bullet. With spread, the on-screen bullet limit can swallow presses, so his real press rate may be higher. The shortest single gaps were 4.0 frames (15 /s instantaneous).

## Calibration intervals for the harness

Fixed in-game delays as they appear in this video, in video frames. In NES frames they should be about 0.16% longer.

- Title last frame to medals: 251
- Stage intro screen: 188-191
- Playfield first to medals: 44 (stages 1, 5, 6, 7), 42 (stage 8), 29 (stages 2, 4), 25 (stage 3)
- Base room wall explosion to next dark room: 142
- Base boss explosion to lift rising: 190
- Wall boss first explosion to pose revert (stages 1, 7): 196
- Stage 3 and 5 explosion to automatic walk: 102
- Heart explosion to automatic stand: 223

## Measured and inferred, in one place

Measured directly: container frame rate, START, END, span, all medal, playfield, intro-screen and black frames, base-room onset/dark/lit frames, boss first-explosion frames for stages 1, 2, 3, 4, 6, 7 and the heart, REST and score values, M and R pickups, bullet spacing and speed.

Inferred or soft: NES-frame conversion (assumes clocks), first frame Bill can move, stage 5 lethal hit, stage 6 control lost, Base 1 room 5 onset, S letter, the fourth stage 1 pickup and its letter, the extra-life thresholds, the loss estimates for the two bad rooms, weapons after stage 1, and the press rate as opposed to the shot rate.

# Can our AI beat the best Contra TAS? Section-by-section comparison (2026-10-16)

TAS = tasvideos **4623M**, Mars608 & aiqiyou, **8:48.213 = 31,745 frames**, FCEUX 2.2.2, **Contra (Japan)**.
Checked on https://tasvideos.org/18G on 2026-10-16: the featured "1 player" run is still this one (08:48.21), the
publication page https://tasvideos.org/4623M links the YouTube encode we measured (6kej45k7StE). Nothing newer.
Ours = our best verified US-ROM stage results (S1 3,898 / S2 3,604 / S3 3,494 / S4 5,154 / S5 6,039 / S6 4,028 /
S7 4,407 / S8 3,237). They come from different runs, so they are not one chained run. The best complete verified
run is chain1, 9:33.622.
Machine-readable numbers: `knowledge/tas_compare.json`. Each number is marked **[M]** measured (video or movie file),
**[C]** code or our RAM logs, or **[E]** estimate. All frame counts are NES frames (60.0988 Hz) unless they say "video".

## Bottom line

| | frames | time | kind |
|---|---|---|---|
| TAS, gameplay only (8 stages, first medal frame to boss event, stage 8 to END) | 28,246 | 7:50.0 | M |
| Ours, gameplay only (same events) | 29,066 | 8:03.6 | C |
| **Gameplay gap (the real difference)** | **820** | **13.6 s** | M/C |
| TAS **on our clock**, JP ROM (first medal frame to END) | 31,525 | **8:44.55** | M (END = heart explosion + 223, E) |
| Ours **estimated on the JP ROM** (our gameplay + the TAS's JP transitions) | 32,344 | **8:58.19** | E |
| TAS estimated on the US ROM, our clock (TAS gameplay + our US transitions) | 33,041 | 9:09.79 | E |
| Ours on the US ROM (sum of best verified segments) | 33,861 | 9:23.42 | C |
| Ours on the JP ROM, **TAS timing** (power-on to last input), vs 31,745 | 32,563 | 9:01.83 vs 8:48.21 | E |

* The JP-vs-US version difference is **1,517 frames (25.2 s)** over the seven stage transitions. It is all in the
  transitions, not in gameplay. Compared on the same version, **the TAS is 13.6 s ahead of us**. Per stage, the
  TAS is ahead in 7 stages and level in 1 (stage 7).
* The research estimate of the TAS under the US board rule (9:06-9:08) was about 2-4 s too optimistic. Measured
  gameplay + US transitions gives **9:09.8**.

## Per stage: gameplay (identical in both versions) and transitions

Gameplay = from the stage's first medal frame to the boss event below. Stage 5 uses the scripted walk after control
is lost; stage 8 runs to END. Transition = from that event to the next stage's first medal frame.

| stage | event | TAS gameplay [M] | ours [C] | TAS - ours | JP transition [M] | US transition, ours [C] | JP saves |
|---|---|---|---|---|---|---|---|
| 1 Jungle | wall core first explosion | 3,176 | 3,197 | **-21** | 496 | 701 | 205 |
| 2 Base 1 | eye gone / first explosion | 2,623 | 2,820 | **-197** | 582 | 784 | 202 |
| 3 Waterfall | gate first explosion | 2,663 | 2,784 | **-121** | 455 | 710 | 255 |
| 4 Base 2 | last helmet gone / first explosion | 4,005 | 4,352 | **-347** | 599 | 802 | 203 |
| 5 Snow Field | scripted walk after control loss | 5,503 | 5,532 | **-29** | 304 | 507 | 204 |
| 6 Energy Zone | giant gone / first explosion | 3,388 | 3,431 | **-43** | 395 | 597 | 202 |
| 7 Hangar | door gone / first explosion | 3,712 | 3,713 | **-1** | 449 | 694 | 245 |
| 8 Alien's Lair | heart first explosion (END) | 2,953 (3,176) | 3,013 (3,237) | **-60 (-61)** | - | - | - |
| **sum** | | **28,246** | **29,066** | **-820** | **3,278** | **4,795** | **1,517** |

Our events are taken from RAM: explosion seen = `$3B` + 3 (the video pipeline's measured offset), medals seen on row 1,
stage 5 walk = `$3B` + 50 + 33 (s5_notes). Exits (`$3B` to the next stage's first frame) are the same in chain1 and
the best runs.

**The transitions explained [C + M].** From the boss's explosion to the first black frame, the TAS and our US runs
take the same time within 2 frames in stages 1, 2, 4, 5 and 6 (458/457, 547/545, 545/545, 250/250, 342/340). So
the end-of-level script and the 160-frame delay are the same in both versions. After the black frame, the JP game
draws the next stage in 35-54 frames. The US game shows the 192-frame score screen (`level_routine_02`, `$2A`=$C0)
plus about 51 frames of draw and load (chain1: level byte change to the next first frame = 243). That is the
**~203 frames per stage**. Stages 3 and 7 are a further **48 and 41 frames** shorter on JP before the black frame.
Our stage 7 exit equals the record's (695/694), so this is most likely a version difference. The JP code is not in
the project, so this is not identified. It is counted as version, not gameplay.

## Inside the stages

**Stage 2 (Base 1), -197.** Room onset = the frame the electric barrier is gone (wall explosion), measured on the TAS
by a colour detector, against ours = room load + last-hit T + 34 [M/C]:

| room | TAS onset | ours | TAS gain in this room |
|---|---|---|---|
| 1 | 333.5 | 334 | -0.5 |
| 2 | 797.3 | 822 | -24.2 |
| 3 | 1,261.1 | 1,310 | -24.2 |
| 4 | 1,725.8 | 1,797 | -22.3 |
| 5 (16-HP core) | 2,196.6 | 2,313 | -45.2 |
| boss (room 5 onset to explosion) | 426.7 | 507 | -80.3 |

Room 1 is level (both about T 300; one soldier, slot-limited). Rooms 2-4: the TAS's last hit lands about T 270, ours
at the 5-frame-cap floor T 293. Room 5: 16 hits at up to 1 per frame against our 5 frames per press. The boss room is
the biggest single item. The TAS kills Garmakilma 212 frames after the room appears; the record takes 306 and we
are level with the record.

**Stage 4 (Base 2), -347** [M/C]: room onsets 197 / 770 / 1,132 / 1,620 / 2,185 / 2,649 / 3,113 / 3,583 against ours
213 / 825 / 1,226 / 1,745 / 2,343 / 2,843 / 3,355 / 3,866. The TAS gains -16, -39, -39, -31, -33, -35, -48, -41 in
rooms 1-8 and **-64 at the boss**: 421.7 vs 486 from room 8's onset; 210 frames from the room's appearance, with
only one helmet left by the end. Every room is faster, so this is fire rate: plated cores, several cores per press,
and 1 HP per frame on 16- and 23-HP targets.

**Stage 3 (Waterfall), -121, all in the climb** [M]:
* The 64-px boss auto-scroll starts 1,838 frames after the medals for the TAS against 1,958 for ours (-120).
* The mouth opens 2,537 vs 2,660, and the kill takes 126 vs 124 (level).
* The TAS makes 42 jumps before the scroll and we make 41. The count of ledge skips is therefore about the same (ours
  is 13). The TAS chains its jumps every 40-58 frames. We have **three waits of 96, 74 and 106 frames** at the
  floating rocks.
* 7177S/7317S say the TAS times the rock's spawn frame and uses Y-subpixel control. Not a press-rate issue: a
  solver/route issue.

**Stage 8, -61** [M/C, ours' guardian E]: guardian first explosion 710 vs about 745 (-35); heart 2,953 vs 3,013 (-60
overall, so -25 after the guardian). Both are fire-rate limited (bullet slots and 1 HP per frame).

**Stage 6, -43** [M, appearance E]: the giant appears about 3,284 (+-10) vs ours 3,292 (created). The TAS kills it in
about 103 frames against our ~141, so nearly all of the gap is the boss fight. The TAS uses its 2 Left+Right frames
during this fight (movie 24214/24218 = video ~24294/24298), and two 2-frame pauses earlier in the stage (flame
timing, as its notes say).

**Stage 5, -29** [M total; split E]: the approach is about equal. The fitted-TAS boss scroll was 5,089 vs our 5,094 in
s5_notes. The likely cause is the UFO kill: ours 65 frames for 32 HP, while the TAS can hit about once per frame.

**Stage 1, -21** [M total; split not measured]. 7177S credits its boss fight with an earlier first bullet stream.

**Stage 7, level (-1)** [M]: our second-pass route (Barrier, no stop in Heartbreak Alley, trio volleys, scripted door)
matches the TAS's gameplay to within a frame, even under our press caps. The TAS takes the Barrier ("B") too, per
7317S's submission notes.

## Route facts and inputs (movie file [M])

* **Fire:**
  * B presses per stage: 105 / 700 / 72 / 1,189 / 203 / 112 / 181 / 211 (2,773 total, every one 1 frame long).
  * The tightest gap is 2 frames, used 1,889 times. Maxima: 28 per 60 frames, 235 per 600, 618 per 1,800. Our
    limits are one press per 5 frames, 109 per 600 and 246 per 1,800.
  * Outdoors the TAS fires only 1.4-2.6 presses/s. It mashes at up to 30/s in the bases (13-15/s on average there)
    and at the bosses. **The press cap matters almost only in the bases and in the boss fights.**
* **Pauses:** four in-level 2-frame pauses: two in stage 6 (movie 22475, 22506) and two in stage 7 (25964, 27563).
  Plus the intermission skips (Start twice, 2-3 frames apart, at 4084, 7291, 10407, 14995, 20801, 24584, 28745) and
  an intro skip (395/398).
* **Left+Right:** 2 frames (stage 6 boss). **Up+Down:** 10 frames (stage 1: 2, stage 3: 1, stage 6: 1, stage 7: 6).
* **Waterfall:** 42 jumps to the top (A presses every 39-58 frames from movie 7392 to 9148).
* **Deaths:**
  * No death was seen. The medal counts at the stage starts (2, 3, 3, 4 for stages 1-4) match the record's no-death
    pattern.
  * From stage 4 on the HUD caps at 4 medals, so stages 5-8 cannot be checked that way.
  * 4623M is not tagged "uses death"; the older 4409M/4504M are.
  * Treat "no deaths" as likely, **not verified**.
* **Weapons:** the TAS fires Spread in every boss and base fight sampled. The pick-up frames were not measured.

## What it would take to beat the TAS outright (TASVideos rules)

* **Rules** (https://tasvideos.org/MovieRules, read 2026-10-16):
  * Timing is power-on to the last input.
  * Any official version is allowed if the choice is explained.
  * "Regional differences such as text and cutscene length are completely discounted… Only actual gameplay is
    considered."
  * So a US-ROM movie could obsolete 4623M only by beating its comparable gameplay. The 25 s of JP transitions do
    not help or hurt either way.
  * No press limit. Left+Right and Up+Down are not mentioned in the rules. The published movie itself has 2 L+R and
    10 U+D frames, so they are accepted for this game.
  * The movie must sync on an accepted emulator. BizHawk is one, so NesHawk is fine.
* **Target:** beat 28,246 frames of gameplay, i.e. find **820+ frames (13.6 s)** against our current best stage
  results.
* **Where the 820 frames are, and the levers** (estimates of what an uncapped version of our solvers could take back):
  1. **Bases + base bosses: 544 frames (66 %)**: rooms ~374, bosses 145. This is mostly the press cap: our rooms sit
     exactly on the 5-frame-cap floor (T 293 for 8 HP) and the TAS is ~23 frames under it per room. Uncapped room
     planning (1 HP/frame, several cores per press, plated cores from T 33) should recover most of it **[E 350-500]**.
     The base boss fights need new plans; the TAS's are 64-80 frames faster.
  2. **Waterfall climb: 120 frames**: not the cap. Our climb waits at three rocks. Manipulating the rock spawns as the
     TAS does **[E 60-120]**.
  3. **Bosses outdoors: ~150 frames** (S8 61, S6 43, S5 29, S1 21): fire-rate/slot limited, so mostly recoverable
     uncapped **[E 80-150]**.
  4. Stage 7: nothing to gain against the TAS at our current level.
  * Sum of plausible recoveries: **about 490-770 of the 820**.
* **Honest estimate:**
  * With the press cap removed and the climb fixed, our approach could plausibly get **within about 1-5 s** of the
    TAS's gameplay.
  * **Beating it outright is unlikely (I'd put it well under 1 in 4).** Every stage would have to match frame-level
    work refined over 15 years of submissions (the last improvement was 8 frames), plus ~14,000 rerecords of
    lag/RNG polish. That work includes Y-subpixel control, frame rules (stage 3's 8-frame boss rule, stage 5's first
    tank), lag management and pause-based RNG control.
  * Porting to the JP ROM is a further project. It has different RNG, lag and base timing (`reference_run.md`: none
    of these movies sync on our US setup).
  * Staying on the US ROM is allowed, and the comparison is then exactly the gameplay table above.
* **Biggest single levers:**
  1. Uncapped base-room/boss planning (~0.5 of the gap).
  2. The waterfall rock timing (~0.15).
  3. 1-HP-per-frame boss fights in stages 5, 6 and 8 (~0.15).

## Method

* **Encode and frame rate:**
  * Measured in the built-in browser by seeking `(n + 0.5)/60` with the player paused and muted, and reading canvas
    pixels in the page. Nothing was downloaded.
  * The YouTube encode is 960x720 at 60.000 fps, 701.42 s long, with a ~2 s TASVideos card before power-on and the
    ending after the last input.
  * It is **not 1:1**: the background scroll steps 2 px once every ~601 video frames, so one NES frame is dropped
    per ~601-608 video frames. The archive.org MP4 shows the same pattern.
  * The 7 intermission-skip Start presses in the movie line up with the first black frames at
    `v = 0.998356 n + 120.5` (+-0.8, fitted slope 0.998337). So 1 video frame = 1.00165 NES frames, power-on is
    video ~120.5, and the last input (31,744) is video ~31,812. The heart's first explosion follows 7 frames later.
  * Power-on to the stage-1 medals = 449 frames. END to the last input = 230 frames [C/E]. Hence
    31,745 = 449 + 31,525 - 229 (consistent).
* **Ads:** a mid-roll ad pod (two ads) appeared once. The scan detects ad playback (duration/`.ad-showing`) and
  re-reads those frames; frames read during the ad were discarded and re-scanned. The archive.org MP4 was tried as
  an alternative, but its long GOPs make seeking too slow, so it was only used for the frame-rate check.
* **How each event was found:**
  * Stage starts: first frame with the blue medals.
  * Blacks: mean brightness.
  * Base onsets: a barrier-colour detector (red in Base 1, green in Base 2).
  * Waterfall scroll: vertical-shift tracking.
  * Boss events: magnified frame-by-frame contact sheets.
  * Tolerance: +-1 video frame for frame-exact events, +-2 near a resampling drop. "Approximate" events carry their
    own tolerance in the JSON.
* **Not measured:**
  * The TAS's control-lost frames other than stage 5, the stage 7 Barrier pick-up frame and the weapon pick-ups.
  * The stage 1 internal split, and lag frames.
  * Deaths in stages 5-8 (see above).
  * The JP code for the stage 3 and 7 exits.

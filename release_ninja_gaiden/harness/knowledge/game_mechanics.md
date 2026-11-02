# Ninja Gaiden (NES) game mechanics for speedrunning

Labels:
- **[TV]** TASVideos game resources page.
- **[S1119]/[S5222]/[S7532]** TASVideos submission notes (1119S, 5222S, 7532S).
- **[3223]** comment and subtitle notes inside the 3223M movie (`work/tas3223_notes.txt`).
- **[DIS]** 0xe1f disassembly notes.
- **[rec]** what I saw in the record video.
- **[replay]** seen in the BizHawk replay of 4751M.
- **[srcom]** speedrun.com guide or resource listing.

Nothing here has been tested by us in play yet.

## 1. Structure

- **6 acts. Each has 2-5 stages, and the last stage of an act is the boss.** Long stages are split into vertically stacked **rooms** (substages a, b, c...).
- An in-stage room change is a black screen of about 22 frames. [rec] [S7532]
- The full list of rooms, with the TAS's length for each, is in `dl/tas/text/7532S.txt`. The room and stage RAM values are in `ram_map.md`.

| Act | Stages (rooms) | Boss |
|---|---|---|
| I | 1-1, 1-2 | Barbarian (1-2) |
| II | 2-1 (a-d), 2-2 (a-c), 2-3 | Bomberhead |
| III | 3-1, 3-2, 3-3 | Basaquer |
| IV | 4-1 (a-c), 4-2, 4-3 (a-d), 4-4 | Kelbeross (two dogs) |
| V | 5-1, 5-2 (a-d), 5-3 (a-g), 5-4 | Bloody Malth |
| VI | 6-1, 6-2 (a-e), 6-3 (a-d), 6-4 (Masked Devil, then Jaquio), 6-5 | The Demon (the "demon statue"; the run ends on its heart) |

- **Fixed costs at a stage start:** 151 frames from the stage change (`$6D`) to control. Stage-to-stage transitions take 277 frames, and act transitions take about 744-749 frames including the Start-skipped cutscene. The TAS presses Start to skip every cutscene (frames 3147, 9674, ...). [S7532] [replay]
- **Act VI boss rush:**
  - Losing a life at the Masked Devil, Jaquio or the Demon sends Ryu back to the start of **6-1**. [community knowledge; the speedrun.com "Jaquio Tutorial All Strats" mentions "backtracking to 6-1 and coming back to him armed with spin slash"]
  - Do not die in Act VI.
  - Elsewhere a death restarts the current stage or room with full HP. A death costs the death animation, a reload, and the weapon and ninpo.
  - Lives start at 2 (`$76`). [DIS]
- **Score:** irrelevant to the board. Leftover ninpo and leftover timer are converted to points after each boss. [DIS]

## 2. The timer (it matters for the board clock)

- Each stage starts at TIMER 150. `$63` decrements when the sub-timer `$62` wraps, every 61 frames ("60-0"). [TV] [replay]
- **After each boss, the remaining timer is tallied at 3 frames per second.** Leftover ninpo is also tallied first, at 3 frames each per the TAS notes: ending a fight with spare ninpo costs frames. [TV] [S1119]
- **The sub-timer carries over between stages.** So for each boss there is a window of entry sub-timer values in which one more second ticks off during the fight, saving 3 tally frames. [TV]
  - Formula from TASVideos: with F = frames the sub-timer runs during the fight, F mod 61 = the largest useful entry sub-timer value.
  - The TAS shifted inputs by a frame here and there to hit these windows (Act III and IV notes in 7532S).
- **The board clock stops at TIMER 000 after the demon.** From the demon kill to the end costs 3 x (timer left) frames. One second (61 frames) faster at the demon therefore saves only about 58 frames; frames saved earlier save their full value. [derived; replay: 147 x 3 = 441 frames]
- Boss timers: "the timer will always tick to 149 on the same frame based on ranges of frames that the screen loads", which "sometimes means that the screen takes 3 frames longer to fade out after the boss is defeated". [S1119]

## 3. Movement

[TV unless noted]
- **Horizontal speed:** only 1.5 px/frame (running, or forward in the air), 0.5 (back in the air) or 1.0 (knock-back after a hit, uncontrollable until Ryu touches a wall or floor).
- **Jumps:**
  - Standing jump: rises 48 px and peaks 19-24 frames in. Pattern -4 x5, -3 x5, -2 x4, -1 x4, 0 x6, then falling.
  - Wall jump: rises 15 px and peaks 10-14 frames in. Pattern -2 x5, -1 x5, 0 x5.
  - Damage boost: rises 29 px and peaks 14-19 frames after the hit. Pattern -3 x5, -2 x5, -1 x4, 0 x6.
  - Ladders climb 1 px/frame.
- **Wall climbing:**
  - Ryu clings to any regular wall. Jumping off and re-grabbing climbs it; Up and Down climb only on ladders and steps. [DIS]
  - Human technique: the "Wall Climb Tutorial" by twin0mega (speedrun.com guide, https://www.twitch.tv/videos/310179594).
  - The practice ROM "Ninja Gymnasium" (speedrun.com resource `4hhdk`) trains it.
- **Recovery walljump:** get hit next to a wall, then wall-jump immediately. This cuts the uncontrollable knock-back, and a perfect one costs only one frame of back input. [TV]
- **Sticky floors:** landing on certain tiles (mostly platform edges, the "red" blocks) stops forward movement for 1 frame. Usually avoidable. When it is unavoidable, it is a free frame to throw a sub-weapon. [TV] [S1119] [3223]
- **Banned TAS movement (we cannot use it):**
  - L+R / U+D+L stops a new x speed being written. That gives full-speed backward air movement and half-pixel adjustments.
  - Entry-ladder shortcuts: Right on the load frame, then L+R to get inside walls.
  - "Wobbling" up the insides of walls with U+D+L.
  - [S1119] [S5222]
- **Vertical screen wrap:**
  - Taking a hit at certain y values (4, 5, 14, 15, 16, 25, 26, 35, 36, 45, 46, 55, 56, 65, 66, 75, 84, 93, 102, 111), or wall-jumping at y 73, 82 or 91, can wrap Ryu from the bottom of the screen to the top instead of dying.
  - The cause: falling speed has no cap, and the game only checks the bottom 8 px.
  - No known use. [TV]

## 4. Attacks, weapons, items

- **Sword:**
  - B swings. A jumping B is a normal slash; Down+B in the air is the regular sword and costs no ninpo even with Jump & Slash equipped. [DIS]
  - **The first sword attack after power-on cannot kill.** `$92` is 0 until the first swing, so the TAS "whiffs" once on its first jump. [TV] [3223]
- **Slash cancel (sword canceling):**
  - Down+B re-starts the swing, so Ryu can attack as fast as Down+B can be pressed and released (every 2 frames in a TAS).
  - This is the core of the Jaquio and demon fights.
  - Human tutorial: "Sword Canceling Tutorial by Duckfist" (https://www.youtube.com/watch?v=ylKs_JnBXuw).
  - The speedrun.com resource "MashyMashy" exists to practise "B with down" mashing for Jaquio.
  - [S5222] [srcom]
- **Special weapons:** Up+B spends ninpo `$64` on the weapon in `$C9`. [DIS] [TV]
  - Throwing Star `$81`: 3 ninpo, flies straight.
  - Windmill Throwing Star `$82`: 5 ninpo, passes through and comes back. The record uses it on most bosses.
  - Art of the Fire Wheel `$80`: 5 ninpo, three flames. The TAS uses it on 3-3, 4 frames faster than the Windmill.
  - Jump & Slash ("Spin Slash", "Bzzzt") `$85`: 5 ninpo per jumping attack, ends on landing.
  - Invincible Fire Wheel `$84`: time-out based.
  - Time-stop hourglass: freezes enemies about 5 s (`$D0` bit 7).
  - **Special weapons persist across screen and room transitions.** A weapon thrown just before a boss room can land a "free" hit on the boss (used at 3-3 and 6-4). [S5222] [3223]
  - The first jumping slash after using Spin Slash keeps the larger hitbox ("impossible" kills). [3223] [TV]
- **Lanterns (item containers):**
  - They hang as the screen reaches their column; slashing one drops the item. Contents: 5 or 10 ninpo, 5 or 10 points, health, 1-UP, sub-weapons, hourglass. [DIS]
  - A power-up vanishes after a timer (`$04E8-$04EF`).
  - Grabbing a power-up or passing through an enemy can cause a 1-frame lag glitch (one frame of lag, except at the end of 4-1). [TV]
- **Ninpo bookkeeping:**
  - Leftover ninpo is tallied after the boss and costs frames.
  - The TAS keeps its ninpo divisible by the weapon cost: "power remains 16, which modulo 5 is 1, means that 1 ninpo will remain at the end of the level, which loses 3 frames". [S7532]

## 5. Damage boosts and enemy manipulation

- **Damage boosts are central:** a hit gives a 29 px upward launch plus 1 px/frame of horizontal travel, and is used to skip climbs. Invulnerability is 60 frames (`$95`). [TV] [S5222]
  - The record's HP and the TAS's HP are spent as a resource. The TAS even takes a health pick-up mid-5-1 to afford more boosts. [S5222]
- **Global timer `$BF`** (0-255, +1 per frame from power-on) sets each tosser's throw delay (`$BF >> 1`) and throw speed. Only some arrival frames give a "good" tosser.
  - The tossers in 3-2, 5-1 and 6-1 are gatekeepers. Saving frames before them can change their pattern for the worse.
  - The TAS keeps "false frames" for this reason. [TV] [S7532]
- **Enemy subpixels are inherited** from the previous occupant of the same slot (new = old remainder + spawn). This changes birds' paths over long distances. [TV] [S7532] [3223]
- **Spawns:**
  - Levels are 16 px blocks. The spawn iterator `$B5` scans the room's spawn list about 8 entries per frame, so spawns can be delayed 1-3 frames.
  - One frame of backward movement can delay or cancel a spawn. Moving back can also re-spawn enemies ahead of Ryu for a boost. [TV] [S5222]
- **Drawing interrupts:** every 16 px of scroll (10-11 frames of running), enemy logic is skipped for a frame ("enemies freeze"). Ryu still moves, and can time things around it. [TV] [S5222]
- **Birds** home on Ryu: y +/-1 per frame, x speed +/-1/16 per frame. **Bats** spawn at Ryu's y - 16. **Cheetahs** turn around on the sticky block. **Tysons** (boxers) jump every 10 frames, and an interrupt landing on their action change delays their attack by about 10 frames. [TV]
- **Pre-kill** (Joecurr, 2022): kill an enemy or projectile on the exact frame it leaves the screen. Its death bit stays set, so the next enemy in that slot spawns dead. No TAS use found yet; it may help a human-legal route. https://www.twitch.tv/videos/1497514873 [S7532]
- **Knuckle's Skywalk glitch:** a projectile-shooting enemy is manipulated to enable sky-walking. https://www.youtube.com/watch?v=rIMaGYevbhk [S7532]
- **Taking damage on the frame a boss dies:** "3-3 actually does this". [TV]

## 6. RTA route landmarks (the record and the speedrun.com guides)

- **The "5-1 manip":** a standard RTA manipulation in 5-1 that sets up bird or tosser boosts. The record's runner missed it ("Without the missed manip, maybe a low 31 or high 30").
  - feos found a way to include it in the TAS that did not cost more than it saved. [S5222] [run comment]
  - The record still lost +157 frames to the TAS in 5-1 (`record_notes.md`).
- **Jaquio "plate kill":** the fastest human Jaquio strategy, which beats him "in 1 and a half cycles". The record got it. Tutorial: "Jaquio Tutorial All Strats" (https://youtu.be/s-A6dsb1MWQ, by TheRetroRunner). The guide also covers the Spin Slash backtrack to 6-1 as the slow, safe fallback.
- **CORRECTION 2026-10-24 (`ninpo_budget.md`):** the icons below were misread. Purple swirl = **Jump & Slash**, orange diagonal = **Windmill**, orange round flame = Fire Wheel (checked on NesHawk screenshots with known `$C9`). The record uses J&S at 1-2, 2-3, 4-4, 5-4 and 6-4a (one spin at the Masked Devil's orb) and the Fire Wheel at 3-3. Leftover ninpo after a boss costs 3 f per point (measured), and ninpo and the art never carry over between acts.
- **Record weapon route, from HUD icons [rec] (WRONG colours, see the correction above):**
  - Windmill Star at 1-2, 2-3, 4-2/4-4, 5-3/5-4 and 6-3/6-4a.
  - An orange icon (Fire Wheel or Jump & Slash) at 2-2, 3-2/3-3, 5-2 and 6-2.
  - No weapon at Jaquio and the Demon (sword only).
  - Ninpo at stage starts is in `record_notes.md`.
- **Speedrun.com guides:**
  - Arcus Beginner/Advanced Tutorials: https://www.youtube.com/watch?v=AJkCsI9nj04 and https://www.youtube.com/watch?v=x-cyeYr5bTI
  - ShuriBear "Any% Tutorial (2020)": https://youtu.be/_eMHhSLrDmQ
  - Sinister1 beginner: https://www.youtube.com/watch?v=GqKyAp_rU5M and https://www.youtube.com/watch?v=Z-MBNmAobdU
  - These are videos and were not watched for this report. Watching them for the human-legal wall-climb routes is a worthwhile next step.
- **Practice and analysis tools on speedrun.com** (the downloads sit behind Cloudflare; get them in a browser if needed):
  - maps with item markers by NESmaps (`6e1cr`)
  - hitbox viewer Lua (`xp7f4`, `het3o`, `go29z`)
  - Practice ROM v4.02 (`jwrxg`), with a stage select and global-timer freeze
  - FCEUX save states for every level (`ct710`)
  - Demon Head ROM (`18d1t`)
- **Level maps:** NESmaps (Rick Bruns); the disassembly's `gfx/stages/stage-bg-*.png` (`dl/NinjaGaidenNES/gfx/stages/`).

## 7. Lag and emulation

- **Lag frames:** the replay of 4751M logged `emu.islagged()` per frame (`work/tasrun/tas4751_ram.csv`, column `lag`). [replay]
  - From power-on to the board end (frame 39,525) there are only **32 lag frames**.
  - Almost all are at boot and at stage or cutscene transitions (for example 3146-3150, 9673-9677, 14414-14417, 16524-16530).
  - Gameplay itself barely lags, so lag is not a route factor (except the power-up pass-through glitch frame).
- **DPCM / controller-read conflict:** the TAS was resynced with Scumtron's "DPCM glitch detection tool" when it moved from QuickNES to NesHawk [S7532]. So, as in Contra, some controller reads are corrupted on NesHawk/console and not on QuickNES. **Use NesHawk for the final run; QuickNES is for exploration only.**
- Power-on RAM: "The game starts with some values un-initialized" (the Barbarian collision case) [3223]. Use BizHawk's default `InitialWRamStatePattern` (null, as in the TAS's SyncSettings) for reproducibility.

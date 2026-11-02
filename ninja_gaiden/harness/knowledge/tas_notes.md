# Ninja Gaiden (NES) TAS notes

Sources:
- TASVideos API `https://tasvideos.org/api/v1/publications?GameIds=175&ShowObsoleted=true` (saved as `dl/tas/pubs175.json`)
- the game resources page https://tasvideos.org/GameResources/NES/NinjaGaiden
- the submission pages 7532S, 5222S, 1119S, 1081S, 986S, 7602S, 10688S (text copies in `dl/tas/text/`)
- TASVideos game id **175** ("Ninja Gaiden", NES). Game id 1486 is the PC Engine game.

## 1. The current best Any% movie

**[4751] NES Ninja Gaiden by eien86 & Scumtron in 10:50.33** (https://tasvideos.org/4751M)

| | |
|---|---|
| Submission | #7532 (https://tasvideos.org/7532S), submitted 2022-06-09, published 2022-07-06. Judge feos, publisher EZGames69 |
| Branch / class | baseline (fastest completion), Standard |
| Emulator | BizHawk 2.8, core NesHawk. It was resynced from the submitted EmuHawk 2.7.0 + QuickNES movie with Scumtron's DPCM glitch-detection tool |
| ROM | Ninja Gaiden (U) [!].nes, SHA1 `CA513F841D75EFEB33BB8099FB02BEEB39F6BB9C`, MD5 `0C2CCCDA6BA6CAB7BEDE0FF05E7F6852`. The SHA1 is the same as **our ROM file's SHA1** (`Ninja Gaiden (USA).nes`; file CRC32 11F953F6, headerless CRC32 7C4A72D8). The bk2 header says BoardName SxROM |
| Length | 39,084 frames at 60.0988138974405 fps = 650.33 s. Rerecords 693 (bot-driven) |
| Start | power-on. Controller 1 only (`NesLeftPort: ControllerNES`, right port unplugged) |
| Timing method (TASVideos) | power-on to the last input. The movie ends on frame 39,084, the frame the demon's HP display `$66` reaches 0. The 147-second timer tally after that is not counted |
| Video | https://www.youtube.com/watch?v=z1AnlaNmCyI (publication encode). Submission video https://www.youtube.com/watch?v=0RjA5FfCuRs. Archive.org mp4 linked from the publication |
| Movie file | `dl/tas/4751M/eien86,scumtron-ninjagaiden.bk2` (read-only), unpacked in `dl/tas/4751M/bk2/` |
| Obsoletes | 3223M (10:50.36, by 1 frame) |

### It syncs in our BizHawk (verified 2026-10-19)

- I played the bk2 in **BizHawk 2.11.1 NesHawk** with a RAM-logging Lua script (`work/tasrun/tlog.lua`, private config, movie end action "finished" so the game ran on after the inputs).
- The stage and room changes land exactly on the frames in the submission's timing table: transitions at 4271, 5080, 5199, 6723, 7353 and so on; stage starts at 173, 3301, 6103, 9828, 14568, 22124, 30062 and so on.
- The demon's display `$66` reaches 0 at 39,084, the movie's last frame.
- **The movie syncs on 2.11.1 with our ROM.** The per-frame log is `work/tasrun/tas4751_ram.csv` (39,984 frames, including 900 frames after the movie). The stage events are in `work/tasrun/tas4751_stage_events.json`.

### Its time under the board's rule

- START = first frame with `$33 == 0x97`: **frame 174**. On that frame `$63` (seconds) = 149 and `$62` (sub-timer) starts counting. Ryu moves on 175.
- END = first frame with `$63 == 0` in stage `$6D == 21` (6-5) after `$66 == 0`: **frame 39,525**. `$1FD` goes 0xD5 to 0xD6 three frames later (39,528). That D5-to-D6 change is the autosplitter's final split.
- **Span 39,351 frames = 654.78 s = 10:54.78.**
- The moderators time from the picture, not RAM: Ryu visible (about 2 frames after control) to TIMER-000 drawn. **Board-equivalent time for the TAS: about 10:54.76 +/- 0.05 s**, which is **37.4 s faster than the record** (692.183 s).
- The stage-by-stage comparison is in `record_notes.md` section 6.

### Techniques in the movie (author notes)

- **Breadth-first bot routing:** Jaffar (https://github.com/SergioMartin86/jaffar), on QuickNES at about 1.6M states/s on a 64-core Threadripper.
- **Bird simulator:**
  - Birds accelerate toward Ryu at 1/16 px per frame.
  - A bird inherits the low byte of its position from the last enemy in the same slot.
  - Enemy routines are skipped on the frame of each 16 px scroll interrupt.
  - The simulator found a 2-frame faster 4-2 and nearly matched 5-1.
- **Weapon route, by act:**
  - Act II: Spin Slash (Jump & Slash, "Bzzzt") instead of the Windmill Star.
  - Act III: Throwing Star, used to pick up the **Fire Wheel** in III-1a. The Fire Wheel is 4 frames faster on the 3-3 boss than the Windmill Star. They throw 5 stars to land on the right ninpo and timer phase.
  - Act IV: bird boost after a turn-around.
  - Act V: the 10-ninpo pickup in 5-2 is skipped (the only true frame saved); two V-3f enemies are left alive to save 5 ninpo.
- **Global-timer gatekeepers:** the "tosser" enemies (III-2a, 5-1, VI-1) behave by the global timer `$BF`. Some local frame saves become **false frames**: frames saved early are thrown away later to wait for a good timer.
- **Future work (their words):** false frames; **pre-kill** (Joecurr: kill an enemy on the frame it leaves the screen, so the next enemy in that slot spawns dead, https://www.twitch.tv/videos/1497514873); "Knuckle's Skywalk Glitch" (https://www.youtube.com/watch?v=rIMaGYevbhk).

### Banned inputs in the TAS (counted from the input log)

| Movie | Frames | L+R frames | U+D frames |
|---|---|---|---|
| 4751M any% (current) | 39,084 | 1,221 (131 events) | 3,430 (1,778 events) |
| 3223M any% (previous) | 39,086 | 1,807 | 948 |
| 4812M pacifist | 40,680 | 1,809 | 2,944 |
| 7355M damageless (JP ROM) | 39,437 | 1,607 | 498 |

- **Every published movie relies on Left+Right and Up+Down.** These are banned by the board (L+R) and by the linked general rules (U+D).
- What they do (submission 5222S/1119S):
  - L+R or U+D+L stops a new horizontal speed being written. That gives full-speed backward air movement and pixel-precise adjustments.
  - On screens that start on a ladder, Right on the load frame plus L+R lets Ryu **get inside walls** and climb pseudo-walls.
  - U+D+L "wobbling" up the inside of walls.
- Scumtron's 2006 notes estimate up+down+left saved "roughly 300 frames" and getting inside walls "roughly 180 frames" over the previous TAS.
- **Rough estimate of a legal-input TAS:** 10:54.8 plus 8-15 s, so about 11:03-11:10 under board timing. This is a guess to be refined by our own search. It would still be 22-29 s under the record.

### Press rate in the TAS

The TAS slash-cancels every 2 frames, mashes A and Up/Down at 30 a second, and its B peaks at 25 presses in 60 frames. See `record_mash_rate.md`.

## 2. Every NES Ninja Gaiden publication

| Pub | Title | Emulator | Frames | Date | Movie file (in `dl/tas/`) |
|---|---|---|---|---|---|
| 255 | by BoltR in 11:20.28 | FCEU 0.98.12 | 40,817 | 2004-12 | not downloaded |
| 258 | by BoltR in 11:18.62 | FCEU | 40,717 | 2004-12 | - |
| 470 | by Slotermeyer in 11:14.02 | FCEU | 40,441 | 2006-02 | - |
| 487 | by Slotermeyer in 11:05.82 | FCEU | 39,949 | 2006-02 | - |
| 539 | by Scumtron in 11:02.47 | FCEU | 39,748 | 2006-05 | - |
| 562 | by Scumtron in 10:52.68 | FCEU 0.98.15 | 39,161 | 2006-07 | `562M/scumtrom4-ninjagai.fcm` |
| 3223 | by Scumtron, MESHUGGAH, feos, Xipo & Marx in 10:50.36 | FCEUX 2.2.3 | 39,086 | 2016-09 | `3223M/...ninjagaiden.fm2` (has 84 comment and subtitle lines of technical notes, extracted to `work/tas3223_notes.txt`) |
| **4751** | **by eien86 & Scumtron in 10:50.33** | BizHawk 2.8 NesHawk | 39,084 | 2022-07 | `4751M/...bk2` (current) |
| 4812 | "pacifist" by MESHUGGAH, eien86, feos, Marx, jprofit22 & Scumtron in 11:16.89 | BizHawk 2.8 | 40,680 | 2022-08 | `4812M/...pacifist.bk2` (Alternative class) |
| 7355 | "damageless" by FourLi39 & Rum in 10:56.203 | FCEUX 2.2.2 | 39,437 | 2026-09 | `7355M/...damageless.fm2`. **Japanese ROM** (Ninja Ryuuken Den, SHA1 fcd14af7...), which does not match ours. The judge notes "the game also plays fine in the US version" |

- The pre-2016 movies are FCEU-era and only of historical interest.
- 3223M uses our US ROM. Its FCEUX checksum `B8G5Kum3jyCQdajMbT7r8A==` decodes to MD5 `07c1b92ae9b78f209075a8cc6d3eebf0`, which is the MD5 of our ROM without the iNES header (I checked). It would need resync work for BizHawk.

## 3. What this means for our plan

- **Our first target** is a legal-input, press-capped run under board timing.
  - Start from the TAS's route and boss strategies.
  - Re-solve every L+R and U+D section (the wall-climbing stages 2-1, 2-2, 4-3, 5-1, 5-2, 5-3, 6-2, 6-3), with no L+R and no U+D.
- **The record's biggest gaps to the TAS** are the same wall-climbing stages (about 1,670 of 2,248 frames) plus Jaquio and the demon (about 314 frames). The bosses 1-2, 2-3, 4-4, 5-4 and 6-4a are near-TAS already.
- **"TAS-mode attempt"** (after the legal run): the 4751M movie already syncs in our BizHawk, so it is a ready baseline to beat (10:54.78 board time, 10:50.33 TASVideos time). TASVideos rules allow L+R, so a TAS-mode attempt could use it.

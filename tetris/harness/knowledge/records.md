# NES Tetris (Nintendo, NTSC, 1989): human records on 2026-11-13

Researched on the web on 2026-11-13 (nothing from memory; pages only, nothing downloaded). Two blocks: the timed
categories on speedrun.com (read through its API the same day) and the endurance records the classic-Tetris
community tracks on its own sheet. "Gym" = TetrisGYM, a modified ROM (uncapped score, crash triggers off).
‡ = read off the on-screen counters or timestamps of the record video by the research pass, not stated in writing.

## 1. Timed categories (speedrun.com/tetrisnes)

Rules common to all: real time, video required, emulators allowed (FCEUX, Nestopia, BizHawk, Mesen, OpenEmu
named), PAL has its own boards, and "use of turbo, L+R or U+D, save states, and tetris demo glitch are banned".
The linked general NES rules add: no RAM watch, no rewind, and "submitting a movie file or a recording of a movie
file playing not allowed" (so a bot run can never go on the board; it is a demonstration, like the TMNT one).

| Category | Rule (timing) | Runs | Record | Holder | Date | Platform |
|---|---|---|---|---|---|---|
| **100 Lines** | any start level; from level select until the lines counter shows >= 100 | 239 | **2:43** (video title: 2:43.54) | Cheez | 2022-03-07 | console, level 19 start |
| 100 Lines, Level 0 Start | same, start at level 0 | 306 | 3:42 | SodumOversdoes | 2020-03-29 | Mesen |
| 300K Points | from level select until the score shows >= 300,000 | 71 | 1:35 | TegaMech | 2021-09-14 | console |
| B-Type Height 0-5 | all six heights in order, any level each, cutscenes play; ends when SUCCESS appears on height 5 | 20 | 5:42 (5:42.58 on the runner's timer) | Gwafey | 2025-01-08 | console, level 19 on every height |
| Level 0-19 (misc.) | level 0 start until the transition to level 19 at 190 lines | 17 | 7:04 | (user 8v5onynj) | 2020-04-17 | console |

100 Lines top of the board: Cheez 2:43 (2022-03-07), EricICX 2:49 (2022-03-06), Gwafey 2:55 (2024-04-15), TegaMech
2:56 (2021-09-30), HeyoNight 2:59 (2022-06-20), PixelAndy 3:04 (2021-05-31). All level 19 starts, all console.
Runs per year on that board: 25 in 2024, 17 in 2025, 17 so far in 2026, so it is still played; the record has
stood since March 2022.
Record videos: 100 Lines https://www.youtube.com/watch?v=T2uQ6I-eM6I (854x480, 30 fps, 2:55 long);
B-Type https://www.youtube.com/watch?v=FE9GZAAjRJU (1280x720, 60 fps).

What the community says about routed runs (forum threads by TegaMech, the 300K record holder): RNG manipulation
"is not mentioned at all by the rules, and therefore by default allowed" (thread from about 2021); a late-2025
thread describes how a person does it (power on, start the game on an exact frame, never push down on level 19 so
every piece takes a known time, replay a route built in a TAS editor) and argues for allowing it on the main board.
He also writes that in the 100 Lines record "approx 7 seconds was lost due to poor longbar timings".
A routed game by a person exists: TegaMech, 1,616,360 points, 615 pre-routed pieces on an original cartridge with
DAS only and frame-perfect power-on/start inputs (video 2026-02-05, https://www.youtube.com/watch?v=PR6T5DO4k4A).

## 2. Endurance records (community sheet, all A-Type)

| Record | Value | Holder | Date | Rules | Length |
|---|---|---|---|---|---|
| Highest score, any ROM | 40,264,954 | Blue Scuti (Willis Gibson) | 2025-12-06/07 | Gym‡, level 19 start‡ | about 2 h 21 min‡ |
| previous | 29,486,164 | dogplayingtetris (Michael Artiaga) | 2024-10-05 | Gym, L19 | 2:01:33 |
| before | 16,700,760 | Alex T (Alex Thach) | 2024-04-15 | Gym | about 1 h |
| Highest score, unmodified cartridge | 6,850,560 (screen stays at 999999) | Blue Scuti | 2023-12-21 | original ROM, ended in the crash | about 38 min‡ |
| Level 29 start | 18,862,720 | Blue Scuti | video 2024-05-22 | Gym‡ | 1 h 02 min |
| Hypertapping only | 2,382,340 | moja314 | video 2024-12-06 | level 18 start | 19 min |
| DAS only | 1,384,416 | Mark Migas | video 2026-08-07 | DAS | 12 min |
| Highest level / most lines | level 373 (shown as 117), 4,479 lines‡ | Blue Scuti | 2025-12-06/07 | Gym‡ | same game |
| First game crash | level 157, 1,511 lines | Blue Scuti | 2023-12-21 | original ROM | about 38 min‡ |
| Earliest possible crash (level 155) | 6,787,420 | fractal161 (Justin Yu) | 2024-01-03 | original ROM | |
| Rebirth (level 255 wraps to 0, at 3,300 lines) | first: 1:21:24 to the wrap | dogplayingtetris | 2024-10-05 | Gym | 2:01:33 |
| | second and third | Alex Thach (video 2025-11-01), Blue Scuti (2025-12-06/07) | | Gym‡ | 1:48‡, 2:21‡ |
| Lines to maxout (999,999) | 163.91 lines, about 5 min 10 s‡ | Blue Scuti | video 2025-03-30 | | |

No human rebirth on the unmodified cartridge and no double rebirth were found. There is no timed "fastest
maxout" or "fastest crash" board: the sheet counts lines, not seconds.

Tap speed: DAS is a fixed 10 Hz (16-frame delay, then a shift every 6 frames). Hypertappers 14-19 Hz (moja 20+).
Rolling "consistently over 20" per second (Cheez, 2021), "up to 30" (Ars Technica, 2024); seven readouts of the
Hz counter in Blue Scuti's 29-start record gave 18.8-24.0 Hz burst averages‡. 30 Hz is the game's ceiling (a
press needs a released frame before it). These are bursts of up to five or six taps, not continuous tapping.
Our own measurements of the two speedrun records are in plan.md.

Bots on this game: BetaTetris (Adrien Wu) did a rebirth on the original ROM with crash dodging at 30 Hz (video
2024-01-22); StackRabbit (Greg Cannon) reached 102,252,920 with a scoring mod (2021). TASVideos has "maximum score"
02:53.13, "Mode B" 00:36.89 and a playaround; no 100-line movie. None of these files is used or loaded here.

## 3. Disagreements and gaps

- Dog's rebirth: 5 Oct (tetrisinterest) or 6 Oct 2024 (Wikipedia).
- First crash: 1,511 lines (Ars, video) or 1,510 (biggieblog); Guinness dates the record 26 Dec 2023.
- That the 2025 rebirths were on Gym is read from the on-screen HUD, not stated in writing.
- Not confirmed: highest score at a real crash, any human fastest-crash time.

## Sources

- speedrun.com API: /api/v1/games/tetrisnes?embed=categories, /leaderboards/3dxzqv1y/category/<id>, /games/3dxzqv1y/records
- speedrun.com forum: https://www.speedrun.com/tetrisnes/forums/ky1v4 , https://www.speedrun.com/tetrisnes/forums/xu0hz
- General NES speedrun rules: https://docs.google.com/document/d/1apP69VDIzUx-iVO_sj5YjTxBAE2ukHPa6kl33AOW9hA
- Community leaderboard sheet: https://docs.google.com/spreadsheets/d/1ZBxkZEsfwDsUpyire4Xb16er36Covk7nhR8BN_LPodI/htmlview
- Tap-only sheet https://docs.google.com/spreadsheets/d/1KkW7U8E5lQU1HA-Vlc_hUEeNF30Z7MIdEI2wCDNlRXQ/htmlview ;
  DAS-only sheet https://docs.google.com/spreadsheets/d/1OR0kGUJdC2AyIhM4BftCg3Tc9786AlBybcc5D85YBHY/htmlview
- https://nestetris.com/worldrecords.html ; https://kottke.org/26/09/0049585-previous-record
- Blue Scuti 40M https://www.youtube.com/watch?v=nt2QNJLk1MY ; first crash https://www.youtube.com/watch?v=J9oVQ43j22g ;
  29-start https://www.youtube.com/watch?v=dHdYU51pm2o
- Dog rebirth https://www.youtube.com/watch?v=fXhbti5SneE ; Alex Thach rebirth https://www.youtube.com/watch?v=4NXe_fb2eFU
- https://tetrisinterest.com/dog-becomes-the-first-player-to-achieve-rebirth-in-nes-tetris/
- https://arstechnica.com/gaming/2024/10/nes-tetris-first-ever-rebirth-loops-past-level-255-and-back-to-zero/
- https://arstechnica.com/gaming/2024/01/someone-has-finally-beaten-nes-tetris/
- https://www.guinnessworldrecords.com/world-records/607869-highest-score-on-nes-tetris-ntsc
- https://en.wikipedia.org/wiki/Classic_Tetris ; https://tetris.wiki/Tetris_(NES,_Nintendo)
- https://cardiffstudentmedia.co.uk/nes-tetris-faster-than-hypertapping/ ; https://biggieblog.com/celebrating-the-first-nes-tetris-game-crash/
- Bots: https://www.youtube.com/watch?v=yBOfsnBQ5i0 (BetaTetris), https://github.com/GregoryCannon/StackRabbit ,
  https://meatfighter.com/nintendotetrisai/ , https://tasvideos.org/4853M

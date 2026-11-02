# Ninja Gaiden (NES) board rules, verbatim

Fetched 2026-10-19 from the speedrun.com API. Raw copies are in `dl/api/`:
- game rules: `v2game.json`, from `https://www.speedrun.com/api/v2/GetGameData?gameId=lde39l63`
- categories and variables: `game.json`, from `https://www.speedrun.com/api/v1/games/ngnes?embed=categories,levels,variables,platforms,regions`
- the linked Google doc: `rules_doc.txt`, from `https://goo.gl/pYN6AR`, which redirects to `https://docs.google.com/document/d/1apP69VDIzUx-iVO_sj5YjTxBAE2ukHPa6kl33AOW9hA` (exported as text)

Game id `lde39l63` (abbreviation `ngnes`). Ruleset flags: show-milliseconds true, require-verification true, require-video true, run-times `realtime` only, emulators-allowed true.
Platforms: Nintendo Entertainment System, Wii Virtual Console, NES Classic Mini, Switch, MiSTer, Analogue Nt, Analogue Nt Mini.
Regions: USA / NTSC, EUR / PAL, JPN / NTSC. The board has no region sub-category, so US and JP runs share one board (beco's #8 run is JPN). There are **no variables** (no sub-categories) and **no per-level boards**.

## Game rules (apply to every category)

```
General:

- Timing starts when you gain control of Ryu.
- Timing ends when the timer reaches 000 after defeating the demon statue.
- Reset/power on from the previous run must be included in your run submission video.
- Left+Right is not allowed.
- Turbo is not allowed.

Emulator specific:

- Specify the emulator used in the run and its version in the comments.
- Always enable your input display and frame counters as well as "no movie" when applicable. 
- MESEN Emulator Specific: Use of run-ahead is NOT permitted. Please capture the entire emulator window to rule out the possibility of the movie player being used.
- MESENRTA Emulator: Please consider using this emulator over MESEN as it provides the same accurate emulation and also gives assurance to mods that certain features of MESEN are removed that make cheated runs harder to detect.  MesenRTA: https://github.com/threecreepio/mesenrta/releases

Controller Specific:

- Swapping controllers is permitted but only between stages. (For example: 3-1, 3-2 or a boss room)
- A separate set of key bindings for the same controller is permitted, but will be treated as a second controller. Do not use two keys or buttons for the same game input within a single stage or boss room.
- Mapping multiple inputs to a single key/button is NOT permitted. (For example: Down + B to one key)

Approved Emulators for Mac Users:

- Nestopia
- OpenEmu

Banned emulator(s):

- Gotvg
- Retroarch
- Jnes

(Please note that a stricter enforcement of some of these rules may only apply to competitive times)

For additional rules, please consult this google document, https://goo.gl/pYN6AR
```

## Category rules

### Any% (id `ndx8vvkq`, 1 player) - our category

```
- Beat the game!
- Please do not use milliseconds for runs 11:50 and above.
```

### Low% (id `wdmqp32q`)

```
- Only allowed to kill enemies with your sword!
- Not allowed to pickup health!
- Not allowed to pickup fire armor/time stopper!
- Beat the game!
```

### Pacifist (id `w20z9odn`)

```
- Not allowed to kill any enemies!
- Not allowed to use ninpo on enemies!
- Bosses need to be damaged with sword only!
- Not allowed to pickup health!
- Not allowed to pickup extra lives!
- Not allowed to pickup fire armor/time stopper!
- Beat the game!
```

### Damageless (id `9kv67q32`)

```
Beat the game without taking any damage. This includes the head from the Demon.
```

### 100% (id `vdozw49k`)

```
Player must slash and collect every item container!

Beat the game!

If a player restarts a screen for any reason, all item containers must be recollected.

In certain instances item containers can respawn when you are still on that screen. Respawned item containers do not need to be collected twice.

*** UPDATED RULE:  A glitch will sometimes cause unopened item containers to despawn, you are not required to collect those item containers.  This is most common in 4-2 and 5-2 ***
```

### 2P1C (id `9d8o0862`, archived, misc)

```
2 Players 1 Controller any%

All any% rules apply
```

## The linked Google doc ("General rules for speedrunning NES games"), full text

```
General rules for speedrunning NES games.

Rules can always be slightly different on a game by game basis, but this aims to cover most of the general rules.

Video
* Submissions must include a video. Submitting only splits is not acceptable. No vid no did.
* Game capture should be the proper 4:3 aspect ratio, and not stretched to fit in a 16:9 layout, for example.

Turbo/L+R
* Turbo is not allowed as it provides an unfair advantage. There may be a few exceptions regarding JRPGs, but there is an overarching rule that turbo is not allowed.
* Left+Right or Up+Down is not allowed.

Save states
* Save states may not be used to start a run (ie skip a long intro), or at any point during a run. Doing so can unfairly manipulate RNG, whether knowingly or not.

Emulator
* Include Emulator and version used in submission notes.
* Mesen, Bizhawk/NEShawk, puNES, Nestopia and FCEUX are the most acceptable emulators, listed in order of accuracy, most other emulators are not accepted. Retroarch should not be used.
* It is preferred that the entire emulator window is captured, to help prove the emulator being used.
* Recommended to use input display, frame counter and have "No Movie" showing to help prove legitimacy.
* RAM and memory watch features are not allowed, as they provide an unfair advantage that is not possible on console.
* Remapping buttons during a run is not allowed.
* Mapping multiple buttons to one key is not allowed.
* Rewind features not allowed.
* Submitting a movie file or a recording of a movie file playing not allowed.

Flash cart
* If doing runs from a flash cart, include which one is used in submission notes, ie Everdrive, Powerpak

Game audio
* Always recommended to have game audio playing. Lack of game audio may be grounds for a run getting rejected, as it makes cheating (splicing) harder to detect. Rejecting a run for this reason is at the discretion of a games mods.

Reset/Power on
* Recommended to always include the reset/power on from the previous run in your submission. This helps to show that the run was not started from a save state or a movie file.

Streaming
* While not required for every run, it is highly recommended that runs are livestreamed. This lends another amount of credibility to a run if it is done on stream. Certain games require streaming of attempts below a certain time, again this is on a game by game basis.

Proofcall/Skill check
* Sometimes in the case of a WR or top time from a new runner of a game in a very short time, a skill check may be requested to demonstrate that a runner has the skills shown in their submitted run. This is not a sign of disrespect, simply a double check to corroborate the skills shown by the runner. This is purely on a run by run basis and at the discretion of a games mods to request one.

Frame drops
* While some amount of frame dropping can be unavoidable, gratuitous frame drops may be grounds for rejection. If large portions of a run are 'frozen' due to frame drops, this makes it harder to determine if a run is legitimate. It is always recommended to record locally to avoid this problem.
```

## What the rules mean for us (my reading, not the board's words)

- **Clock:** from gaining control of Ryu in 1-1 to TIMER 000 after the demon. The moderators timed the record from the first video frame where Ryu is **visible** to the first video frame showing **TIMER-000** (`record_notes.md`).
- **Banned inputs:** Left+Right (game rules). The linked doc also bans **Up+Down**. Every published TAS of this game uses both, a lot (`tas_notes.md`).
- **Turbo:** banned. No number is given, so we need our own press cap (`record_mash_rate.md`, `project_rules.md`).
- **Glitches:** the rules ban none. Wall-clipping, damage boosts, sword (slash) canceling, enemy manipulation and pre-kills are all legal as long as no L+R or U+D is used.
- **ROM:** no version requirement. JP runs are accepted on the same board, and BizHawk/NesHawk is an approved emulator. Our ROM is the US cart (see `research.md` section 1).
- **Save states:** banned during a run, and the run must show the reset or power-on. For us that means every movie starts from power-on.
- **Category-specific:** Any% has no extra restrictions.

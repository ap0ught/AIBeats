# Battletoads video: voice-over cards

Record **one audio file per section**, named after the section number, for example `03 is it possible.m4a`.
Drop the files in `toads/yt/voice/`. The picture gets cut to your read, so take as long as you need. Pauses and
retakes are fine, because the silences get trimmed.

The quoted lines are only starting points. Say it your own way.

---

## 01 · Opening montage (about 15 s)
Music and game sound only. Optional single line over the last shot:
- "This is an AI playing Battletoads."

## 02 · You asked for it (about 25 s)
On screen: 10–15 s of the best of the Zelda video (the emulator grid, the Darknut fight with the planner's lines, the
route map), then your four YouTube comments slam in.
- "Last time, an AI taught itself to speedrun Zelda."
- "A lot of you asked for the same game next." (the comments slam in here)
- "So we did Battletoads."
- Call to action: "This video exists because of your comments, so keep them coming, and subscribe if you want to see what it
  plays next."

## 03 · Is it even possible? (about 55 s)
- Battletoads' reputation: one of the hardest NES games ever made. The Turbo Tunnel ended a generation of childhoods.
- The human world record: **12:29.25**, by jay_cee.
- The AI plays by the human speedrun rules (speedrun.com Any%, No Credits Warp):
  - the hidden warps in levels 1, 4 and 6 are allowed ("so, Animebryan2: warps")
  - no credits warp, which is a memory-corruption trick
  - no impossible button presses like Left and Right together, and no turbo
  - the clock starts when the toad lands
- "Goal one: just beat the game. Goal two: beat twelve twenty-nine."

## 04 · How to read the screen (about 30 s)
A frozen frame with arrows pointing at each part:
- **The controller:** the buttons it's pressing, every frame.
- **WHAT / WHY:** what it's trying to do right now, and why.
- **The token counter:** how much AI thinking it took to work this part out, and what it was spent on.
- **The timer and the level bar:** the speedrun clock, and the record's pace in gold.

## 05 · Day 1: power on (about 1:45)
- Claude Code wrote a bridge into the emulator, so it can step one frame at a time, save and load states, and read memory.
- It started blind. It found where the toad's position, health and enemies live by pressing buttons and watching
  which numbers in memory change.
- Research day: the speedrun rules, notes from published TAS runs, and a fan's breakdown of the game's code.
- It found the Level 1 warp in memory. Level 1 takes under five seconds.
- The key idea: "The AI doesn't play the game. It writes programs that search for the inputs. Then a script plays them
  back."

## 06 · Goal one: just beat it (about 2:30)
One beat per level:
- **Turbo Tunnel:** the full bike ride, walls coming at 12 pixels a frame, solved by search.
- **Arctic Caverns (Level 4):** the pit after checkpoint 5.
- **Karnath's Lair:** the snakes are the platforms. Ride them, then the warp.
- **Terra Tubes:** swimming is about three times slower than walking, and a current kept dragging the search down.
  It ended up following a TAS's line along the water.
- **Rat Race:** kick a falling rat and the whole level ends. That's allowed on the board.
- **Clinger-Winger:** keep top speed or the Buzzball catches you. Done in one evening.
- **The Revolution tower, then the Dark Queen.**
- Failure reel: deaths, searches that ran for hours and found nothing, and the AI killing its own jobs by accident.
- "Day five. Game beaten. Eighteen oh-four." (pause) "The record is twelve twenty-nine."

## 07 · Goal two: shaving seconds (about 3:00)
- It measured every level against the record. The biggest losses were the Turbo Tunnel, Level 4 and the tower.
- **The Turbo Tunnel skip, worth 128 seconds:**
  - The record uses it. Crash into the gap before the first checkpoint, and when you respawn the game reads its
    own variables as level data.
  - It walks through memory until it finds a 127, and 127 means "level over".
  - The AI read the game's code to understand why, then rebuilt it frame by frame.
- **Level intros, about 20 seconds:** a button press skips each intro page.
- **Chaos:** change anything early and the game's random numbers change for everything after it, so every later
  level had to be re-fitted.
- The chart drops: 18:04, 12:58, 12:37, 12:34, 12:31.
- **The tower:**
  - It kept losing time waiting for platforms.
  - The record holder has to wait too, so the waiting itself wasn't the problem.
  - It studied a TAS frame by frame and copied how it uses the waits. That was worth about five seconds.
- 12:28.60: the record falls. You kept going for a bigger margin, and got 12:23.39.
- **Integrity checks:**
  - Every run is replayed twice from power-on and has to match exactly.
  - It found one banned Up+Down frame hiding in the run, removed it, and got the same result.

## 08 · What's a TAS? (about 30 s)
- A TAS is a tool-assisted speedrun: built on an emulator with save states, then played back as a file of button
  presses. This is one.
- The difference: most TASes are built by people, frame by frame, often over months. This one was built by an AI
  writing its own search tools, in 12 days, and it kept to the human rules, which normal TASes don't.

## 09 · Claude, by the numbers (about 30 s)
- 12 days, 5,388 AI replies, about 3 billion tokens, about $1,327 at API prices. If you're on a subscription, say
  what you actually paid.
- Most of those tokens are the AI re-reading its own notes and context as it works.

## 10 · The run: voice pop-ins (record each as its own short file)
- `10a`: Level 1 warp, "under five seconds".
- `10b`: Turbo Tunnel, "watch the gap".
- `10c`: rat boot.
- `10d`: the tower.
- `10e`: final hit, "twelve twenty-three point three nine".

## 11 · Outro (about 40 s)
- Quick thank-you to the sources (they're on screen).
- Call to action 1: "What should it play next?" (Zelda II, Contra, TMNT…)
- Call to action 2: "What did it do wrong? Where would you have saved time?"

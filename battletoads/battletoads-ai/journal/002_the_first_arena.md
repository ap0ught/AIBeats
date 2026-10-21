# 002 — The first arena (day 1, 2026-09-26)

## The fastest way into the game (measured, from power-on)

- Hold **Right from frame 1**. With a direction held through the logos, the title accepts Start at **frame 1,170**;
  with nothing held it waits until 1,519. Bisected: 1,163–1,169 are ignored, 1,170 works. **349 frames saved.**
- Press Start at 1,170, then **hold A**: story pages skip the moment they allow it. Nothing / Start / Select /
  directions are all slower; mashing Start restarts the story loop instead.
- Level 1 begins (byte $0F → 255) at 1,901; the toad lands and answers Right at **1,918**. Old path: 2,804.

## The memory map (all from diffing RAM dumps, no documents)

| what | where | how it was found |
|---|---|---|
| camera (level progress) | $87 | the only byte climbing while Right is held after an arena clears |
| lives | $11 | 3 at start; splits random attempts into 3/2/1 |
| health | HUD tiles $1C9–$1CE (244 = full) | six squares, two lost per hit |
| toad | object slot 13: X $3FD, Y $41B, Z $475 | Right/Left move X, Up/Down move Y, A (jump) arcs Z |
| enemies | object slots 14, 16–18 (same arrays) | slot 15 rides on the toad and is not an enemy |
| title accepts Start | $12 = 255 | |

Wrong turns, kept because they happened: $343 looked like health (5→4→3→2 on hits) and is not. $3B3 counted
4,3,2,1,0 up to a pig's death and is a timer. $4C2 counted hits 1–4 and is an animation clock. Enemy health is
still unknown.

## Brute force, three ways

1. **Random** (120 attempts × 25 s, six emulators, 61 s): not one scrolled the screen. A few emptied the arena,
   slowly, losing health. The arena does not open by walking right; it opens when the pigs are dead.
2. **Beam search** (every 16 frames, 20 moves from each of the best 6 states): two kills, full health, then
   stuck. It had no reward for a punch that lands, only for a death.
3. **Beam + random playouts** (each move scored by the best of 2 random 64-frame futures): **arena clear at
   1,184 frames from control, no damage, camera scrolling.** 171 s of search. The playouts stand in for the enemy
   health byte we could not find.

Verified: the whole route (power-on → arena cleared) replays from power-on to the same RAM, SHA-1 `87211897…`.

## Video
- `video/day1_first_arena_overlay.mp4` — power-on to the clear, with the panel and the token counter.
- 120-toad ghost grid source: `shots/brute/L1_arena/`. Every random attempt's final frame.
- Recordings of every experiment: `video/*.mkv`.

## Tokens
17.6M tokens, ~$16 to this point (priced per reply by model: Fable 5.1 earlier in the session, then Opus 4.8,
then Opus 5.5 by the owner's choice).

## Next
The rest of Level 1 with the same search, stopping at each arena; then checkpoints per section like Zelda's
segments. Find enemy health properly (it would make the search much cheaper). Keep an eye out for anything the
game does that a human would never try — that is where a new trick would come from.

## Rule change (owner, same day)
The clock starts when the toad lands in Level 1, so the intro is no longer timed. The blind rule is lifted:
decoding the ROM, reading guides and TAS notes, and watching the 12:29 record are all allowed now. Day one was
done blind; everything after this line may use outside knowledge, and the journal says where each piece came from.

## After the arena (same day, later)
- Walking on from the cleared arena: the camera byte $87 parks at 97 and nothing else scrolls smoothly. The level
  is arena-based; the screen moves between fights, not during them. $B5 and $0C rise at half a unit per frame even
  standing still: timers, not a camera.
- The next enemy is a tall yellow giant in **object slot 15**, the slot I had excluded as "riding on the toad" (it
  merely shared the toad's spawn point). Walking into it and punching every 16 frames kills the toad twice.
- $34F counts 18→1 then 12→1 at a fixed cadence (every 33, then 67 frames) whether or not a punch lands: a timer.
  Enemy health is still not found; three candidates so far were all clocks.
- The playout search stopped on a false kill: the giant's slot flickers empty before it spawns, which reads as a
  death. Kill accounting needs "was alive, then empty for 20+ frames".
- ROM: mapper 7 (AxROM), 256 KB PRG, CHR-RAM, 8 banks of 32 KB. Text is not ASCII in the ROM (the level name in
  RAM at $700 is decoded at runtime), so string search finds nothing.

# 001 — Power on (day 1, 2026-09-26)

Rules for this one: glitchless (warps allowed, they are designed; clipping, wrong warps, corrupted state are not),
blind (no guides, no maps, no runs, no disassembly; the cartridge and RAM are the only sources; one exception, the
category's timing rules), verified from power-on, filmed from hour one, and a token counter on everything.
Target: the human record, 12:29.

## What the first hour found

- The bridge is the Zelda one with the game removed: Python tells it which RAM addresses to report. It started with
  none. Everything below came from dumping all 2 KB every frame and asking which bytes moved when.
- The intro is long. Publisher cards, title, a 30-second attract story, and it loops. Start is **ignored until
  frame ~1519** (byte $12 flips 0→255 there; presses at 1515 do nothing, 1519 works). After an accepted press:
  Gargantua page → LEVEL 1 card → ship flying → the toad drops in. About 1,200 frames with no input.
- Holding a direction right after the press changes memory at frame 1711 — some page is skippable by any input.
  Which pages, and by which button, is the next measurement, because those are free seconds in the record.
- Start pauses during play. Holding Start does nothing; the game wants a press edge.
- The joypad lands in RAM at $29 (Right=1, Left=2 seen so far). $25–$28 churn every frame: the RNG.
- $0200–$02FF is the sprite table (Y, tile, attribute, X per sprite; 248 = off screen). $1C9–$1CE hold the six
  heart tiles of the HUD. $700+ holds the level name as ASCII ("RAGNAROK'S CANYON").
- Scene bytes: $6A steps 5 → 15 → 18 → 0 → 15 through the intro; $0F goes 3 → 255 when the level starts;
  $0D goes 0 → 1 at the level card. Not yet a clean "mode" byte.
- Left alone in Level 1, the toad is beaten up and loses lives. Six lives on the HUD at the start.

## Method notes

Every session is a plan of button holds from power-on (or from a bookmark), video on, RAM dumped every frame.
Parallel emulators are fine (eight at once) as long as each has its own screenshot file — three sessions
sharing one tmp screenshot crashed the bridge on minute five.

Tokens at the end of this entry: see logs/token_marks.jsonl ("first boot recorded": 2.1M total, $6).

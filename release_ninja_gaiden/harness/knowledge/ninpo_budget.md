# Ninpo and ninja-art budget, 2-2 to 6-5 (2026-10-24)

Use this file to check every stage lock: each stage must exit with at least the ninpo shown and with the art shown.
The rule behind it, in the owner's words: never arrive at a boss short of ninpo, or holding the wrong art, when
the right amount would save a lot of time there.

The numbers come from these sources:
* the disassembly (`dl/NinjaGaidenNES/prg/bank07.asm`);
* the TAS RAM log (`work/tasrun/tas4751_ram.csv`);
* the ROM lantern tables (`python -m ng.solve.items <stage>`);
* the record video's HUD, read on 2026-10-24 (crops listed in section 6);
* short NesHawk/Mesen experiments run on 2026-10-24, listed in section 7.

## 0. The short version

1. **Ninpo and the art never carry from one act to the next.** After every boss kill the game turns the
   leftover ninpo into points and then clears the art (`score_leftovers` and `hold_loop` in bank07). So the budget is
   per act. Ninpo picked up in 2-2 can only help 2-3. It can **not** help 3-3. Act III must find its own 30+ ninpo
   in 3-1 and 3-2.
2. **Leftover ninpo at a boss kill costs exactly 3 frames per point**, measured on NesHawk:
   * Setup: the TAS 2-3 kill state, with ninpo poked to 0, 20 and 22.
   * Result: the post-boss hold lasts 451, 511 and 517 frames.
   * Why it can't be avoided: the ninpo tally starts on the kill frame and runs before the timer tally. The total
     tally (about 3 x (ninpo + timer), roughly 450 frames) always outlasts the 255-frame explosion. A J&S spin during
     the explosion does not burn the leftover; the tally takes it first.
   * So: **arrive at each boss with exactly what it will spend.** Every surplus 5 costs 15 frames. A remainder that is
     not a multiple of the art's cost costs 3 frames per point (Throwing Star throws cost 3).
   * Way out: a surplus can still be spent BEFORE the kill at no cost wherever Ryu waits anyway. Examples: spare
     wheels thrown while Basaquer is in the air, or a spin on a jump Ryu makes anyway. Plan the exact amount; treat
     "burn it in the fight" as the fallback.
3. **The record's weapon icons were misread before (fixed here).**
   * The **purple swirl icon is Jump & Slash**, not the Windmill. The orange diagonal icon is the **Windmill**, and the
     orange round flame is the **Fire Wheel**. This was checked against NesHawk screenshots of TAS states with known
     `$C9`.
   * So the record uses **J&S at 1-2, 2-3, 4-4, 5-4 and 6-4a (Masked Devil: one spin)**, the Fire Wheel at 3-3, and
     the Windmill only inside stages (2-1/2-2 start, 5-1/5-2 start, 6-1/6-2 start).
   * The "Masked Devil Windmill strat" in `record_route_a56.md` and `legal_a56_notes.md` is really a **J&S spin**:
     6-3 must keep **J&S**, not the Windmill.
4. **Our current 2-2 line holds the Throwing Star, not J&S.**
   * The TAS's room-6 spin at TAS 6580 breaks the Star lantern (X 256) and catches the Star. Both 2-2 agents copy that
     spin: `$C9` = 129 (Star), ninpo 5 in `states/mesen/l22f_r6w`, `l22f_r7s` and `l22p_s7b`.
   * The agent note in LOCKED_CHAIN ("room 8 change at 7,537, hp 16, np 5, J&S") is wrong about the item.
   * **The J&S lantern in room 8 (X 1312, y 96) is therefore MANDATORY.** Without it 2-3 is a sword fight, about
     270 frames slower.

### Exit requirement per stage (copied to LOCKED_CHAIN.md)

"Exit" = the state on the next stage's control frame (`$C9`, `$64`).

| stage | exit art (`$C9`) | exit ninpo: minimum / target | why |
|---|---|---|---|
| 2-1 (locked) | J&S (133) | 10 / 10 | done (exit J&S/10) |
| **2-2** | **J&S (133)** | **10 / exactly 10** | 2-3 Bomberhead takes 2 spins = 10. Each extra 5 costs 15 f at the 2-3 tally. The room-8 J&S lantern (X 1312) is mandatory, because we hold the Star from room 6 |
| 2-3 | - | 0 | the act ends (tally; the art is cleared) |
| 3-1 | Fire Wheel (128), or none if the 3-2 Fire Wheel (X 1680) is planned | 15 / 20+ | feeds 3-3. Every Star throw is -3 and breaks the multiple of 5 |
| **3-2** | **Fire Wheel (128)** | **25 / 30-35, a multiple of 5** | 3-3 Basaquer: first-pass damage saturates at ~12 HP whatever the ninpo (one wheel at a time). The kill comes on his 2nd sit. Spare wheels thrown during his jump right still hit once each, so 30-35 costs nothing. Section 3 |
| 3-3 | - | 0 | the act ends |
| 4-1 | J&S (133), or none if the 4-2 J&S (X 2624) is planned | 0 / whatever the 4-2 route spends | J&S for 4-4 |
| 4-2 | J&S (133) | 5 / 5-10 (+ 4-3's planned spins) | TAS exits 4-2 with J&S/10, the record J&S/10 |
| **4-3** | **J&S (133)** | **5 / exactly 5** | 4-4 Kelbeross: ONE spin kills both dogs (legal `logs/a34/4-4_p2` = TAS +0, record -14). 4-3 has NO J&S lantern; its Fire Wheel and Windmill lanterns are traps |
| 4-4 | - | 0 | the act ends |
| 5-1 | any art (J&S comes in 5-2) | 30 / 40-45 | 5-3 is the biggest spender of the game (TAS 11 spins, the record ~10) |
| 5-2 | J&S (133) | 40 / 40-55 | J&S at room 23 X 144 is the only J&S of Act V (TAS and record take it) |
| **5-3** | **J&S (133)** | **5 / exactly 5** | 5-4 Bloody Malth: ONE spin (legal `logs/a56_5-4_b13` = TAS +2 = record +0) |
| 5-4 | - | 0 | the act ends |
| 6-1 | J&S, or none if 6-2's J&S (room 36 X 432) is planned | 0 / 10-35 | the record leaves 6-1 with Windmill/35, the TAS with none/5 |
| 6-2 | **J&S (133)** (do NOT take the room-36 Windmill at X 256 the TAS takes) | 5 / 10 | the record leaves 6-2 with J&S/10 |
| **6-3** | **J&S (133)** | **5 / exactly 5** | 6-4a Masked Devil: the record does ONE spin at the orb (record = TAS +10). Ours: Fire Wheel + 10 = TAS +52 (`a56_6-4a_r5f1`), sword only = TAS +164. J&S experiment: section 3 |
| 6-4a | - | 0 | the art and ninpo are cleared after the kill |
| 6-4b, 6-5 | - (sword only) | 0 | no lanterns; the art is always cleared; nothing to plan |

## 1. Mechanics (bank07 unless noted)

| thing | value / behaviour | where |
|---|---|---|
| ninpo `$64` | +5 / +10 per lantern, capped at **99** | `add_ninpo_5/10` $DBE1 |
| Throwing Star `$81` | **3** per throw, up to 3 stars out at once | `throw_star` $EF55 |
| Windmill Star `$82` | **5** per throw, one at a time; it passes through things and comes back (it can break several lanterns) | `throw_windmill` |
| Art of the Fire Wheel `$80` | **5** per throw, three flames. **Only one throw at a time**: while a flame lives, Up+B plays the throw animation (~16 f locked on the ground) and spends nothing | `throw_fire_wheel` $EEF9; legal_a34_notes |
| Jump & Slash `$85` | **5 per spin**. ANY B pressed in the air without Down is a spin while ninpo >= 5. The spin hits every frame (1 HP/frame on bosses) and ends on landing. Down+B in the air = the normal sword (free). With ninpo < 5 a B is a normal slash | $ECB1/$ED55/$EDF9 |
| Invincible Fire Wheel `$84` | no ninpo. Pickup sets `$C9`=$84 for 96 + 7x60 = ~516 f (~8.6 s); **then `$C9` = 0: the old art is GONE** | `invincible_fire_wheel` $DC48, `move_weapon` $D753 |
| Hourglass | freezes enemies ~5 s; picking it up while the Invincible Fire Wheel is on also ends the IFW (`$C9` = 0) | `hourglass` $DC2A |
| art pickup | any art item REPLACES `$C9` (no stacking, no refusal) | $DC66-$DC78 |
| pickup | automatic on touch (\|dx\| < 12, \|dy\| < 17) once the item has dropped. A lantern drops its item only when hit by the sword, a **spin**, a thrown weapon or the IFW flame. Walking past an unbroken lantern is safe; **spins and Windmills break lanterns in passing** | `take_powerup` $DB89, `slash_lantern` $DAA2 |
| health lantern | +6 HP (cap 16). There are no time lanterns | $DC00 |
| sub-weapon throw | Up+B with NO Left/Right on that frame. Legal = 2 frames released, so ~1 frame (1.5 px) lost per throw while running | legal_a34_notes |
| carry-over | ninpo, art and HP carry over between rooms and stages inside an act | TAS log |
| after a boss kill (1-2, 2-3, 3-3, 4-4, 5-4, 6-4a, 6-4b, 6-5) | the ninpo tally (-1 per 3 f), then the timer tally, then `$C9` = 0. Leftover ninpo = **+3 f per point** (measured) | `score_leftovers` $D65A, `hold_loop` $D5B3 |
| death | `$C9` = 0, **ninpo halved**, HP 16, room restart (Act VI: back to 6-1) | `lose_life` $E3xx |
| HP refill | to 16 at every cutscene: act starts, and the 5-4 and 6-4a stage starts (TAS log). Not at 2-3, 3-3 or 4-4 | $D5xx `@call4` |

## 2. What the TAS and the record carry (ninpo / art per stage)

TAS = `work/tasrun/tas4751_ram.csv`. Record = HUD reads from `dl/record_video/v1890225973.mp4`; frames are video
frames. W = Windmill, FW = Fire Wheel, S = Throwing Star, "-" = no art.

| stage | TAS in -> out | TAS pickups (+) / spends (-) | record in -> out |
|---|---|---|---|
| 2-1 | -/0 -> J&S/10 | +5 +10 +5, W (room 2 X 1168), W throw at the room-3 start, +10, J&S (room 3 X 592), 4 spins, +5 | -/0 -> **W/15** |
| 2-2 | J&S/10 -> J&S/10 | room 6: spin, spin(+5 lantern X 672), +10 (X 608), spin, **spin that breaks the Star lantern -> Star (X 256)**; room 7: +5 (X 432), +10 (X 272) = S/20; room 8 (leftward): +5 (1616), +5 (1552), **J&S (1312)**, 2 spins, +10 (1088), spin, spin(+5 X 800), 3 spins -> J&S/10. FW (944) left hanging | W/15 -> J&S/10 (room 8 entry with **50**, J&S taken ~video 9740, then ~8 spins in room 8) |
| 2-3 | J&S/10 -> 0 | 2 spins, kill at control+81 | J&S/10 -> 0 (2 spins, TAS +3) |
| 3-1 | -/0 -> FW/10 | +5 (432), +10 (576), S (768), **5 Star throws** (break +10 1152 and FW 1184 from range; ninpo/timer phase), +10, FW | -/0 -> FW/17 (00 -> 10 -> S -> 1 throw -> 07 -> +10 -> FW) |
| 3-2 | FW/10 -> FW/20 | +10 (448), FW throw at the pillar (TAS 12646), +5 (2192) | FW/17 -> FW/27 |
| 3-3 | FW/20 -> 0 | 4 wheels + 4 air slashes, kill control+84 (uses U+D) | FW/27 -> 2 left (5 wheels, kill ~control+166, TAS +83) |
| 4-1 | -/0 -> J&S/0 | +10, +5, J&S (896), spin(+10 1168), 3 spins, spin in room 15 | -/0 -> J&S/0 |
| 4-2 | J&S/0 -> J&S/10 | +5 (704), spin, +10 (2784) | J&S/0 -> J&S/10 |
| 4-3 | J&S/10 -> J&S/5 | spin(+5 272), spin(+10 592), 3 spins (room 19), +10 (room 20 464), 2 spins, +5 (656) | J&S/10 -> J&S/5 |
| 4-4 | J&S/5 -> 0 | ONE spin, both dogs dead in 16 f | J&S/5 -> 0 (one spin; TAS +14) |
| 5-1 | -/0 -> W/40 | all 7 ninpo lanterns (+50), W (736), health (2576), 2 W throws at the end (X ~2440-2490, top) | -/0 -> W/45 |
| 5-2 | W/40 -> J&S/40 | +5 (480), **J&S (room 23 X 144)**, spin(+5 r24 320), 2 spins (r25), +5 (r25 480), spin, spin(+10 r26 560) | W/45 -> J&S/55 |
| 5-3 | J&S/40 -> J&S/5 | **11 spins (55)**, +5, +10, +5; two room-f enemies left alive to save 5 | J&S/55 -> J&S/5 |
| 5-4 | J&S/5 -> 0 | ONE spin | J&S/5 -> 0 (TAS +2) |
| 6-1 | -/0 -> -/5 | +5 (1216) only | -/0 -> W/35 (all five ninpo lanterns + W 800) |
| 6-2 | -/5 -> W/15 | +5, +5, J&S (r36 432), 2 spins, **W (r36 256)**, W throw (r37), +10 (r37 720), W throw (r39), +10 (r39 544) | W/35 -> **J&S/10** |
| 6-3 | W/15 -> FW/5 | 3 W throws (r43), +10 (r44 528), FW (r44 944), FW thrown at the exit (2 free hits on the orb) | **J&S/10 -> J&S/5** |
| 6-4a | FW/5 -> 0 | 1 wheel + sword, kill control+62 | **J&S/5 -> 0: one spin at the orb** (TAS +10) |
| 6-4b, 6-5 | -/0 | sword | sword |

## 3. Demand: what each boss needs and what ninpo is worth there

| boss | best known art / ninpo | legal result | without it | worth of the ninpo |
|---|---|---|---|---|
| 1-2 Barbarian | J&S 10 (2 spins) | locked (834 f = TAS) | - | done |
| 2-3 Bomberhead | **J&S 10** (2 spins) | TAS pace: boss 0 at control+81 (`states/tmp/a56r2_tk_2-3_tasprobe.inputs.txt`, RNG-independent; NesHawk: kill row 80) | sword only `logs/tk_2-3_bh2`: 1,105 f = TAS +275 | 0 -> 10: **~270 f**. 5 -> 10: **~96 f**. Measured 2026-10-24: with 5 the first spin gives 12 hits (16 -> 4 by row 74), and a crude sword grid (jump + `Down,Down+B,B,-,-`) kills at row 176 vs 80. > 10: -3 f/pt |
| 3-3 Basaquer | **Fire Wheel 30-35** | see below | 20 from the TAS state: `logs/a34/3-3_p2` = TAS +150 (record +67). 23 on the old chain: no kill in 230 rows (5 HP left after the first pass) | 20 -> 30: the difference between a 2nd-pass kill and a possible 1st-pass kill (see below). Remainder (not a multiple of 5): -3 f/pt |
| 4-4 Kelbeross | **J&S 5** (1 spin) | `logs/a34/4-4_p2` = TAS +0 = record -14 | sword-only not measured (16 HP at 1 hit / 5 f is >= 75 f of contact vs 16 f) | 0 -> 5: est. 50-100 f. > 5: -3 f/pt |
| 5-4 Bloody Malth | **J&S 5** (1 spin) | `logs/a56_5-4_b13` = TAS +2 = record +0 | sword-only not measured | 0 -> 5: est. 50-100 f. > 5: -3 f/pt |
| 6-4a Masked Devil | **J&S 5** (record: one spin at the orb, TAS +10). TAS: Fire Wheel 10 (one wheel thrown at the end of 6-3 hits the orb twice) | FW: `logs/a56_6-4a_r5f1` = TAS +52. J&S: see the experiment below | sword only `a56_6-4a_b11` = TAS +164 (old planner) | J&S 5 vs FW 10: ~40 f (record). FW 10 vs sword: ~110 f |
| 6-4b Jaquio | sword (the art is cleared after 6-4a; no lanterns) | `r4` kill = TAS +145, about 7 f ahead of the record; it assumes no art and no ninpo, which is always the case | - | - |
| 6-5 Demon | sword | `a56_6-5_r2d4` = TAS +228 (record +162) | - | - |

### 3-3 Basaquer: how many wheels (experiment, 2026-10-24)

The boss path is fixed and independent of `$BF`. Wheels fly level from Ryu, at most 3 hits each, one throw at a time.
* On the old chain's 3-3 state (`states/mesen/c5_33m1`, poked to 30 ninpo; GA `work/c5/b33ga.py`, 22 min,
  `logs/nb/b33_np30.out`, best rows `states/tmp/nb_b33_np30.inputs.txt`): 5 wheels take him 16 -> 4 by row 82
  (the same first-pass damage as with 23). The 6th wheel thrown at row ~121 lands at row ~161: 1 HP left, no kill
  inside 170 rows.
* Why the GA stalls (Mesen trace of its best rows):
  * Ryu is hit at row 82 by the boss jumping right over him (x ~80) and is knocked back until ~row 122. No throw is
    possible in that time.
  * Its later wheels are thrown facing LEFT, away from the boss on the right.
* Structured probe from row 70 (boss 8 HP; `logs/nb/b33probe2_np35.out`, `_np40.out`; 945 candidates each):
  * Setup: Left/Right/stay for 0-20 rows, then up to 3 wheels (turn right, 2 blank rows, Up+B) at rows 74-152,
    18-30 apart.
  * Result: wheels thrown while he jumps right (rows ~94-121) land **1 hit each** (8 -> 5, the record does the
    same: bar 8 -> 5 by video 15732). One more lands at the 2nd sit (row ~160). Best: **4 HP left at row 175, no
    kill**, identical with 35 and 40 ninpo.
* **Conclusion:**
  * First-pass damage saturates at ~12 HP: the one-wheel-at-a-time rule allows ~4-5 wheels by row ~120, so 20-25
    ninpo already buys all of it.
  * The kill is on his 2nd sit on the right (rows ~132-170): air slashes like the record (kill ~row 166), or more
    wheels there.
  * So ninpo beyond 25 is worth at most a faster 2nd-sit finish (unproven). It is cheap to collect in 3-2 and can be
    thrown during his jump at no cost (1 hit each), so carrying 30-35 is safe.
  * **Requirement: min 25 (5 wheels = the record's count), target 30-35**, a multiple of 5.
  * The real answer needs a search on the chained 3-3 state that avoids the row-82 hit: kill row with 25 vs 30 vs
    35.

### 6-4a Masked Devil with J&S (experiment, 2026-10-24)

* Setup: NesHawk, `ref4751/19_6-4a_control`, `$C9` poked to $85, ninpo 5, `$C8` = 0 (the TAS's flying wheel
  removed).
* Route: floor jump onto the left pedestal (`A`, `Right+A`, Right), jump right from it at row 24 (`Right+A` x2),
  then ONE spin (`B+Right` x2) at rows 26-37.
* Result: the spin alone takes the orb **16 -> 3** (13 hits), but Ryu is hit (hp 16 -> 10). So the record's line is
  one spin + ~3 sword hits (the record's bar drains in ~30 f).
* Not done: the J&S + 5 kill on a chained state. Grafting r5f1's later slash rows onto the spin start gave no kill:
  r5f1's trajectory is a different one. Finish it with the a56 jump planner (`work/r4/jqplan2.py`, `BOSS=mdevil`)
  from a state that holds J&S/5.
* Also untested: a second spin (J&S + 10) instead of the 3 sword hits. That could be a few frames faster, so the 6-3
  target might become 10.

## 4. Supply: every lantern per stage (ROM), and who takes it

Notation:
* "TAS@f" = the TAS catches it on frame f.
* "cost" = `ng.solve.items.lantern_cost` against the TAS line: 1 = the line passes within sword reach; otherwise
  a rough detour estimate in frames.
* Our legal lines differ from the TAS in 2-2 room 7, 3-2, 4-1c, 4-3, 5-x and 6-2/6-3, so re-cost on our own line
  (`items.plan(..., route=...)`).
* **TRAP** = an art lantern on or next to the line that would replace the art the boss needs.

### Act II (boss 2-3: J&S + 10)

**2-2 room 6 (leftward):**

| lantern | cost | taken by |
|---|---|---|
| +10 X 96 | 8 | - |
| Star X 256 | 1 | TAS@6581 (**TRAP**: replaces J&S) |
| +10 X 608 | 1 | TAS@6353 |
| +5 X 672 | 1 | TAS@6314 |

**2-2 room 7:**

| lantern | cost | taken by |
|---|---|---|
| +10 X 272 | 1 | TAS@7216 |
| +5 X 432 | 1 | TAS@7109 |
| InvFW X 592 y 96 | 1 | - (**TRAP**, but harmless here: J&S comes later in room 8) |
| health X 656 | - | - |

Our room 7 is the record's route (right, under the pillar, between the pillars); its lanterns have not been taken so
far (np 5 at room 8).

**2-2 room 8 (leftward):**

| lantern | cost | taken by |
|---|---|---|
| +5 X 1616 y 128 | 1 | TAS@7660 |
| +5 X 1552 y 128 | 1 | TAS@7704 |
| **J&S X 1312 y 96** | 1 | TAS@7877 (catches it at y 128) — **MUST TAKE** |
| +10 X 1088 y 160 | 1 | TAS@8012 |
| **FW X 944 y 128** | 1 | **TRAP** (after the J&S!). The TAS spins at X 924 y 144 (TAS 8127) close to it and leaves it. Never catch it |
| +5 X 800 y 112 | 1 | TAS@8219 (spin-break) |

2-3 has no lanterns.

### Act III (boss 3-3: Fire Wheel + 25 min, 30-35 target)

**3-1 (rightward).** Cheap on the TAS line, at ~1 f each: +5 X 336, +5 X 432 (TAS), +10 X 576 (TAS),
+10 X 1152 y 160 (TAS) = **30**. Also +10 X 1328 y 96 (~15 f).

| art lantern | cost | note |
|---|---|---|
| Star X 768 | 1 | TAS; take it BEFORE the FW or skip it |
| **FW X 1184 y 96** | ~15 by sword | the TAS breaks it with stars |

Hourglass at X 640 (harmless). Health at X 1664.

**3-2 (rightward).** Cheap: +5 X 352, +10 X 448 (TAS), +5 X 1504, +5 X 2192 (TAS), +10 X 2368 = **35**.
Detours: +10 X 2832 (~8 f), +10 X 1152 (~18 f).

| art lantern | cost | note |
|---|---|---|
| Windmill X 1008 y 96 | 8.6 | **TRAP** |
| FW X 1680 y 144 | ~15 | backup FW source, if 3-1's is skipped |
| **Windmill X 2624 y 112** | 1 (on the TAS line) | **TRAP**: the last art lantern before 3-3. Never break/catch it |

### Act IV (boss 4-4: J&S + 5)

**4-1 (rightward).**

| lantern | cost | note |
|---|---|---|
| +10 X 272 | 1 | TAS |
| +5 X 464 | 1 | TAS |
| **J&S X 896 y 80** | 1 | TAS@15137; the record takes it too |
| Windmill X 944 y 128 | 10 | **TRAP** |
| 1-UP X 1008 | - | |
| +10 X 1168 | 1 | TAS spin-break |
| **InvFW X 1360 y 80** | 19 | **TRAP**: it erases J&S after 8.6 s |
| +5 X 1680 | 42 | |

**4-2.** Ninpo: +5 X 704 (TAS), +5 X 784, +5 X 1152, +10 X 2784 (TAS), all ~1 f. Detours: +5 X 304 (8 f),
+10 X 432 (8 f), +10 X 768 (35 f), +10 X 1248 (35 f).

| art lantern | cost | note |
|---|---|---|
| Windmill X 688 | - | **TRAP** |
| FW X 944 y 160 | 10 | **TRAP** |
| Star X 1248 y 160 | 8 | **TRAP** |
| **Windmill X 2224 y 96** | 1 (on line) | **TRAP** |
| J&S X 2624 y 128 | 1 | backup J&S |
| **Windmill X 2976 y 128** | 1 (on line) | **TRAP**: the last lantern before 4-3 |

**4-3.** There is **NO J&S lantern in 4-3.**

| room | lantern | cost | note |
|---|---|---|---|
| 18 | **FW X 272 y 112** | - | **TRAP**: directly above the +5 at X 272 y 176, which the TAS spin-breaks at TAS 19237 (X 265 y 160). Check `$C9` right after |
| 18 | +5 X 272 y 176 | 1 | TAS spin-break |
| 18 | +10 X 592 | 1 | TAS spin-break |
| 18 | +5 X 688 | 8 | |
| 18 | Windmill X 752 | 10 | **TRAP** |
| 19 | **Windmill X 304 y 144** | 1 (on line) | **TRAP** |
| 19 | +5 X 480 | 16 | |
| 19 | **FW X 816 y 96** | 1 (on line) | **TRAP** |
| 20 | Windmill X 304 y 96 | 21 | **TRAP** |
| 20 | +10 X 464 | 1 | TAS |
| 20 | +5 X 656 | 1 | TAS |

### Act V (boss 5-4: J&S + 5; 5-3 is the big spender)

**5-1 (rightward).** All 7 ninpo lanterns are on the TAS line (+50): X 304, 368 (y 160), 592, 864, 944, 1648, 2976.

| lantern | cost | note |
|---|---|---|
| Star X 368 y 96 | - | above the +5 at X 368 |
| Windmill X 736 | 1 | TAS; fine, J&S comes in 5-2 |
| FW X 1376 | - | |
| Windmill X 2176 | - | |
| health X 2576 | - | TAS takes it |

**5-2.**

| room | lantern | cost | note |
|---|---|---|---|
| 23 (leftward) | +5 X 480 | 1 | TAS |
| 23 | +10 X 352 | 1 | |
| 23 | **J&S X 144 y 112** | 1 | TAS@24820 — **MUST TAKE** (the only J&S of Act V) |
| 24 | +5 X 320 y 96 | 1 | TAS spin-break at X 329 y 112 |
| 24 | **FW X 320 y 160** | - | **TRAP**: directly below that +5 |
| 24 | **Star X 512 y 128** | 1 (on line) | **TRAP** |
| 25 | +5 X 96 | 1 | |
| 25 | Windmill X 224 | 10 | **TRAP** |
| 25 | InvFW X 448 | 31 | **TRAP** |
| 25 | +5 X 480 | 1 | TAS |
| 26 | +10 X 560 | 1 | TAS spin-break |

**5-3.** Ninpo here is small and mostly off the line (the TAS takes only +5, +10, +5), so carry 5-3's spending in.

| room | lantern | cost | note |
|---|---|---|---|
| 27 | **FW X 192 y 112** | 1 | **TRAP** |
| 29 | **InvFW X 144 y 80** | 1 (on the TAS line) | **TRAP**: it erases J&S, so 5-4 would have no art |
| 29 | Star X 496 | 15 | **TRAP** |
| 30 | **Windmill X 464** | 1 | **TRAP** |
| 30 | **Star X 624** | 1 | **TRAP** |
| 31 | FW X 240 | 22 | **TRAP** |
| 32 | FW X 256 | 15 | **TRAP** |
| 32 | Windmill X 368 | 25 | **TRAP** |

### Act VI (boss 6-4a: J&S + 5; Jaquio and the Demon are sword only)

**6-1 (rightward).**

| lantern | cost | note |
|---|---|---|
| +10 X 112 | 15 | |
| +5 X 240 | 1 | |
| J&S X 528 y 128 | 1 | |
| +5 X 656 | 15 | |
| Windmill X 800 | 1 | **TRAP** if J&S is held (the record took the Windmill here) |
| +10 X 1024 | 1 | |
| +5 X 1216 | 1 | TAS |
| **Star X 1456** | 1 | **TRAP** |

**6-2.**

| room | lantern | cost | note |
|---|---|---|---|
| 36 (leftward) | +5 X 1232 | 1 | |
| 36 | Windmill X 1072 | 15 | **TRAP** |
| 36 | +5 X 1056 | 1 | TAS |
| 36 | +10 X 800 y 176 | 15 | |
| 36 | +5 X 544 | 1 | TAS |
| 36 | **J&S X 432 y 80** | 1 | TAS@32353 — **TAKE** |
| 36 | **Windmill X 256 y 128** | 1 | **TRAP**: TAS@32484. The TAS's spin at TAS 32483 (X 244 y 118) breaks it and Ryu catches it. Our legalized TAS rows for room 36 (`work/r4/tasleg.py`) copy that spin; change them |
| 37 | Star X 176 | 1 | **TRAP** |
| 37 | +5 X 320 | 8 | |
| 37 | Windmill X 432 | 22 | **TRAP** |
| 37 | FW X 544 | 8 | **TRAP** |
| 37 | +10 X 720 | 1 | TAS |
| 38 | Windmill X 48 | - | never hangs (the room does not scroll) |
| 39 | +5 X 272, +5 X 320, +10 X 544 | 1 each | +10 X 544 = TAS |
| 40 | +5 X 304 | 22 | |
| 40 | health X 384 | - | |
| 40 | +10 X 512 | 1 | |
| 40 | **InvFW X 560 y 160** | 1 (on line) | **TRAP** |

**6-3.**

| room | lantern | cost | note |
|---|---|---|---|
| 41 | **FW X 320 y 96** | - | **TRAP**: directly above +5 X 320 y 144 |
| 41 | +10 X 544 | 25 | |
| 41 | J&S X 688 y 160 | 22 | backup J&S |
| 43 | +5 X 64 / +5 X 208 / +10 X 256 | 31 / 1 / 47 | |
| 43 | **FW X 512 y 80** | 1 (on line) | **TRAP** |
| 43 | +5 X 704 | 15 | |
| 43 | hourglass X 832 | - | |
| 43 | Windmill X 1104 | 46 | **TRAP** |
| 43 | +10 X 1312, +5 X 1392 | 1 each | |
| 43 | +5 X 1424 | 8 | |
| 43 | **FW X 1536 y 144** | 1 | **TRAP** |
| 43 | **Star X 1760** | 1 | **TRAP** |
| 44 | +10 X 528 | 1 | TAS |
| 44 | +5 X 576, +5 X 624 | 1 each | |
| 44 | **FW X 704** | 1 | **TRAP** |
| 44 | Star X 816 | 15 | **TRAP** |
| 44 | Windmill X 880 | 15 | **TRAP** |
| 44 | **FW X 944** | 1 | **TRAP** (TAS@37085) |

## 5. The plan per stage

The general rule:
* While ninpo is **above** the next boss's need, any spin or throw that saves >= 1 f is free. Unspent surplus costs
  3 f per point at the tally.
* While ninpo is **at or below** the need, spend only if the stage gain beats the boss loss:
  * 2-3: never;
  * 3-3: ~10+ f per 5 (to be measured);
  * 4-4, 5-4 and 6-4a: never below 5.
* Prefer Down+B for air slashes once J&S is held. B+direction in the air is a spin and spends 5; the fbeam climb
  cycle `A+L, L, -, B+R, A+B+R` (2-1) spins with J&S.
* Never press Up+B while holding the Throwing Star unless it is planned: each throw costs 3 and leaves a remainder.

### 2-2 (now: lock round)

* **Entry:** J&S/10 (locked).
* **Our line so far:** TAS room 6 (zero loss) gives room 7 with **Star/5** (the TAS's spin at TAS 6580 catches the
  Star). Room 7 is the record route, with no lanterns so far, so room 8 starts with Star/5.

**Room 8, in route order (leftward):**

| step | lantern | what to do |
|---|---|---|
| 1 | +5 X 1616 and +5 X 1552 (y 128) | both on the TAS line. With the Star held, air B is a free normal slash (Up+B would throw: don't) |
| 2 | **J&S X 1312 (y 96)** | the TAS breaks it at about y 128 and catches it. **Mandatory.** If it is not caught, 2-3 is about +270 f |
| 3 | +10 X 1088 (y 160) | on the line |
| 4 | **FW X 944** | never catch it. Check `$C9` == 133 at the room exit |
| 5 | +5 X 800 (y 112) | |

**Arithmetic:**
* 5 + 5 + 5 + 10 + 5 = **30 possible**, against an exit need of 10.
* So up to **4 spins** in room 8 are "free" (the TAS uses 7 spins after the J&S, the record ~8).
* Each lantern skipped removes one spin. Each 5 left above 10 at the exit costs 15 f at 2-3.

**Lock check:** `$C9 == 133`, `$64 == 10` (>= 10 required; 15 = -15 f unless a 3rd spin fits the 2-3 fight for
free).

**Downstream:** 2-3 uses the TAS graft (2 spins). Nothing carries into Act III.

### 2-3

* Entry: J&S/10.
* Spend: 2 spins (the TAS graft).
* Exit: nothing; the act ends.

### 3-1

* **Entry:** -/0.
* **Need at the 3-2 exit:** FW + 25 (min), 30-35 (target).

**Two ways:**
* (a) TAS-like: Star X 768, then thrown stars break the +10 X 1152 and the FW X 1184 from range.
  * **Use 0 or 5 Star throws**, never 1-4. Each throw is -3: 1 throw leaves a remainder of 2 (6 f at the 3-3
    tally), 2 throws leave 4 (12 f).
  * The TAS's 5 throws (-15) also set its timer phase.
* (b) The record: 1 throw. That costs the remainder unless a later Star throw evens it out.

**Lanterns:** take the four cheap ones (+5 X 336, +5 X 432, +10 X 576, +10 X 1152) = 30 before throws.

**Exit:** FW + >= 15 (with 5 throws) or >= 25 (with no throws).

### 3-2

* **Entry:** FW + 15-30.
* **Lanterns:** cheap +5 X 352, +10 X 448, +5 X 1504, +5 X 2192, +10 X 2368 (35 at ~1 f each); +10 X 2832 for ~8 f.
* **Spends:** the TAS throws one wheel at the pillar section (12646). Budget it only if the legal pillar route needs it.
* **TRAPS:** Windmill X 1008 and **Windmill X 2624 (on the line, the last art lantern)**.
* **Exit:** **FW + 25 (minimum) / 30-35 target**, a multiple of 5. Unthrown spares cost 15 f each, but they can be
  thrown during his jump right (1 hit each), so 30-35 is safe.

### 3-3

* Entry: FW + 25-35.
* Plan, as the record:
  * wheels as fast as the one-at-a-time rule allows from control to his first sit (rows ~20-76): ~12 HP;
  * stay clear of his jump right over Ryu at x ~80 (row ~82: the GA line is hit there and loses ~40 rows of
    knockback), throwing wheels at him in the air (1 hit each);
  * air slashes (or wheels) on his 2nd sit on the right (rows ~132-170).
* Exit: nothing.

### 4-1 to 4-4

* **4-1:** take the J&S X 896 (on the line, ~1 f). Avoid the Windmill X 944 and the **InvFW X 1360**. The ninpo is
  free for spins until the 4-3 exit need.
* **4-2:** avoid the Windmills at X 2224 and **X 2976 (the last lantern, on the line)**; the J&S at X 2624 is a backup.
  Exit J&S + 5-10 plus whatever 4-3's legal line spends.
  * The record route's 4-3c uses two kills that `record_route_a34.md` calls "Windmill throws at the ninja/gunner".
    The record held J&S in 4-3 (corrected icon), so those were **spins** (2 x 5). Budget 10 for them.
* **4-3:** the exit must be **J&S + exactly 5**.
  * TRAPS: the FW X 272 above the +5 X 272 (room 18), the Windmill and FW on the room-19 line.
  * No J&S lantern: a lost J&S in 4-3 cannot be repaired.
* **4-4:** one spin (`4-4_p2`).

### 5-1 to 5-4

* **5-1:** take the cheap ninpo (~50 on the TAS line).
  * The Windmill (X 736) is fine here and useful if the legal 5-1 needs throws (the TAS throws 2 at the top end).
  * Exit any art + 40-45.
* **5-2:** **take the J&S at room 23 X 144** (the only one in Act V).
  * TRAPS: FW X 320 under the room-24 +5 that the TAS spin-breaks; Star X 512 (on the line); the room-25
    Windmill/InvFW.
  * Exit J&S + 40-55. The TAS has 40, the record 55; it depends on how many spins our 5-3 needs.
* **5-3:** spins as needed. TRAPS: **InvFW room 29 X 144 (on the TAS line)**, FW room 27 X 192, room-30 Windmill
  and Star (on the line).
  * **Exit J&S + exactly 5.** If J&S is lost here, the 5-4 fallback is the Windmill (room 30 X 464; untested at
    5-4) or the sword (untested).
* **5-4:** one spin (`5-4_b13`).

### 6-1 to 6-4a

* **6-1:** either take the J&S X 528 (on the line) and avoid the Windmill X 800 and the Star X 1456, or take
  nothing (TAS) and get J&S in 6-2. Ninpo here only feeds 6-2/6-3 spins.
* **6-2:** take the **J&S at room 36 X 432**. **Do NOT copy the TAS's room-36 spin at TAS 32483 that catches the
  Windmill X 256.**
  * Our "room 36 at TAS pace" rows copy it: re-check `$C9` at the room-37 entry.
  * The TAS's two Windmill throws (rooms 37 and 39) become spins or sword.
  * TRAP: InvFW room 40 X 560 (on the line).
  * Exit J&S + 10 (as the record).
* **6-3:** TRAPS everywhere on the TAS line: FW r41 X 320, FW r43 X 512 and X 1536, Star r43 X 1760, FW r44 X 704 and
  X 944. The J&S r41 X 688 (~22 f) is the only backup.
  * Exit **J&S + exactly 5**.
  * The TAS-style alternative is to keep the Fire Wheel and exit FW + 10, throwing one wheel at the 6-3 exit for
    free orb hits (our r5f1 = TAS +52, ~40 f worse than the record's J&S).
* **6-4a:** one J&S spin at the orb (record). Then the sword for Jaquio and the Demon.

## 6. Record HUD reads (2026-10-24)

* Tool: `ffmpeg` crops `crop=560:110:600:250` of `dl/record_video/v1890225973.mp4`, made with a scratch script.
* Icons calibrated on NesHawk screenshots `shots/nb_icon_*.png`:
  * J&S = purple swirl;
  * Fire Wheel = orange round flame;
  * Windmill = orange diagonal blades.

Reads by video frame:

| what | video frame(s) | art / ninpo |
|---|---|---|
| 1-2 | 4030 / 4060 / 4110 | J&S/10, 05, 00 |
| 2-1 in | 4870 | -/00 |
| 2-1 out | 7525 | W/15 |
| 2-2 room 8 entry | 9560-9680 | W/50 |
| 2-2 room 8 | 9740 | J&S/50 |
| 2-2 room 8 | 9800-10340 | J&S, 45 -> 40 -> 45 -> 40 -> 35 -> 30 -> 25 |
| 2-2 out | 10640 | J&S/10 |
| 2-3 | 10870 / 10900 / 10930 | J&S/10, 05, 00 |
| 3-1 out | 13080 | FW/17 |
| 3-2 out | 15410 | FW/27 |
| 3-3 kill | 15775 | FW/00, already tallied |
| 4-1 out | 18530 | J&S/00 |
| 4-2 out | 20760 | J&S/10 |
| 4-3 out | 23330 | J&S/05 |
| 4-4 | 23575 | J&S/00 |
| 5-1 out | 26590 | W/45 |
| 5-2 out | 29050 | J&S/55 |
| 5-3 out | 32070 | J&S/05 |
| 5-4 | 32250 | J&S/00 |
| 6-1 out | 34390 | W/35 |
| 6-2 out | 37530 | J&S/10 |
| 6-3 out | 40505 | J&S/05 |
| 6-4a | 40700 / 40750 | J&S/05, 00 |

## 7. Experiments run for this file (2026-10-24)

* **Tally cost**, NesHawk, `ref4751/04_2-3_boss0`, ninpo poked 0/20/22, idle or jump+B every 48 f:
  * the post-kill hold (`$4B8` != 0) lasts 451 / 511 / 517 f, so +3 f per leftover point;
  * jump-spins during the explosion change nothing.
* **Weapon icons:** NesHawk screenshots of `ref4751/03_2-2_control` (J&S), `07_3-3_control` (FW),
  `18_6-3_control` (Windmill) -> `shots/nb_icon_*.png`.
* **Our 2-2 item:** Mesen reads of `states/mesen/l22f_r6w`, `l22f_r7s`, `l22p_s7b` -> `$C9` 129 (Star), ninpo 5.
* **3-3 with 30/35/40 ninpo** (Mesen, `states/mesen/nb_33m1_np{30,35,40}.mst` = `c5_33m1` poked):
  * GA `logs/nb/b33_np30.out`;
  * probes `logs/nb/b33probe_np*.out` (from row 84; invalid because of the knockback) and
    `logs/nb/b33probe2_np*.out` (from row 70);
  * results in section 3.
* **2-3 with J&S + 5** (NesHawk, `ref4751/04_2-3_control` poked to 5, tasprobe rows + a sword grid): kill row 176
  vs 80.
* **6-4a with J&S** (NesHawk, `ref4751/19_6-4a_control` poked): one spin = 13 hits, no kill composed. Section 3.
* Scratch scripts are in the session scratchpad and are not needed to reuse the results.

## 8. Open questions (experiments for later)

* 2-3 with J&S + 5 only (one spin + sword): how much slower than 10? This decides whether a 5-short 2-2 exit is a
  disaster or a small loss.
* 3-3: the kill row with 25, 30 and 35 ninpo on a chained start, avoiding the row-82 hit (GA/sweeps from the real
  3-3 control state once 3-2 is locked). If 25 kills as fast as 35, lower the 3-2 target to 25.
* 4-4 and 5-4 sword-only kill times (the worth of the 5 ninpo there; only J&S has been tried).
* 5-3 and 6-2/6-3 legal spin counts (sets the 5-2 / 6-1 exit targets); not solved yet.
* 6-4a: J&S spin + sword on a chained start; and whether a pre-thrown spin is possible (it is not: J&S is not
  thrown).

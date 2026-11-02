### Agent notes (5-3)
* **l53a (room 27, pit) PAUSED 2026-10-27 by the owner: resume note.** No rows built yet. Tools in `work/l53a/`: `tr.py`
  (trace a row spec from a TAS state or .mst: X y xsub vy `$8C` `$84` anim hp np room, `--en` enemy slots, `--poke`), `gate.py`
  (waits for free RAM >= 3 GB before running a command).
  * **The record's pit crossing is the X-672 column's ladder + the y-112 platform, and it costs ~+40, not ~+17.** From
    `work/a56r2/rec/r53.json` (record camera vs the TAS camera, RAM x = video x + cam - 2, y = video y + 9): the record's camera
    starts scrolling at t 75 (TAS t 31): **lag 44 from the first move**; then the camera moves at exactly 1.5 px/f without a stop
    (lag 44 -> 42 -> 40 through the pit). Ryu is at y 86 over X 549 at t 135 (hidden above y ~81 for t 115-133 = a jump from
    the platform), runs on the y-112 platform X 535 -> 445 (t 143-203), drops to the floor at X ~399 (t 239). So he climbed the
    ladder face before t ~58 and jumped off left at 1.5 px/f; the pit itself costs ~0 once on the platform. Later lags: 45-46
    (X 400-260), 51 around the X-240 lantern / '84' pillar, 36 at X ~180 (the record walks under the '84' pillar; the TAS climbs it).
  * **The ladder grab works (prep's `pitgrid.py` never walked far enough left: k <= 15 leaves Ryu under the column, where
    rising into the '9' tile sets the let-go bit `$80`).** Grab rule (`touch_walls` $E677): `$8F` = kind at (x+5, y-1) must be the
    '9' (X 672-687, rows y 80-191) in the same frame `$8E` (x+5, y-5) is; i.e. come in from the LEFT (x <= 666 first) with feet
    y 85-192. Verified trace (TAS state 26,607, hp 3): `Left*30, Right*2, A+Right*2, Right*...` -> walks to X 643, jumps at
    26,640, **grabs at X 667 y 165 on 26,654** (`$8C` = $20, action 10); Up climbs exactly 1 px/f (action 12). On steps only
    A+Left ($82) jumps off (vy -2, facing flips to LEFT, run speed 1.5 px/f); Down climbs down; anything else holds.
  * Arithmetic for the line: Ryu at pure 1.5 px/f leftward would be at X 444 on t 163; the TAS is on the floor at X 401 on t 194
    (~2 f behind pure running), so **cost of a platform line = frames lost vs pure leftward running**. A jump-off from the face
    at X 667 reaches the platform's edge (x <= 646) ~14 f later at y0 - 7, so it needs y0 <= ~118 at the jump-off. Grab at
    y 165 + Up 1 px/f = ~47 f of climbing -> ~+79 total (worse than the record). Faster: grab higher (a jump from further left
    peaks at y 160) and climb with jump-off/regrab cycles (`[A+Left x2, Right x6]`-type, 5-2's `cyc.py` grammar) - untested.
* **Next steps (l53a on resume):**
  1. Beam (`b53.py`-style, goal X <= 446 and y <= 112, or floor X <= 400) from TAS 26,607 with the alphabet incl. Up/Down and
     the grab prefix above; also a cycle grammar from the grab (walk-left distance k x jump frame x cycle pattern x jump-off y).
     Target: beat the record's ~+40 (record lag 40 at X 445).
  2. Try the other routes still untested: knockback from the hovering t0s (X 500-540, y 104-112, t 42-172) while above the
     pillar; a ground jump that crosses the X-528 pillar at y <= 160 (passes over it; y-1 must be < 160) then a cling on the
     '21' block's '1' face (X 511); J&S spin / slash effects on air physics (check `drift_speed`/`run_speed` $E??? at
     bank07 lines 6746-6760, `move_ryu` line 5805).
  3. Then the exit (`work/l53p/b_ex27b_h3n35i133.txt`, +46), the +5 lanterns X 400 / X 240 (y 160; on the platform line Ryu
     falls past X ~400 from y 112, so the X-400 lantern may be free), room 28 phase (bf53.py).
  4. Re-check on the real 5-2 exit state (NesHawk) once a 5-2 candidate exists; report hp 9 and hp 12.

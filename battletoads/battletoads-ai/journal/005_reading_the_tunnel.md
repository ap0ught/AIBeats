# 005 — Reading the tunnel (2026-09-27)

With the bike on the left edge of the screen the Turbo Tunnel stopped being a memory test and became a reading
test. Everything that matters shows up in the object table 200+ px early, and each object type has one rule:

- **Walls (0x23)** sit in two lanes, depth 200 (top) and 224 (bottom). One kills you within 14 px of its depth and
  lets you pass at 19. So: if the other lane is clear for the next 420 px, slide over (Up/Down, ~1 px/frame); if
  not, jump when the wall is 150–283 px out. A jump in my lane always beats a slide in progress, and a slide is
  abandoned the moment a wall appears in the lane I was heading for.
- **Holes (0x25)** are objects, not missing road. You cross one airborne — the arc covers press+40 to press+430 —
  so press *late* (hole 60–160 px out) and a second hole 170 px behind the first fits under the same arc.
- **Trampolines (0x24)** come in two kinds. On the road (h 64) they bounce you over a short gap by themselves.
  Floating (h 92) ones are the long-gap answer: line up at depth 212, jump anywhere in the 350 px before it, and
  the bounce is enormous (h 165, ~1,300 px). That is the 32k gap that looked impossible from the right edge.
- **Ramps** are just road: `h` is the height of the road under the bike and climbs to 154 on the big ones; A is
  ignored while gliding back down, so "grounded" means z ≤ 13 *and* road ≤ 66.
- **Drops (0x29)** fall out of the sky and then sit on the road like a wall.
- **Parked objects**: everything waits at the right screen edge (dx constant) until its trigger x, then closes at
  8 px/frame. A rule that fires on a parked wall jumps for a ghost.
- **The portal (0x22)** — same object ID as the level-1 warp — sits in the bottom lane at x 58,856, right after a
  wall, near the end of section 5. Touching it is the 3→5 mega-warp to Surf City. The route wants 3→4→6, so it
  gets a slide to the top lane, not a landing.

Twenty-four learned overrides on top of the rules cover the cases reacting cannot: a second wall that lands in the
dead zone after a jump, the middle lane before a trampoline, the timing on the two ground trampolines. From the
mount to the portal: 7,676 frames. The first policy needed a day to learn 36 walls blind; this one read the whole
course in an afternoon.

Journal 004 has the screenshot that made it possible.

## Section 5 (later the same day)

Past the portal the course runs at 12 px/frame and the walls alternate lanes every ~21 frames. A lane change takes
~26 frames and a jump lasts 55, so every reactive rule was one frame short, every time (three rewrites, three
deaths at 58,6xx–61,4xx). Rules were the wrong tool: I stopped reasoning and searched. `l3s.py` is a layered
breadth-first search over 4-frame holds (Left always; nothing / A / Up / Down / A+Up / A+Down) from x 56,000,
keeping every distinct (depth, height, rising) state per layer — never more than 400 — and letting the walls prune.
288 layers, 20 minutes, one path: the level ends at x 65,032 (the bike parks at 64,653), 8,290 frames from the
mount, 4 lives (a 1-up on the way), and the next screen is Level 4, Arctic Caverns.

The first beam version died out in 43 steps: at constant speed every node has the same x, so "furthest" ranked
nothing and the beam filled with doomed twins. Diversity by state, not score, was the fix.

## Level 4, first hour

Arctic Caverns opens on ice: the toad slides down the entrance slope by itself, two icicles drop on approach, and
a tall ice step needs a hop. Then an ice ball (HP 255) rolls down at you. Punching it when it is within 34 px
*stops* it; every kind of hit after that — punch, running punch, jump kick, headbutt — sends it up the slope at
exactly speed 192, apex x 626, and the checkpoint barrier sits at 640. Twenty experiments to learn that the
barrier also only takes hits while it is on screen, and the camera trails the toad by ~150 px.

The answer was in the TAS notes all along ("falling with the block on your hands"): stand within 10 px of the
stopped ball and press B — the toad lifts it overhead. Carry it up the slope until the slope stops you (x 538)
and press B again: thrown at speed 241, it shatters the barrier in 36 frames. Next: a snowman throwing snowballs
from the ledge behind, and the ball rolling back down at you.

Checkpoint 2 took the afternoon's second lesson: `h` wraps every 256 px, so the shaft's floors read 222, 126,
30, 222, 62 going *down*, and for an hour I hunted a platform that was only the ice block's own height. Once the
screenshots were read instead of the bytes, the answer was cheap: the block that bounces along the bottom floor
breaks the snowball stack on its own; the toad just has to get down there (floor 2 → ledge → floor → pit → slope)
and hop over it twice. 3,445 frames from the tunnel's end, checkpoint 2 open.

The bowl after the stack looked sealed: a snowman, two slopes, a wall each side, and forty probe jumps that found
nothing above or below. The exit was hiding in the screenshot — a ramp's lip hanging 85 px over the left slope,
ten more than a jump reaches. The TAS notes had the answer in passing: meet a higher floor's edge mid-jump and
the game lifts you onto it. A jump with Right held from x 258 lands on the ramp. Up it: a ledge, a slow spike, and
a snowman above lobbing bouncing snowballs down the shaft — three deaths to hand rules, so this stretch goes to
the search too.

Checkpoint 3 is a stack of snowballs on a ledge. Snowballs from a pile fly in the direction you *face*, and on
ice the slide flips you — hold Left together with B. Seven throws (every other one connects), then a searched
landing on the ledge's tip. Behind the ice pillar a yellow spiky ball rolls the ledge at four pixels a frame
and can't be killed (punching it eight times only got me a death and a checkpoint respawn — the "full health" I
briefly celebrated). Everything past the pillar is search work now: 4-frame holds, any HP loss is a dead branch,
and the endpoint must survive sixty idle frames, because twice the search "won" with an enemy one step away.

## Ruleset change and checkpoint 4 (2026-09-27, afternoon)

Two decisions from the owner today. The run now uses exactly the speedrun.com "Any% (No Credits Warp)" rules —
the same tricks the record holder uses (the Turbo Tunnel skip, the rat boot, the Level 9 wall skip), nothing the
board bans. The tunnel I spent the morning learning to ride will be skipped in the run and kept in the film. And
the plan is: finish a full verified run first, then cut time.

Checkpoint 4 fought back. The barrier object reports x 395 but the thing that hurt it was a snowball thrown by a
snowman at the bottom-left of a zig-zag shaft — not the ice block I spent an hour carrying, lifting and throwing
(the carry works exactly like checkpoint 1's; the throw just isn't the answer here). The shaft is a stack of short
icy ramps; stand still and the toad slides down them on its own. The search is now aimed at "any damage to the
barrier" with its ranking pointed at the barrier's real position instead of "up and right".

Checkpoint 4, resolved by evidence rather than theory: the wall at x 223 can't be walked or jumped, and the
toad only ever got past it because the bouncing block hit it from behind and threw it over. So the recipe uses
the hit on purpose: lift the block, throw it right from x 190, keep running, take the knock-back (−16 HP) and
land at x 264 — where the camera finally shows the barrier, and the snowman at the bottom of the shaft breaks
it for me, one snowball every 176 frames. The only skill left is dodging the block once while waiting. Four
emulators are running now (the owner asked why only one): two on Level 4, one grinding the rat section, one
that tried Level 1 and taught me the generic search is useless in the 3D levels.

Checkpoint 4 fell at 16:00: with the ranking told to *stay put* instead of "make progress", the search found the
one block-dodge in 285 seconds — 564 frames of standing at x 264 while the snowman's snowballs did the work.
Lesson filed: for a waiting game, rank by distance from where you want to stand.

Verified from power-on through checkpoint 4 and the loose block beyond it: 20,863 frames, four lives. The toad is
standing on a floating platform over a spike pit, riding it toward the next ledge while the searches figure out
the step-off.

Late afternoon, the bug. Every beam search that had "stalled" today — the rats, Level 1, the pillar floor —
stalled for the same reason: children were bucketed by position in 8-pixel cells and the *first* child in a cell
won, and the first action in the list is "do nothing". On flat ground a step moves one to three pixels, so the
walking child landed in the standing child's cell and was discarded, every layer, forever. The search could
not take a single step. Ice slopes, falls and platforms moved the toad far enough per step to hide it. One line
fixed: the better-ranked child keeps the cell. Four searches relaunched.

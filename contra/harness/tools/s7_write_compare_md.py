"""Write knowledge/s7_record_compare.md from the measured record timeline and the traces of our runs.

    python tools/s7_write_compare_md.py <first-pass run> <second-pass run> [more runs]

(each run needs logs/s7/<run>.trace.json: tools/s7_tr.py). Also refreshes knowledge/s7_record_landmarks.json.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import s7_record_compare as rc  # noqa: E402

names = sys.argv[1:]
sys.argv = [sys.argv[0]] + names
rc.main()
table = (ROOT / "logs" / "s7" / "record_compare_table.md").read_text(encoding="utf-8")
K = rc.K
tabs = [rc.table_for(n) for n in names]
old, new = tabs[0], tabs[1]
rk = rc.REC_EVENTS_VIDEO["door_core_first_explosion"] * K
lm = "| 0 | 128 | the camera rests until about 82 | 82 |\n" + "\n".join(
    f"| {c} | {c + 128} | {rc.REC8[c // 8]} | {rc.rec_at(c):.0f} |" for c in range(128, 3584, 128))
stops = "\n".join(f"| {s['video_from']} ({s['video_from'] * K:.0f}) | {s['frames']} | {s['cam']} / {s['cam'] + 128} | {s['what']} |"
                  for s in rc.REC_STALLS)
md = f"""# Stage 7 (Hangar): the record's run measured section by section, against ours

Second-pass builder, 2026-10-12. Record = Angrylanks 9:48.183 (https://www.youtube.com/watch?v=YgtFCclM1jM).
Machine-readable: `knowledge/s7_record_landmarks.json` (the record's camera position every 8 px, its stops, our
runs' rows). Tools: `tools/s7_record_compare.py`, `tools/s7_write_compare_md.py`, `tools/s7_tr.py`.

## How the record was measured

* The video is 60.000 fps; every image is two NES frames woven together (one per field). In the browser the video
  was paused and muted, each frame n was shown by seeking to (n + 0.5) / 60 and drawn to a canvas in the page.
* For every video frame 28250..32500 the background's horizontal shift against the previous frame was found from
  one field (49 scan lines x 256 columns, sum of absolute differences over shifts -1..6 px). The running sum of
  the shifts is the camera position (world x of the left screen edge). **Check: the sum reached 3,583 when the
  boss screen stopped; the true value is 3,584.** No frame had to be repeated (no stale reads, no timeouts).
* Offsets below are video frames counted from the stage's first medal frame (video frame 28262); NES frames =
  video x 60.0988 / 60 (+0.16 %). Tolerance of a landmark: +/-2 frames. Bill is at camera + 128 while he runs.
* What he does at each stop was looked at in magnified stills (6 per screenshot). Not measured: his exact inputs,
  his Barrier pick-up frame to better than about +/-5 frames, his bullets.
* Nothing was downloaded; the tab was closed afterwards.

## The record's stage 7 in one paragraph

{rc.REC_NOTES['route']}
Alley: {rc.REC_NOTES['alley']}
Carts: {rc.REC_NOTES['carts']}
Boss: {rc.REC_NOTES['boss']}
Pauses: {rc.REC_NOTES['pauses']}
After the door: control lost at video 3984, first black 4226, stage 8's medals 4481 = **4,488 NES frames**.

### His stops (every stretch of 7+ video frames without scrolling)

| from video frame (NES) | frames | camera / Bill's x | what he does |
|---|---|---|---|
{stops}

Sum of his stops: 112 frames. He never waits in Heartbreak Alley.

### His camera every 128 px

| camera px | Bill's x | video frame | NES frame |
|---|---|---|---|
{lm}
| 3583 (scroll over) | - | 3733 | {3733 * K:.0f} |
| door core's first explosion | - | 3788 | {rk:.0f} |
| stage 8 medals | - | 4481 | 4488 |

## Section by section: record, first pass (`{old['run']}`, {old['segment']}), second pass (`{new['run']}`, {new['segment']})

Rows = frames from the stage's first frame. "in it" = frames spent in the section; "at its end" = row at which the
camera reaches the section's end; in brackets the difference to the record at that point (negative = we are ahead).

{table}
## Where he was faster than the first pass, and what was done about it

| section | first pass lost to him | why | second pass |
|---|---|---|---|
| Heartbreak Alley (camera 2272-2448) | 121 frames (137 behind after it) | he is INVINCIBLE there: he takes the Barrier from the pill box at x 1552 and simply runs under the five "seeking" claws; the first pass had no Barrier and baited / waited at every claw | same route: cart 1424 by a "Chariot Hop", small ledge, a jump over the pill box with a down-forward shot, the item caught in the air, drop through the ledge; the alley is then a straight run (and no longer depends on `$1A` mod 256) |
| pit and floor before it (2048-2272) | 17 | a sniper and the cart, handled by repair jumps | free with the Barrier; the pit jump is chosen to land on the cart's rear edge |
| two rising walls (688-832) | 14 | same wall-top jumps as his, but with a 4-frame pull-back and a later jump to the step | jump to the step from x 762 (the first point clear of the claw at 758), no pull-back: equal to him |
| boss (scroll start to door dead) | 25 (his 150 frames, ours 175) | he jumps during the reveal scroll and fires level with the core; the first pass's beam search never jumped | scripted fight found by a grid: one jump timed so that Bill falls through the core's height as the scroll ends, then up-forward volleys while walking to the cap: 143 frames in the two chain solves shown here, 143-155 over all solves |
| carts | about 15 over three carts | he lands on the rear edge of each cart | rear-edge landings chosen by trial on all four carts |

Everything else (screen 1, tall walls, claw corridor, six claws, gunners) the first pass already did as fast as
he or faster: he waits 21 frames at the claw corridor, 31 at the six claws, 14 at the gunners; we use 5-frame
pauses over the claws' trigger frames.

## Where the second pass is ahead of him ({new['run']})

At the door's death we are {new['door_hp0_row'] - rk:+.0f} frames against the record ({new['door_hp0_row']} against {rk:.0f});
the {new['segment'] - new['door_hp0_row']} frames after the kill are fixed by the game (his: 694).
The lead comes from: the claw corridor (no wait at this phase against his 21 frames), the cart 1424 and the B
grab (the forced 17-frame drop, nothing else: 8 frames less than he needs there), the trio (4 frames lost against
his 11: volleys timed so that walls 2 and 3 are dead on arrival; wall 1 is broken by touch while the Barrier
still runs), the six claws (two 5-frame pauses against his two waits of 12 and 19), the gunners (shot from
further away, one duck), the door (143 frames against 150), rear-edge cart landings, and almost no lag in play
(3 lag frames before the load).
"""
p = ROOT / "knowledge" / "s7_record_compare.md"
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(md, encoding="utf-8")
tmp.replace(p)
print("wrote", p)

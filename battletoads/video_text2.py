"""Text for the run video, route-agnostic (2026-10-01): the side panel's WHAT || WHY entries, the narration
captions (.captions.txt, .srt, readable script) and the token-counter keyframes with what each stretch's tokens
were spent on. Level frames come from the route's own trace (level byte changes), so any verified route works.

    python video_text2.py <route>

Writes logs/<route>.events.txt, logs/<route>.captions.txt, video/<route>.srt, video/<route>_script.md and
logs/<route>.tokens.json (keyframes {"frame", "tokens", "cost", "label", "why"}).
Level 12's inner moments are placed proportionally from the old WIP's section frames
(knowledge/l12_section_frames.json) unless knowledge/l12_section_frames_<route>.json exists.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS, VIDEO, K = HERE / "logs", HERE / "video", HERE / "knowledge"
FPS = 60.0988
ORDER = [1, 3, 4, 8, 7, 11, 9, 10, 5, 13]                 # level bytes in run order
NAME = {1: "L1", 3: "L3", 4: "L4", 8: "L6", 7: "L8", 11: "L9", 9: "L10", 10: "L11", 5: "L12", 13: "L13"}


def frames(route):
    """level enter frames by name, clock start, finish (cut to T. Bird), total frames"""
    F = {}
    clock = finish = None
    prev_lv = prev_an = None
    n = 0
    for ln in (LOGS / f"{route}.trace.txt").read_text().splitlines():
        fr, _, st = ln.split("\t")
        k = int(fr)
        n = k
        kv = dict(t.split("=") for t in st.split())
        lv, an = int(kv["level"]), int(kv.get("anim", 0))
        if clock is None and lv == 1 and prev_an == 5 and an == 4:
            clock = k
        if lv != prev_lv and lv in NAME and NAME[lv] not in F:
            F[NAME[lv]] = k
        if "L13" in F and lv == 254 and finish is None and k > F["L13"] + 300:
            finish = k
        if "L1" in F and "L1end" not in F and lv == 254 and k > F["L1"] + 100:
            F["L1end"] = k
        prev_lv, prev_an = lv, an
    F["clock"], F["finish"], F["total"] = clock, finish, n
    return F


def fmt_srt(frame):
    t = max(0.0, (frame - 1) / FPS)
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h:02d}:{m:02d}:{t % 60:06.3f}".replace(".", ",")


def build(route):
    F = frames(route)
    wr = json.load(open(K / "wr_splits.json"))
    L1, L3, L4, L6, L8, L9, L10, L11, L12, L13 = (F.get(x) for x in ("L1", "L3", "L4", "L6", "L8", "L9", "L10", "L11", "L12", "L13"))
    clock, finish, total = F["clock"], F["finish"], F["total"]
    skip = (L4 - L3) < 6000                               # the Turbo Tunnel skip route
    # Level 12 inner frames: scaled from the WIP's section table
    p = K / f"l12_section_frames_{route}.json"
    sec = json.load(open(p if p.exists() else K / "l12_section_frames.json"))
    s0, s1 = sec[0][1], sec[-1][1] + sec[-1][2]
    l12_len = (L13 or total) - L12 if L12 else 0
    def S(name, extra=0):
        f = next(a for n_, a, _ in sec if n_ == name) + extra
        return int(L12 + 40 + (f - s0) / (s1 - s0) * max(1, l12_len - 60)) if not p.exists() else f

    ev, cap = [], []
    # (lists regenerated 2026-10-05 from the up9 outputs after the source file was lost; level-relative frames)
    ev += [
        (1, 'POWER ON. Right held from frame 1: with a direction held through the logos the title accepts Start 349 frames sooner.||Found by pressing Start on every frame from 1,161'),
        (1171, 'START on the first frame the title counts it.||1,169 is ignored - bisected'),
        (1175, 'Holding A: each story page closes the moment the game allows it.||Nothing, Start, Select, directions: all slower'),
        (clock - 170, "LEVEL 1: RAGNAROK'S CANYON. The clock starts when the toad lands.||speedrun.com Any% (No Credits Warp)"),
        (clock - 150, 'The left pig first, the moment it can be hurt; then ONE dash to the right: ram the second pig on the way, dash-jump onto the rock, portal.||First version headbutted leftwards and had to come back: 300 frames, now 239'),
        (clock + 395, 'MEGA WARP to LEVEL 3 - a designed shortcut, skips level 2. Start mashed through every cutscene page.||Cutscenes are on the clock: nothing 860 f, Start held 673 f, mashed 191 f'),
        (L3 + 40, "LEVEL 3: TURBO TUNNEL. A tool-assisted run's own inputs for as long as they are legal: frame for frame through the first three rats.||It breaks at that run's first Left+Right press (banned)"),
        (L3 + 780, 'TWO BLOWS PER RAT: a flying attack (jump, B in the air) stuns it, then THE BOOT - dash, B, a 24-frame wind-up - kills it whatever its health.||About 95 frames per rat; our first searches took 324 to 655'),
        (L3 + 1050, 'This rat drops in BEHIND the toad when the camera reaches the pit. Jump back at it while it is still falling, boot it, then the pit.||While a rat lives the camera will not scroll'),
        (L3 + 1340, 'Third rat: back off, flying attack to the right, boot. After a boot the game refuses a dash for 11 frames - the reference run cheats that with Left+Right.||We wait the 11 frames'),
        (L3 + 1646, "THE BIKE SKIP. Mount, roll the bike back with Left+Up taps, drive it into the gap between the lanes before the first checkpoint saves.||The respawn then reads the level's object list from the wrong memory"),
        (L3 + 1836, "Respawned with the object-list pointer inside the game's own variables: it walks through live memory, 11 bytes a frame.||When it reaches a byte holding 127 it spawns object 127 - the level-end fireworks"),
        (L3 + 2116, 'Object 127 spawned: the level is over. The whole 2.3-minute bike course never happens.||Allowed in Any% (No Credits Warp); costs one life'),
        (L4 + 30, "LEVEL 4: ARCTIC CAVERNS. The intro page skips on any button. Then the reference run's own inputs, frame for frame, through three checkpoints.||Its inputs are legal until its first Left+Right press"),
        (L4 + 1560, 'The reference run stops the ice block with a banned press. Legal version: brake, wait 26 frames, grab it - then a search carries it down the shaft into barrier 4.||53 frames instead of its 60'),
        (L4 + 2100, "CHECKPOINT 5, THE TAS'S WAY: keep Right held through the landing - a flying kick ON the landing frame keeps the sprint - drop at the wall, dash-jump left, kick the snowman from the air, two throws from its pile.||The 1-player TAS's own inputs replay from our sprint; we run 1 px behind, so each landing is re-synced by repeating the input"),
        (L4 + 2750, 'THE DAMAGE BOOST (from the world record run). The ice ball sweeps the pit floor every 192 frames: take the hit on the ice slide at x 185, get up, walk into the spikes while still invulnerable.||Getting up, the toad is invulnerable for half a second: long enough to walk INTO the spikes'),
        (L4 + 2935, '...and fall through them, through the rock, into the chamber two screens down. The floating platforms and the whole switchback never happen.||Hold Left in the fall or the game puts the toad off screen'),
        (L4 + 3020, "But the game spawns objects from a list that waits on the camera - and the list is now stuck on the part we skipped. Run RIGHT until the camera has satisfied it.||Read from the game's code: one list entry per frame"),
        (L4 + 3220, 'Now the barrier, the ice ball and the spiky ball exist. Punch the rolling ball (that lifts it), carry it to the pillar top, face right, throw.||It grinds the 255-point barrier down in 3 seconds'),
        (L4 + 3695, "Left over the spiked dip, down the shaft, along the ledges to barrier 7 - which only the snowmen's own snowballs can break. Crouch under the fast ones, hop the slow ones.||About 10 shots; dash off behind the last one"),
        (L4 + 4710, "The lift sinks under the toad; the portal only appears once the camera is low enough. Then back up: lift, the ledge's lower lip, the portal.||Designed warp to level 6"),
        (L6 + 40, "LEVEL 6: KARNATH'S LAIR. Snakes are the platforms - their heads pause at corners and lift you.||The exit is three screens up: a double jump off the third snake's head"),
        (L8 + 60, "LEVEL 8: INTRUDER EXCLUDER. A 4,000-px tower: every jump peaks exactly at the next floor's edge; moving electric holes and elevators timed by beam search.||Then Robo-Manus: 21 smashes"),
        (L8 + 3320, 'ROBO-MANUS. Which attack B gives is random - and the game stirs its random numbers with spare CPU time. SELECT does nothing in play, but costs CPU time: press it on the right frame and the dice land differently.||The AI re-rolls each of ~25 random decisions until the fight replays an earlier winning one'),
        (L8 + 4782, "THE BRIEFING PAGES. Our first run sat on every 'LEVEL n' page for four seconds. The record's video shows one. A fresh A press every other frame skips it.||~230 frames at each of levels 9-12: 15 s found by watching the record"),
        (L9 + 40, 'LEVEL 9: TERRA TUBES. The start wall has no collision on top: over it and down the outside of the level.||Out of bounds is allowed in this category'),
        (L9 + 1400, "Through a spark-guarded pipe, then four giant gears (Krazy Kogs) that only start moving when they see you.||The beam follows a 1-player TAS's path, with scripted waits for each gear"),
        (L9 + 9586, 'The level ends while dying on the last spikes - the exit trigger counts.||Allowed: an end-of-stage trigger'),
        (L10 + 40, "LEVEL 10: RAT RACE. Out-race the rat down the shaft, kick its bomb, then the RAT BOOT: a hard hit, then a second running kick.||The 1-player TAS's own inputs: no banned press in this level, so they replay frame for frame (2 s found)"),
        (L11 + 40, 'LEVEL 11: CLINGER-WINGER. The unicycle maze with the Buzzball behind. Turn at every arrow before you reach it.||The TAS pressed Up+Down here (banned) - this is our own legal controller'),
        (L11 + 5200, "THE BUZZBALL, THE RECORD'S WAY: stand ~30 px from the wall and kick every 40 frames - the ball bounces off the wall straight back into every kick.||13 kicks in ~780 frames; the old chase around the room needed 985"),
        (L12 + 40, 'LEVEL 12: THE REVOLUTION. A rotating tower. Sprints by double tap, platforms that sink and launch, enemies that lock the camera.||The hardest level to make legal: the reference run leans on Left+Right'),
        (L12 + 1260, 'KILL the Hornhead - 3 hits.||While a Hornhead lives the camera will not scroll, and the ledge above never appears'),
        (L12 + 2146, "THE FIGHTS, THE TAS'S WAY: the 1-player TAS's own kicks replay from a sync point, one idle frame placed to match the Hornhead's wake-up grid; SELECT re-rolls where the dice differ.||Nine fights: 15 s found; two more killed by our own beam"),
        (L12 + 3347, 'A boss cloud that only comes down when the random number generator says so.||Every button press changes the generator'),
        (L12 + 5343, 'WIND FACE 1: grab the pole, hang on, let go when it leaves.||The face locks the camera too'),
        (L12 + 6600, "THE SINKING PLATFORM. The old line walked the long way round the tower to the reference run's spot and then waited a lap for the platform. Walk the short way: the same phase comes a lap earlier.||69 frames instead of 360: 256 saved"),
        (L12 + 7023, 'WIND FACE 2: pole, wait, drop straight onto the higher platform.||'),
        (L12 + 7753, 'WIND FACE 3: jump INTO the wind - it carries the toad 230 px to the pole.||'),
        (L12 + 7932, "THE LAST POLE: the old run idled 204 frames on the circling platform before its jump; 174 of them go - the spring platform still launches to the pole.||Dropping the old route's idle frames: 256 + 174 + 88 frames in the tail"),
        (L12 + 8985, 'THE TOP. The TAS scrolls the camera with Left+Right to end the level early (banned). We climb.||Two small platforms, then the spring: hold A, the camera reaches the top, level over'),
    ]
    if l12_len and l12_len < 8950:                          # L12g: faces 3 and 4 too
        ev = [(f, t) for f, t in ev if not (L12 + 5200 <= f <= L12 + 9000)]
        ev += [
            (L12 + 5230, "THE TAS'S KILL: kick, walk AWAY, then turn back with Right+B - the big boot finishes the Hornhead in two hits.||Frame for frame from the 1-player TAS (its Left+Right presses swapped for legal ones)"),
            (L12 + 5370, "PUMP THE SPRING: hold A as it sinks - it throws the toad up, the camera follows, and wind face 2 appears while the toad is still in the air.||Face 2 now 80 frames sooner"),
            (L12 + 6000, "WIND FACE 2 ends sooner, so the lift comes sooner: the old drop and jump land exactly where they used to, 84 frames earlier.||"),
            (L12 + 6480, "The walker's dice changed with the new timing: its fight is re-solved (242 frames, old 243).||"),
            (L12 + 6790, "RIDE THE LOWER SPRING instead of jumping off it: face 3 is timed so this spring passes under the pole just as the wind stops.||118 frames of riding buy 240 later"),
            (L12 + 7358, "Drop while the wind is still blowing, land on the spring, pump - and up to the next spring.||The record does this drop too"),
            (L12 + 7480, "Pump again: straight onto the face-4 pole. Face 4 appears 88 frames sooner.||"),
            (L12 + 7939, "Face 4: drop onto the circling spring, run with it, jump: the ledge 154 frames sooner than before.||"),
            (L12 + 8496, "THE TOP: walk along the slow moving platform instead of standing on it.||53 frames"),
        ]
    elif l12_len and l12_len < 9100:                          # 2026-10-07 Revolution (L12f): face 2 the TAS's way, the top walked
        ev = [(f, t) for f, t in ev if not (L12 + 5200 <= f <= L12 + 9000)]
        ev += [
            (L12 + 5230, "THE TAS'S KILL: kick, walk AWAY, then turn back with Right+B - the big boot finishes the Hornhead in two hits.||Frame for frame from the 1-player TAS (its Left+Right presses swapped for legal ones)"),
            (L12 + 5370, "PUMP THE SPRING: hold A as it sinks - it throws the toad up, the camera follows, and wind face 2 appears while the toad is still in the air.||Face 2 now 80 frames sooner; the toad lands right on its pole"),
            (L12 + 6000, "WIND FACE 2 ends sooner, so the lift comes sooner: the old drop and jump replayed 84 frames earlier land exactly where they used to.||Same landing, same camera - 84 frames gained"),
            (L12 + 6150, "THE BIG BOOT and THE LAP, as before: run at the Hornhead, catch the circling platform a lap early.||"),
            (L12 + 6480, "The walker's dice changed with the new timing: its fight is re-solved (242 frames, old 243).||"),
            (L12 + 7425, 'WIND FACE 3: jump INTO the wind - it carries the toad 230 px to the pole.||'),
            (L12 + 8650, "THE TOP: walk along the slow moving platform instead of standing on it for 124 frames.||53 frames"),
        ]
    elif l12_len and l12_len < 9300:                          # the 2026-10-06 Revolution (L12q3): big boot + the lap caught early
        ev = [(f, t) for f, t in ev if not (L12 + 6500 <= f <= L12 + 9000)]
        ev += [
            (L12 + 6240, "THE BIG BOOT. One kick, then RUN at it and press the direction with B: the lunge does 47 damage - a Hornhead with 47 left dies in one blow.||Old: four kicks, 239 frames. New: 127. The 1-player TAS does this at its frame 74914"),
            (L12 + 6400, "THE LAP. The circling platform comes round every 256 frames. Walk INTO it, jump on, pump it at once: the launch comes one lap early.||260 frames earlier than the old line at the walker's platform"),
            (L12 + 6600, "The walker, then the jump onto the next platform timed to where that platform actually is (x 334).||The lap shifted its phase; the old inputs after it replay with every landing re-synced"),
            (L12 + 6790, 'WIND FACE 2: pole, wait, drop straight onto the higher platform.||'),
            (L12 + 7505, 'WIND FACE 3: jump INTO the wind - it carries the toad 230 px to the pole.||'),
            (L12 + 7684, "THE LAST POLE: the spring platform launches to the pole.||"),
            (L12 + 8737, 'THE TOP. The TAS scrolls the camera with Left+Right to end the level early (banned). We climb.||Two small platforms, then the spring: hold A, the camera reaches the top, level over'),
        ]
    cap += [
        (1, 'This is Battletoads on the NES. Every input from here to the end comes from an AI - nobody is touching the controller.'),
        (clock - 1654, 'Same rules as the speedrun world record: Any%, no credits warp. No cheat codes, and no pressing left and right at the same time.'),
        (clock - 1074, 'First trick is before the game even starts: holding Right through the logos lets the title accept Start 349 frames early.'),
        (clock - 574, "The timer top right starts when the toad lands. The gold bar under it is the world record's pace - the green one is ours."),
        (clock - 60, 'The speedrun clock starts now.'),
        (clock + 150, 'One headbutt kills a pig. So: left pig, then one long dash to the right - second pig, the rock, and a portal most players never find.'),
        (clock + 395, 'That portal is a real shortcut the designers left in. It skips level 2 entirely.'),
        (L3 + 60, 'Turbo Tunnel - the level that ended a lot of childhoods. The bikes come later. First, rats.'),
        (L3 + 780, 'The first version of this AI needed up to eleven seconds per rat. Then it studied a tool-assisted run: a flying kick to stun, then a running boot. Two hits. A second and a half.'),
        (L3 + 1340, "That reference run presses left and right at the same time to cancel a recovery animation. That's banned here - so we wait eleven frames and do it the honest way."),
        (L3 + 1526, "Here's the biggest time save in the run. The first version of this AI rode the whole bike course - two minutes and eighteen seconds of it."),
        (L3 + 1706, 'The record skips it. Drive the bike into a pit before the first checkpoint, and the game respawns you with a pointer aimed at the wrong memory.'),
        (L3 + 1946, 'The game starts reading its own variables as if they were a list of enemies. One of those bytes happens to be 127 - the object that ends a level.'),
        (L3 + 2146, "The AI found this by reading the game's machine code. The catch: the bike has to crash on the exact frame the pointer jumps - its wreckage has to be sitting in three particular memory slots."),
        (L4 + 30, 'Arctic Caverns. The first version of this level took three minutes twenty. This one is a minute and a half.'),
        (L4 + 1560, "Here the reference run presses left and right together to stop the ice block. That's banned. So the AI found its own way to grab it - seven frames faster."),
        (L4 + 2100, "Checkpoint five. The old version walked the whole floor and threw snowballs for six seconds. This is the tool-assisted run's own inputs: a flying kick on the landing frame keeps the sprint, drop at the wall, kick the snowman out of the air. Seven seconds faster."),
        (L4 + 2700, 'Now watch this. This trick is straight from the world record: get hit on purpose, right at the edge of the spike pit.'),
        (L4 + 2935, 'For half a second after getting up, nothing can hurt you. So you walk into the spikes - and fall straight through the floor.'),
        (L4 + 3020, "It skips half a minute. But it also breaks the level: the game's list of things to spawn is still waiting for a part of the map we never visited. Nothing ahead of us exists."),
        (L4 + 3140, 'The AI read the spawning code, found what the list was waiting for, and ran the camera over there to satisfy it.'),
        (L4 + 3695, "This barrier can't be punched. Only the snowmen's own snowballs break it. So you crouch here and let them do the work."),
        (L6 + 40, "Karnath's Lair. The snakes are the floor. The way out is three screens up, off the last snake's head."),
        (L8 + 60, "Intruder Excluder. A 4,000-pixel climb where every jump tops out exactly on the next floor's edge."),
        (L8 + 3200, 'Robo-Manus at the top. Whether B gives a punch, a kick or the big smash is random.'),
        (L8 + 3600, "And here's a strange one. Every change earlier in the run reshuffles the game's random numbers. But the Select button - which does nothing - changes how long a frame takes to compute, and that changes the shuffle."),
        (L8 + 4000, "So when an old winning fight stops working, the AI doesn't solve it again. It presses Select on the right frame until the dice land the way they did before."),
        (L8 + 4782, 'Quick aside. Watch the gap between levels: about a second. Our first run sat on this page for four. That came from watching the record frame by frame - fifteen seconds for free.'),
        (L9 + 40, 'Terra Tubes. The wall at the start has no collision on top, so we go over it and down the outside of the level.'),
        (L9 + 1400, 'The route came from a tool-assisted run. The AI follows its path - but the gears only move when they see you, so it has to wait for each one.'),
        (L9 + 9586, 'The level ends by dying on the last spikes. The exit trigger still counts, and the rules allow it.'),
        (L10 + 40, "Rat Race. This level is the tool-assisted run's own inputs, frame for frame: nothing banned in it, so the AI just borrowed it. Beat the rat down, kick its bomb, then the rat boot: two exact kicks that end the level early."),
        (L11 + 40, 'Clinger-Winger. The reference run pressed up and down together here, which is banned. So the AI got its own controller for every corner.'),
        (L11 + 5250, 'The Buzzball. The old version chased it around the room. The record stands near the wall and kicks on a rhythm, and the ball bounces straight back into every kick. Thirteen kicks.'),
        (L12 + 40, "The Revolution. This one tower took more work than any other level. Here's why."),
        (L12 + 808, 'The reference run sprints with left and right held at once. The legal way is a double tap - and you have to finish turning first.'),
        (L12 + 1260, "Big discovery: while one of these horned enemies is alive, the camera won't scroll up - so the platforms above never show up."),
        (L12 + 3347, 'The big one waits for the random number generator. Every button press - even Select - changes it. So the AI presses buttons until it comes.'),
        (L12 + 4124, "Here's the weird one: the reference run's left-right presses left its toad a fraction of a pixel off. We can never match that exactly."),
        (L12 + 5343, 'The wind faces. Stand in the open and the wind blows you right off the tower. So you grab a pole and hang on.'),
        (L12 + 6620, 'This platform circles the tower. The old run walked the long way round to where the reference run stood, then waited a whole lap for it. Walk the short way and the same moment comes a lap earlier. Four seconds.'),
        (L12 + 7753, 'Number three. This time you have to jump into the wind on purpose - it carries you 230 pixels to the pole.'),
        (L12 + 8985, 'The top. The reference run uses a banned left-right trick to scroll the camera and end the level early. We have to actually climb it.'),
    ]
    if l12_len and l12_len < 8950:
        cap = [(f, t) for f, t in cap if not (L12 + 5200 <= f <= L12 + 9000)]
        cap += [
            (L12 + 5230, "Here's a trick from the tool-assisted run: kick him, walk away, then turn back and kick. That's the big boot - two hits instead of three."),
            (L12 + 5370, "Now the spring. Hold A while it sinks and it throws you up. The camera follows you up - and that's what makes the wind face appear. Eighty frames sooner than before."),
            (L12 + 6790, "This is the one the record holder does. Stay on this spring. Ride it round, so that when the wind stops, the spring is right under the pole."),
            (L12 + 7358, "Let go while the wind is still blowing - land on the spring - pump - and up to the next one."),
            (L12 + 7480, "One more pump, straight onto the last wind face's pole. That whole stretch is about four seconds faster."),
            (L12 + 8496, "And at the top: don't ride this slow platform, walk along it. Another second."),
        ]
    elif l12_len and l12_len < 9100:
        cap = [(f, t) for f, t in cap if not (L12 + 5200 <= f <= L12 + 9000)]
        cap += [
            (L12 + 5230, "Here's a trick from the tool-assisted run: kick him, walk away, then turn back and kick. That's the big boot - two hits instead of three."),
            (L12 + 5370, "Now the spring. Hold A while it sinks and it throws you up. The camera follows you up - and that's what makes the wind face appear. Eighty frames sooner than before."),
            (L12 + 6000, "Because the wind came sooner, it also ends sooner - and the same drop and jump land in exactly the same spot, almost a second and a half earlier."),
            (L12 + 8650, "And at the top: don't ride this slow platform, walk along it. Another second."),
        ]
    elif l12_len and l12_len < 9300:
        cap = [(f, t) for f, t in cap if not (L12 + 6500 <= f <= L12 + 9000)]
        cap += [
            (L12 + 6240, "The big boot. Kick once, then run at it and press the direction with B. The lunge does forty-seven damage. One blow instead of three more kicks."),
            (L12 + 6400, "And that kill is early enough to catch this circling platform a whole lap sooner. Walk into it, jump on, pump it - launched. Four seconds, and that lap carries all the way to the top of the tower."),
            (L12 + 7505, 'Number three. This time you have to jump into the wind on purpose - it carries you 230 pixels to the pole.'),
            (L12 + 8737, 'The top. The reference run uses a banned left-right trick to scroll the camera and end the level early. We have to actually climb it.'),
        ]
    if L13:
        ev.append((L13 + 20, "LEVEL 13: ARMAGEDDON - THE DARK QUEEN. Beam search on the hit counter.||RAM $586: +12 per hit, "
                             "240 after 20 hits; the 21st finishes her"))
        cap.append((L13 + 20, "Armageddon. The Dark Queen. The game keeps her hit count in one byte of memory: 12 per hit. Twenty hits fill it - and it takes one more to finish her."))
    if finish:
        t = (finish - clock) / FPS
        d = t - wr["total"]
        ev.append((finish - 666, "THE DARK QUEEN IS DOWN - 21st hit.||The clock stops at the cut to Professor T. Bird"))
        ev.append((finish, f"TIME: {int(t // 60)}:{t % 60:06.3f}||World record: 12:29.250 ({'+' if d >= 0 else '-'}{abs(d):.1f} s)"))
        cap.append((finish - 666, "Twenty-one hits. The Dark Queen is done."))
        cap.append((finish, f"That's the game. {int(t // 60)} minutes {t % 60:.1f} seconds on the speedrun clock. The world record is 12:29."))
    ev = sorted(e for e in ev if e[0] and e[0] > 0)
    cap = sorted(c for c in cap if c[0] and c[0] > 0)
    (LOGS / f"{route}.events.txt").write_text("\n".join(f"{f}\t{t}" for f, t in ev) + "\n")
    rows = []
    for i, (f, t) in enumerate(cap):
        nxt = cap[i + 1][0] if i + 1 < len(cap) else total
        end = min(nxt - 6, f + 480, total)
        rows.append((f, max(end, f + 120), t))
    (LOGS / f"{route}.captions.txt").write_text("\n".join(f"{a}\t{b}\t{t}" for a, b, t in rows) + "\n", encoding="utf-8")
    srt = []
    for i, (a, b, t) in enumerate(rows, 1):
        srt += [str(i), f"{fmt_srt(a)} --> {fmt_srt(b)}", t, ""]
    VIDEO.mkdir(exist_ok=True)
    (VIDEO / f"{route}.srt").write_text("\n".join(srt), encoding="utf-8")
    md = [f"# Battletoads AI run - narration script ({route})", "",
          "Timestamps are video time (power-on = 0:00). The same lines are in the .srt.", ""]
    for a, b, t in rows:
        s = (a - 1) / FPS
        md += [f"**{int(s // 60)}:{s % 60:04.1f}**  {t}", ""]
    (VIDEO / f"{route}_script.md").write_text("\n".join(md), encoding="utf-8")

    # token keyframes: the build cost of each stretch (from the token marks of the first full run), placed at this
    # route's level ends, plus the second pass (chasing the record) spread over the levels it rebuilt
    why = json.load(open(K / "token_reasons.json"))
    base = [("first boot", 2088250, 6.03, 1), ("Level 1 solved", 107632706, 65.42, L3),
            ("Turbo Tunnel: to the bike", 141916836, 78.87, L4 - 640 if skip else L3 + 3700),
            ("Turbo Tunnel done", 229930079, 117.82, L4), ("Level 4 done", 575613634, 258.95, L6),
            ("Level 6 done", 713968363, 316.06, L8), ("Level 8 done", 741860904, 338.06, L9),
            ("Terra Tubes done", 931448178, 415.71, L10), ("Rat Race done", 972054418, 425.88, L11),
            ("Clinger-Winger done", 992711792, 430.96, L12),
            ("Revolution: the camera locks", 1075965334, 454.91, S("L12_g1640") if L12 else None),
            ("Revolution: three wind faces", 1281608570, 534.76, S("L12_gtop") if L12 else None),
            ("The Revolution done", 1331570496, 552.34, L13), ("The Dark Queen", 1368162350, 575.50, total)]
    sys.path.insert(0, str(HERE))
    from toads import tokens
    tt = tokens.totals()
    extra_t, extra_c = max(0, tt["total"] - base[-1][1]), max(0.0, tt["cost"] - base[-1][2])
    share = {"Turbo Tunnel done": 0.15, "Level 4 done": 0.45, "Level 8 done": 0.08, "Terra Tubes done": 0.08,
             "Rat Race done": 0.04, "Clinger-Winger done": 0.04, "The Revolution done": 0.12, "The Dark Queen": 0.04}
    second = {"Turbo Tunnel done": " Second pass: reading the game's code to make the bike skip work - 2 min 8 s saved.",
              "Level 4 done": " Second pass: rebuilt on a reference run's line, piece by piece - 90 s saved.",
              "Level 8 done": " Second pass: re-solved, because every change upstream reshuffles the random numbers."}
    keys, add_t, add_c = [], 0, 0.0
    for label, tok, cost, fr in base:
        if not fr:
            continue
        add_t += share.get(label, 0) * extra_t
        add_c += share.get(label, 0) * extra_c
        keys.append({"frame": int(fr), "tokens": int(tok + add_t), "cost": round(cost + add_c, 2), "label": label,
                     "why": why.get(label, label) + second.get(label, "")})
    keys.sort(key=lambda k: k["frame"])
    (LOGS / f"{route}.tokens.json").write_text(json.dumps(keys))
    print(f"{route}: {len(ev)} panel entries, {len(rows)} captions, {len(keys)} token keyframes; levels {F}")


if __name__ == "__main__":
    build(sys.argv[1])


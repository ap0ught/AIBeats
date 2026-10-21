"""Panel text, cue track, level splits and token keyframes for the corrected run video (2026-10-10).

    python yt/run_text.py <capture name> <segment> [<segment> ...]
        capture name = what yt/run_capture.py recorded (logs/<name>.trace.txt, video/<name>.mkv)
        segments     = the route's segments in order (logs/pbeam_<segment>.json), as given to assemble.py

Writes logs/<name>.events.txt (WHAT || WHY for the side panel), yt/run_cues_<name>.json (level slams, credits, the final
card), logs/<name>.levels.json (level enter / end frames; a level ends on the record's terms = the first black frame
after it, read from the capture itself) and logs/<name>.tokens.json (the published run's ledger plus what the recovery
cost, from logs/recovery_tokens.json).

The clock: the toad's landing in Level 1 to the cut to Professor T. Bird = the SECOND level-byte 13 -> 254.
"""
import json
import sys
from pathlib import Path

YT = Path(__file__).resolve().parent
TOADS = YT.parent
LOGS, VIDEO, K = TOADS / "logs", TOADS / "video", TOADS / "knowledge"
sys.path.insert(0, str(YT))
import style as S  # noqa: E402

FPS = 60.0988
INTRO = 1170 + 4 + 727 + 16                                # assemble.INTRO: the first segment starts on frame 1918
NAME = {1: "L1", 3: "L3", 4: "L4", 8: "L6", 7: "L8", 11: "L9", 9: "L10", 10: "L11", 5: "L12", 13: "L13"}
RECORD = 749.25


def read_trace(name):
    rows = []
    for ln in (LOGS / f"{name}.trace.txt").read_text().splitlines():
        fr, _, st = ln.split("\t")
        rows.append((int(fr), {k: int(v) for k, _, v in (t.partition("=") for t in st.split())}))
    return rows


def frames(rows):
    F, leave = {}, {}
    clock = None
    cuts = []
    last_hit = robo = robo_dead = None
    prev = {}
    for k, kv in rows:
        lv, an = kv.get("level"), kv.get("anim")
        pl = prev.get("level")
        if clock is None and lv == 1 and prev.get("anim") == 5 and an == 4:
            clock = k
        if lv != pl:
            if lv in NAME and NAME[lv] not in F:
                F[NAME[lv]] = k
            if pl in NAME and NAME[pl] not in leave:
                leave[NAME[pl]] = k
            if pl == 13 and lv == 254:
                cuts.append(k)
        if lv == 13 and prev.get("id3") == 0x7E and kv.get("id3") == 0x46:
            last_hit = k                                   # the 21st hit: the Queen's object turns into her dead body
        here = lv == 7 and any(kv.get(f"id{s}") == 0x7D for s in range(2, 8))
        if robo is None and here:
            robo = k
        if robo is not None and robo_dead is None and lv == 7 and not here and k > robo + 200:
            robo_dead = k
        prev = kv
    F.update(clock=clock, cut1=cuts[0] if cuts else None, finish=cuts[1] if len(cuts) > 1 else None, last_hit=last_hit,
             robo=robo, robo_dead=robo_dead, total=rows[-1][0])
    return F, leave


def first_black(dark, f, back=300):
    """first frame of the first black run (8 frames or more) in [f - back, f + 5]; f itself if there is none"""
    k = max(1, f - back)
    while k <= f + 5:
        if dark[k] < 6:
            j = k
            while j + 1 < len(dark) and dark[j + 1] < 6:
                j += 1
            if j - k + 1 >= 8:
                return k
            k = j + 1
        k += 1
    return f


def build(name, segs):
    rows = read_trace(name)
    F, leave = frames(rows)
    L1, L3, L4, L6, L8, L9, L10, L11, L12, L13 = (F.get(x) for x in ("L1", "L3", "L4", "L6", "L8", "L9", "L10", "L11", "L12", "L13"))
    clock, finish, cut1, hit, total = F["clock"], F["finish"], F["cut1"], F["last_hit"], F["total"]
    start, f = {}, INTRO + 1
    lens = {}
    for s in segs:
        start[s] = f
        lens[s] = len(json.loads((LOGS / f"pbeam_{s}.json").read_text())["inputs"])
        f += lens[s]
    assert f - 1 == finish, f"segments end on {f - 1}, the T. Bird cut is {finish}"
    s6, s8, s9, s12, s13 = (start[segs[i]] for i in (4, 5, 6, 9, 10))
    karnath_new = lens[segs[4]] < 2540                     # K6 / C6 / K7: the record's line in the warp room
    lap = lens[segs[9]] < 8300                             # T12a / T12x: one lap of the level clock gained in the tower
    sh = 258 if lap else 0                                 # the tower's second half comes this many frames sooner
    fight = (F["robo_dead"] - (s8 + 2753)) if F.get("robo_dead") else 652   # control is 2,753 inputs into the segment
    t = (finish - clock) / FPS
    tstr = f"{int(t // 60)}:{t % 60:05.2f}"

    ev = [
        (1, 'POWER ON. Right held from frame 1: with a direction held through the logos the title accepts Start 349 frames sooner.||Found by pressing Start on every frame from 1,161'),
        (1171, 'START on the first frame the title counts it.||1,169 is ignored - bisected'),
        (1175, 'Holding A: each story page closes the moment the game allows it.||Nothing, Start, Select, directions: all slower'),
        (clock - 170, "LEVEL 1: RAGNAROK'S CANYON. The clock starts when the toad lands.||speedrun.com Any% (No Credits Warp)"),
        (clock - 150, 'The left pig first, the moment it can be hurt; then ONE dash to the right: ram the second pig on the way, dash-jump onto the rock, portal.||First version headbutted leftwards and had to come back: 300 frames, now 239'),
        (clock + 395, 'MEGA WARP to LEVEL 3 - a designed shortcut, skips level 2. One fresh press on the first frame each page accepts it.||Cutscenes are on the clock: no press 860 f, a held button 673 f, fresh presses 191 f'),
        (L3 + 40, "LEVEL 3: TURBO TUNNEL. A tool-assisted run's own inputs for as long as they are legal: frame for frame through the first three rats.||It breaks at that run's first Left+Right press (banned)"),
        (L3 + 780, 'TWO BLOWS PER RAT: a flying attack (jump, B in the air) stuns it, then THE BOOT - dash, B, a 24-frame wind-up - kills it whatever its health.||About 95 frames per rat; our first searches took 324 to 655'),
        (L3 + 1050, 'This rat drops in BEHIND the toad when the camera reaches the pit. Jump back at it while it is still falling, boot it, then the pit.||While a rat lives the camera will not scroll'),
        (L3 + 1340, 'Third rat: back off, flying attack to the right, boot. After a boot the game refuses a dash for 11 frames - the reference run cheats that with Left+Right.||We wait the 11 frames'),
        (L3 + 1646, "THE BIKE SKIP. Mount, roll the bike back with Left+Up taps, drive it into the gap between the lanes before the first checkpoint saves.||The respawn then reads the level's object list from the wrong memory"),
        (L3 + 1836, "Respawned with the object-list pointer inside the game's own variables: it walks through live memory, 11 bytes a frame.||When it reaches a byte holding 127 it spawns object 127 - the level-end fireworks"),
        (L3 + 2116, 'Object 127 spawned: the level is over. The whole 2.3-minute bike course never happens.||Allowed in Any% (No Credits Warp); costs one life'),
        (L4 + 30, "LEVEL 4: ARCTIC CAVERNS. The intro page skips on any button. Then the reference run's own inputs, frame for frame, through three checkpoints.||Its inputs are legal until its first Left+Right press"),
        (L4 + 1560, 'The reference run stops the ice block with a banned press. Legal version: brake, wait 26 frames, grab it - then a search carries it down the shaft into barrier 4.||53 frames instead of its 60'),
        (L4 + 2100, "CHECKPOINT 5, THE TAS'S WAY: a flying kick ON the landing frame keeps the sprint - drop at the wall, dash-jump left, kick the snowman out of the air, two throws from its pile.||The 1-player TAS's own inputs replay from our sprint; we run 1 px behind, so each landing is re-synced by repeating the input"),
        (L4 + 2750, 'THE DAMAGE BOOST (from the world record run). The ice ball sweeps the pit floor every 192 frames: take the hit on the ice slide at x 185, get up, walk into the spikes while still invulnerable.||Getting up, the toad is invulnerable for half a second: long enough to walk INTO the spikes'),
        (L4 + 2935, '...and fall through them, through the rock, into the chamber two screens down. The floating platforms and the whole switchback never happen.||Hold Left in the fall or the game puts the toad off screen'),
        (L4 + 3020, "But the game spawns objects from a list that waits on the camera - and the list is now stuck on the part we skipped. Run RIGHT until the camera has satisfied it.||Read from the game's code: one list entry per frame"),
        (L4 + 3220, 'Now the barrier, the ice ball and the spiky ball exist. Punch the rolling ball (that lifts it), carry it to the pillar top, face right, throw.||It grinds the 255-point barrier down in 3 seconds'),
        (L4 + 3695, "Left over the spiked dip, down the shaft, along the ledges to barrier 7 - which only the snowmen's own snowballs can break. Crouch under the fast ones, hop the slow ones.||About 10 shots; dash off behind the last one"),
        (L4 + 4710, "The lift sinks under the toad; the portal only appears once the camera is low enough. Then back up: lift, the ledge's lower lip, the portal.||Designed warp to level 6"),
        (L6 + 40, "LEVEL 6: KARNATH'S LAIR. Snakes are the platforms - their heads pause at corners and lift you.||The exit is three screens up, off the third snake's head"),
    ]
    if karnath_new:
        ev += [
            (s6 + 1725, "THE LAST SNAKE OF ROOM 1: hop onto its body while it climbs and ride just behind the head - a snake's head stops for a frame whenever the toad is in its way.||Then one jump from the head, 56 frames in the air, straight into the exit"),
            (s6 + 2060, "THE WARP ROOM, THE RECORD'S WAY: tap Right, let go one frame, then Right+A together - a full-speed jump from a standstill. The toad grabs the rising snake and keeps that speed while Right+A stays held.||Up the body at 3 px a frame, over the head, onto the ledge still running: 90 frames"),
        ]
    ev += [
        (L8 + 60, "LEVEL 8: INTRUDER EXCLUDER. A 4,000-px tower, searched again: every node of the search is the toad standing somewhere unhurt, and the earliest arrival at each height wins.||The published run climbed it in 3,302 frames. This is 2,749"),
        (s8 + 900, "No waiting for old inputs to line up: the first jump leaves the moment the level lets go of the toad, and ten stalls of about a second each are gone.||617 frames of standing still in the published climb"),
        (s8 + 1600, "DUCK. These floors shoot sparks 22 px above the ground. The search could not get past them until it was given the Down button.||It had been told to jump, run, walk and stand - not to crouch"),
        (s8 + 2200, "Some gates up here open on the level's clock, not on the toad: arrive early and you wait. The top was searched again for the earlier openings.||About 3 seconds faster than the world record's own climb"),
        (F["robo"] or s8 + 2618, "ROBO-MANUS. The last jump of the climb stops short on purpose: the cutscene then hands the toad back 55 px closer to him.||Any further right and he lands on the toad"),
        ((F["robo"] or s8 + 2618) + 150, "PINNED. Only the jump-smash keeps him where he stands - every other blow knocks him across the room. Which blow B gives is a dice roll, and one SELECT press on an earlier frame re-rolls it.||21 smashes and the kill in " + str(fight) + " frames. The published run chased him for 1,087"),
        (leave["L8"] - 10, "THE BRIEFING PAGES. One fresh press on the first frame each page accepts it - the game reads three presses per page and nothing else.||The mashing in the published run was never needed"),
        (L9 + 40, 'LEVEL 9: TERRA TUBES. The start wall has no collision on top: over it and down the outside of the level.||Out of bounds is allowed in this category'),
        (L9 + 1400, "Through a spark-guarded pipe, then four giant gears (Krazy Kogs) that only start moving when they see you.||The beam follows a 1-player TAS's path, with scripted waits for each gear"),
        (s9 + 7780, "THE PROPELLER BUGS. They grab whatever passes under them slowly - and then carry it down this shaft at one pixel a frame. Leave the ledge at sprint speed: under both of them, and fall.||The published run was carried for 314 frames. 3.3 seconds, gone"),
        (leave["L9"] - 400, 'The level ends while dying on the last spikes - the exit trigger counts.||Allowed: an end-of-stage trigger'),
        (L10 + 40, "LEVEL 10: RAT RACE. Out-race the rat down the shaft, kick its bomb, then the RAT BOOT: a hard hit, then a second running kick.||The 1-player TAS's own inputs: no banned press in this level, so they replay frame for frame (2 s found)"),
        (L11 + 40, 'LEVEL 11: CLINGER-WINGER. The unicycle maze with the Buzzball behind. Turn at every arrow before you reach it.||The TAS pressed Up+Down here (banned) - this is our own legal controller'),
        (L11 + 5200, "THE BUZZBALL, THE RECORD'S WAY: stand ~30 px from the wall and kick every 40 frames - the ball bounces off the wall straight back into every kick.||13 kicks in ~780 frames; the old chase around the room needed 985"),
        (L12 + 40, 'LEVEL 12: THE REVOLUTION. A rotating tower. Sprints by double tap, platforms that sink and launch, enemies that lock the camera.||The hardest level to make legal: the reference run leans on Left+Right'),
    ]
    if lap:
        ev += [
            (s12 + 880, "THE SPRING STAIRCASE on the reference run's line: a fresh press of A the frame the toad lands on each spring. Its banned Left+Right frames are swapped for legal taps.||333 frames ahead of the published run by the next Hornhead"),
            (s12 + 1545, "A GROUND KICK, then the big boot. A flying kick lands sooner - but it scores 250 points more, and the Dark Queen's fight only replays if the score is exactly what it was.||Kick 750, flying kick 1,000, big boot 5,000"),
            (s12 + 1700, "The legal dash to the spring - tap, let go, hold - is 6 to 8 frames slower than the reference run's Left+Right. Still 357 frames ahead once the walker is dead.||"),
            (s12 + 2300, "STANDING STILL ON PURPOSE. The green ledges above are solid for only part of a 256-frame cycle. Being 344 frames early is no use: the toad gives 88 back and arrives one cycle early.||Any other gain would shift the timing of every fight and jump behind it"),
            (s12 + 3065, 'A boss cloud that only comes down when the random number generator says so.||Every button press changes the generator'),
        ]
    else:
        ev += [
            (L12 + 1260, 'KILL the Hornhead - 3 hits.||While a Hornhead lives the camera will not scroll, and the ledge above never appears'),
            (L12 + 2146, "THE FIGHTS, THE TAS'S WAY: the 1-player TAS's own kicks replay from a sync point, one idle frame placed to match the Hornhead's wake-up grid; SELECT re-rolls where the dice differ.||Nine fights: 15 s found; two more killed by our own beam"),
            (L12 + 3347, 'A boss cloud that only comes down when the random number generator says so.||Every button press changes the generator'),
        ]
    ev += [
        (s12 + 5200 - sh, "THE TAS'S KILL: kick, walk AWAY, then turn back with Right+B - the big boot finishes the Hornhead in two hits.||Frame for frame from the 1-player TAS (its Left+Right presses swapped for legal ones)"),
        (s12 + 5340 - sh, "PUMP THE SPRING: a FRESH press of A on landing - even inside the boot's recovery - starts the throw at once. Wind face 2 appears while the toad is still in the air.||A held from before the landing does nothing"),
        (s12 + 5440 - sh, "THE LEGAL INSTANT SPRINT: tap the direction, let go for a frame, hold it again on the launch frame - full speed at once. The reference run gets this with Left+Right (banned).||It is what makes that run's exit from wind face 2, its lift catch and its platform launches possible here"),
        (s12 + 5950 - sh, "The lift and the platforms above appear with the camera, not with the clock: every frame gained below carries straight up the tower.||" + str(129 + sh) + " frames ahead of the published run at this platform"),
        (s12 + 6270 - sh, "THE WALKER IS ONE JUGGLE, not five fights: a running kick, a second kick, two dash-jump air kicks while it hangs stunned - then a ram at sprint speed that kills it and carries the toad onto the spring.||Dead " + str(209 + sh) + " frames sooner than in the published run"),
        (s12 + 6546 - sh, "WIND FACE 3, " + str(408 + sh) + " frames sooner. The lower spring passes under its pole just as the wind stops: drop, pump, up.||A pole cannot be let go of while the wind blows"),
        (s12 + 7123 - sh, "WIND FACE 4, " + str(422 + sh) + " frames sooner.||The reference run scrolls the camera faster here with Left+Right; legally it climbs 1 px a frame"),
        (s12 + 7640 - sh, "THE TOP: sprint the last floor, a dash jump, a shorter last hop - then hold A on the top ledge until the camera arrives.||" + str(8880 - lens[segs[9]]) + " frames faster than the published tower"),
        (L13 + 20, "LEVEL 13: ARMAGEDDON - THE DARK QUEEN. Beam search on the hit counter.||RAM $586: +12 per hit, 240 after 20 hits; the 21st finishes her"),
        (L13 + 330, "THE JUGGLE: every blow is the jump-smash - 5 frames of freeze and no knockback - so she never leaves the spot. A hit every 44 or 45 frames.||A wide search (800 states) finds this line; a narrow one loses it"),
        (hit, "THE DARK QUEEN IS DOWN - 21st hit. The clock keeps running.||The rule: time ends at the cut to Professor T. Bird's dialogue"),
        (hit + 190, "Step aside. A toad standing where she comes back up is hit by her whirlwind.||27 frozen frames and a dead toad"),
        (hit + 390, "SELECT WHILE SHE RISES. The last scene waits on a leftover timer of hers, reloaded by the dice on her way up - and Select re-rolls the dice.||56 to 256 frames of waiting are decided here"),
        (cut1 - 2, "Her speech: skipped on the first frame the game reads the controller. One fresh press of A.||The published run's clock stopped HERE. That was the mistake"),
        (cut1 + 40, "Back on the tower: the rescued pair drops in, she rises once more, and her timer runs out.||340 frames nobody can shorten, then the dice"),
        (finish, f"TIME: {tstr} - the cut to Professor T. Bird.||World record: 12:29.25 ({t - RECORD:+.2f} s)"),
    ]
    ev = sorted(e for e in ev if e[0] and e[0] > 0)
    (LOGS / f"{name}.events.txt").write_text("\n".join(f"{f}\t{t_}" for f, t_ in ev) + "\n")

    # ---- level splits on the record's terms: a level ends on its first black frame
    from capsync import Sync
    sync = Sync(name)                                      # exact picture of every emulated frame (the dump repeats a few)
    dark = [255.0] + [sync.dark(k) for k in range(1, total + 1)] + [255.0] * 8
    lead = sync.first
    order = ["L1", "L3", "L4", "L6", "L8", "L9", "L10", "L11", "L12", "L13"]
    byte = {v: k for k, v in NAME.items()}
    levels = []
    for nm in order:
        end = finish if nm == "L13" else first_black(dark, leave[nm])
        levels.append([byte[nm], F[nm], end])
    (LOGS / f"{name}.levels.json").write_text(json.dumps({"clock": clock, "finish": finish, "queen_speech_cut": cut1,
                                                         "last_hit": hit, "lead_in": lead, "repeats": sync.dups, "levels": levels}, indent=1))

    # ---- cue track
    cues = [
        {"type": "level", "frame": clock - 170, "text": "LEVEL 1: RAGNAROK'S CANYON", "y": 340, "size": 70},
        {"type": "credit", "frame": clock - 170, "dur": 5, "title": "jay_cee — world record 12:29.25", "body": "the route and the time to beat", "pos": "top"},
        {"type": "credit", "frame": clock + 395, "dur": 5, "title": "jc583 — run notes (Speed Demos Archive)", "body": "warps, dash-jumps, the rat boot"},
        {"type": "level", "frame": L3 + 40, "text": "LEVEL 3: TURBO TUNNEL", "size": 70},
        {"type": "credit", "frame": L3 + 1646, "dur": 5, "title": "TASVideos #5093 — feos, Alyosha & Samsara", "body": "the bike skip mechanics and the tower fights"},
        {"type": "level", "frame": L4 + 30, "text": "LEVEL 4: ARCTIC CAVERNS", "size": 70},
        {"type": "level", "frame": L6 + 40, "text": "LEVEL 6: KARNATH'S LAIR", "size": 70},
        {"type": "credit", "frame": L6 + 40, "dur": 5, "title": "feos's disassembly + DataCrystal RAM map", "body": "how the game's memory is laid out"},
        {"type": "level", "frame": L8 + 60, "text": "LEVEL 8: INTRUDER EXCLUDER", "size": 70},
        {"type": "level", "frame": L9 + 40, "text": "LEVEL 9: TERRA TUBES", "size": 70},
        {"type": "level", "frame": L10 + 40, "text": "LEVEL 10: RAT RACE", "size": 70},
        {"type": "level", "frame": L11 + 40, "text": "LEVEL 11: CLINGER-WINGER", "size": 70},
        {"type": "level", "frame": L12 + 40, "text": "LEVEL 12: THE REVOLUTION", "size": 70},
        {"type": "credit", "frame": L12 + 40, "dur": 5, "title": "1-player TAS (feos, Alyosha, Samsara)", "body": "the Level 12 kills and spring pumps the AI copied"},
        {"type": "level", "frame": L13 + 20, "text": "LEVEL 13: ARMAGEDDON", "size": 70},
        {"type": "final", "frame": finish + 200, "dur": 1.5, "text": tstr,
         "sub": f"WORLD RECORD 12:29.25  ·  {RECORD - t:.2f} s FASTER",
         "sub2": "1 player  ·  human speedrun rules  ·  timed to the cut to Professor T. Bird"},
    ]
    (YT / f"run_cues_{name}.json").write_text(json.dumps(cues, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- tokens: the published run's ledger at this route's level frames, plus the recovery
    old = {k["label"]: k for k in json.loads((LOGS / "up14.tokens.json").read_text(encoding="utf-8"))}
    rec = json.loads((LOGS / "recovery_tokens.json").read_text(encoding="utf-8"))
    use17 = lap or karnath_new
    part = {}
    for r in rec["rows"]:
        if (r["part"] == "tower1" and not lap) or (r["part"] == "karnath" and not karnath_new) or (r["name"].startswith("wf_3c1656de") and not use17):
            continue
        a = part.setdefault("tower" if r["part"] == "tower1" else r["part"], [0, 0.0])
        a[0] += r["tokens"]
        a[1] += r["cost"]
    where = {"karnath": "Level 6 done", "level8": "Level 8 done", "terra": "Terra Tubes done", "tower": "The Revolution done",
             "queen": "The Dark Queen"}
    # the whole "why" of a stretch the recovery rebuilt (the panel shows four lines of about 60 characters)
    more = {"Level 6 done": "Snake geometry: which head to ride and where it pauses. Recovery: the warp room the record's way - a jump at full "
                            "run speed from a standstill, held all the way up the snake.",
            "Level 8 done": "A 'climb' search for the tower and a boss mode that ranks by smashes landed. Recovery: the climb searched "
                            "again by landings and taught to duck, the boss pinned in place - 16 seconds.",
            "Terra Tubes done": "Decoding a tool-assisted run frame by frame for the out-of-bounds route, then teaching the search to "
                                "follow it. Recovery: sprint under the propeller bugs instead of being carried - 3.3 s.",
            "The Revolution done": ("The top of the tower without the banned camera trick. Recovery: the tower rebuilt from the reference "
                                    "run's line with legal sprints, and one whole lap of the level's clock gained - 12 seconds.") if lap else
                                   ("The top of the tower without the banned camera trick. Recovery: the tower's second half rebuilt from "
                                    "the reference run's line with legal sprints - 7.8 seconds."),
            "The Dark Queen": "Finding her hit counter in memory, then 21 hits without taking one. Recovery: the correct end of the "
                              "run, a faster fight, a steered ending - and three independent checks of the clock."}
    place = [("first boot", 1), ("Level 1 solved", L3), ("Turbo Tunnel: to the bike", L4 - 640), ("Turbo Tunnel done", L4),
             ("Level 4 done", L6), ("Level 6 done", L8), ("Level 8 done", L9), ("Terra Tubes done", L10), ("Rat Race done", L11),
             ("Clinger-Winger done", L12), ("Revolution: the camera locks", L12 + 1810 - (130 if lap else 0)), ("Revolution: three wind faces", L13 - 430),
             ("The Revolution done", L13), ("The Dark Queen", finish)]
    add = {v: part.get(k, [0, 0.0]) for k, v in where.items()}
    keys, at, ac = [], 0, 0.0
    for label, fr in place:
        o = old[label]
        if label in add:
            at += add[label][0]
            ac += add[label][1]
        keys.append({"frame": int(fr), "tokens": int(o["tokens"] + at), "cost": round(o["cost"] + ac, 2), "label": label,
                     "why": more[label] if label in add and add[label][0] else o.get("why", label)})
    (LOGS / f"{name}.tokens.json").write_text(json.dumps(keys), encoding="utf-8")
    print(f"{name}: {len(ev)} panel entries, {len(cues)} cues, {len(keys)} token keys; clock {clock}, last hit {hit}, cuts {cut1}/{finish}, "
          f"time {tstr}; lead-in {lead}")
    print("levels (byte, enter, first black):", levels)
    print("tokens:", keys[-1]["tokens"], keys[-1]["cost"], "recovery parts:", {k: v for k, v in part.items()})


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2:])

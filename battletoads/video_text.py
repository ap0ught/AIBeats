"""Text for the run video: the side panel's WHAT || WHY entries, the narration script (captions, .srt, readable
script) and the token-counter keyframes.

    python video_text.py <route> [l13_segments...]

Frames are global (frame 1 = power-on). Level starts come from the verified routes; Level 12's sections from
knowledge/l12_section_frames.json; Level 13's from the fight sections passed on the command line.
Writes logs/<route>.events.txt (overwrites the assembler's coarse notes), logs/<route>.captions.txt,
video/<route>.srt, video/<route>_script.md and logs/<route>.tokens.json.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS, VIDEO, K = HERE / "logs", HERE / "video", HERE / "knowledge"
FPS = 60.0988

# level starts (first input of each segment), from the verified power-on routes
L1, WARP3, L3, L3B, BIKE, TUNNEL, L4, L6, L8, L9, L10, L11, L12 = (
    1918, 2375, 2811, 2996, 6269, 6305, 14595, 27045, 29705, 34781, 45000, 47297, 54703)
CLOCK = 2074          # the toad lands in level 1: the speedrun clock starts

L12S = {s: f for s, f, n in json.load(open(K / "l12_section_frames.json"))}

EVENTS = [
    (1, "POWER ON. Right held from frame 1: with a direction held through the logos the title accepts Start 349 "
        "frames sooner.||Found by pressing Start on every frame from 1,161"),
    (1171, "START on the first frame the title counts it.||1,169 is ignored - bisected"),
    (1175, "Holding A: each story page closes the moment the game allows it.||Nothing, Start, Select, directions: all slower"),
    (1902, "LEVEL 1: RAGNAROK'S CANYON. The clock starts when the toad lands.||speedrun.com Any% (No Credits Warp)"),
    (L1, "Headbutt each pig once (one hit kills; punches take 8), dash right, dash-jump to the ledge, into the portal.||"
         "The portal only lives 466 frames"),
    (WARP3, "MEGA WARP to LEVEL 3 - a designed shortcut, skips level 2. Start mashed through every cutscene page.||"
            "Cutscenes are on the clock: nothing 860 f, Start held 673 f, mashed 191 f"),
    (L3, "LEVEL 3: TURBO TUNNEL. Headbutt the rat, wait beside it while it's down, headbutt again as it stands.||"
         "Nothing can touch a downed rat"),
    (L3B, "Four rats, seven pits: coast to a stop before each pit, dash-jump from standing (89 px).||"
          "The pits were learned by dying in searches - the run never dies"),
    (BIKE, "Onto the speeder bike.||The world record skips this with the bike glitch - legal, not implemented yet"),
    (TUNNEL, "TURBO TUNNEL: ride the screen's left edge; walls read on sight, the last section (12 px/frame, lanes "
             "switching every 21 frames) solved by beam search.||8,290 frames from the mount"),
    (L4, "LEVEL 4: ARCTIC CAVERNS. Stop the ice ball with a punch, carry it up the slope, throw it through the wall; "
         "snowballs from the pile kill the snowmen.||Then the designed warp to level 6"),
    (L6, "LEVEL 6: KARNATH'S LAIR. Snakes are the platforms - their heads pause at corners and lift you.||"
         "The exit is three screens up: a double jump off the third snake's head"),
    (L8, "LEVEL 8: INTRUDER EXCLUDER. A 4,000-px tower: every jump peaks exactly at the next floor's edge; moving "
         "electric holes and elevators timed by beam search.||Then Robo-Manus: 21 smashes"),
    (L9, "LEVEL 9: TERRA TUBES. The start wall has no collision on top: over it and down the outside of the level.||"
         "Out of bounds is allowed in this category"),
    (L9 + 1400, "Through a spark-guarded pipe, then four giant gears (Krazy Kogs) that only start moving when they see "
                "you.||The beam follows a 1-player TAS's path, with scripted waits for each gear"),
    (L10 - 400, "The level ends while dying on the last spikes - the exit trigger counts.||Allowed: an end-of-stage trigger"),
    (L10, "LEVEL 10: RAT RACE. Out-race the rat down the shaft, kick its bomb, then the RAT BOOT: a hard hit, then a "
          "second running kick.||Allowed in Any% (No Credits Warp)"),
    (L11, "LEVEL 11: CLINGER-WINGER. The unicycle maze with the Buzzball behind. Turn at every arrow before you reach it.||"
          "The TAS pressed Up+Down here (banned) - this is our own legal controller"),
    (L11 + 5200, "The Buzzball fight: jump kicks, 16 damage each.||"),
    (L12S["L12_r1"], "LEVEL 12: THE REVOLUTION. First 857 frames: the 1-player TAS replayed frame for frame.||"
                     "Its inputs sync exactly until its first Left+Right press"),
    (L12S["L12_r2"], "Legal sprint: turn, wait for the turn to finish, double tap, jump.||The TAS used Left+Right+A; "
                     "ours costs 6 frames"),
    (L12S["L12_f0"], "Beam search following the TAS's path up the tower.||Score: progress along the path, distance from it"),
    (L12S["L12_f1k"], "KILL the Hornhead - 3 hits.||While a Hornhead lives the camera will not scroll, and the ledge above "
                      "never appears"),
    (L12S["L12_f1s"], "Back to the floor, then the TAS's own inputs through the bouncing platform.||This launch needs "
                      "frame-perfect inputs no search found"),
    (L12S["L12_g1459k"], "KILL: running kick, one hit.||Camera lock again"),
    (L12S["L12_g1640"], "RE-SYNC: a 90-frame approach puts the toad in the TAS's exact state, then its inputs launch it.||"
                        "Automatic fallback when the search stalls"),
    (L12S["L12_g1829"], "Following the TAS path.||"),
    (L12S["L12_g1920k"], "KILL the walker (0x62).||Camera lock"),
    (L12S["L12_g2000"], "Following the TAS path.||"),
    (L12S["L12_g2120k"], "KILL: this Hornhead only spawns once the camera scrolls up - so climb first, then come back.||"),
    (L12S["L12_g2230"], "Following the TAS path.||"),
    (L12S["L12_g2390k"], "KILL.||"),
    (L12S["L12_g2500"], "Following the TAS path.||"),
    (L12S["L12_g2800"], "Following the TAS path.||"),
    (L12S["L12_g3080a"], "THE BIG WALKER: 111 HP, seven hits. It waits for the random number generator.||Every button press "
                         "(even Select) changes the RNG: 73 frames of presses start it at 73 instead of 324"),
    (L12S["L12_g3080b"], "Finish it from the bouncing platform.||"),
    (L12S["L12_g3160"], "Following the TAS path.||"),
    (L12S["L12_g3290"], "Catch the circling platform (2-frame steps), bounce, re-sync.||Circling platforms spawn when the "
                        "camera reaches them - their timing depends on how you climbed"),
    (L12S["L12_g3442"], "EXACT MATCH with the TAS, then its inputs for 414 frames through the whole platform chain.||"
                        "The TAS's toad sits 168/256 of a pixel off (from its Left+Right presses); ours can't"),
    (L12S["L12_g3760"], "Following the TAS path.||"),
    (L12S["L12_g4060"], "Following the TAS path.||"),
    (L12S["L12_g4360"], "Following the TAS path.||"),
    (L12S["L12_g4500k"], "KILL.||"),
    (L12S["L12_g4610"], "SWELLCHEEKS #1: board the circling platform, bounce onto the pole, hang through the wind.||"
                        "The face locks the camera until it leaves; then drop onto the upper platform"),
    (L12S["L12_g5200k"], "KILL.||"),
    (L12S["L12_g5350"], "Stand on the TAS's exact pixel, wait for the platform's phase, double-tap sprint jump.||"
                        "This platform only launches you if you snap onto it from below. One changed input fixes the pixel"),
    (L12S["L12_g5650k"], "KILL the walker.||"),
    (L12S["L12_g5730"], "SWELLCHEEKS #2: pole at x 96, wait out the wind, drop straight onto the higher platform.||"
                        "Skips the TAS's detour"),
    (L12S["L12_g6330"], "SWELLCHEEKS #3: jump INTO the wind - it carries the toad 230 px to the pole.||Then drop, launch "
                        "back, bounce up"),
    (L12S["L12_g6930"], "The TAS's last stretch, re-synced.||"),
    (L12S["L12_gtop"], "THE TOP. The TAS scrolls the camera with Left+Right to end the level early (banned). We climb.||"
                       "Two small platforms, then the spring: hold A, the camera reaches the top, level over"),
]

CAPTIONS = [
    (1, "This is Battletoads on the NES. Every input from here to the end comes from an AI - nobody is touching the controller."),
    (420, "Same rules as the speedrun world record: Any%, no credits warp. No cheat codes, and no pressing left and right at the same time."),
    (1000, "First trick is before the game even starts: holding Right through the logos lets the title accept Start 349 frames early."),
    (1500, "We found that by trying Start on every single frame. Holding A then skips each story page the instant it's allowed."),
    (CLOCK - 60, "The speedrun clock starts the moment the toad lands. Everything from here counts."),
    (L1 + 300, "One headbutt kills a pig. Punching takes eight hits. So: headbutt, dash, jump - straight into a portal most players never find."),
    (WARP3, "That portal is a real shortcut the designers left in. It skips level 2 entirely."),
    (L3, "Turbo Tunnel - the level that ended a lot of childhoods."),
    (L3B + 200, "The AI learned every pit in this stretch by dying in thousands of practice searches. The actual run never dies."),
    (TUNNEL, "The bike. Walls come faster than you can read them. The AI hugs the left edge and a search times every jump and lane change."),
    (TUNNEL + 3000, "The world record skips this whole ride with a bike glitch. It's legal, and it's the biggest thing we still have to add."),
    (L4, "Arctic Caverns. Punch the ice ball, carry it up, throw it through the wall. Then another designed warp - to level 6."),
    (L6, "Karnath's Lair. The snakes are the floor. The way out is three screens up, off the last snake's head."),
    (L8, "Intruder Excluder. A 4,000-pixel climb where every jump tops out exactly on the next floor's edge."),
    (L8 + 3200, "Robo-Manus at the top: 21 smashes, timed so he never gets a clean hit in."),
    (L9, "Terra Tubes. The wall at the start has no collision on top, so we go over it and down the outside of the level."),
    (L9 + 1400, "The route came from a tool-assisted run. The AI follows its path - but the gears only move when they see you, so it has to wait for each one."),
    (L10 - 400, "The level ends by dying on the last spikes. The exit trigger still counts, and the rules allow it."),
    (L10, "Rat Race. Beat the rat down the shaft, kick its bomb, then the rat boot: two exact kicks that end the level early."),
    (L11, "Clinger-Winger. The reference run pressed up and down together here, which is banned. So the AI got its own controller for every corner."),
    (L12S["L12_r1"], "The Revolution. This one tower took more work than any other level. Here's why."),
    (L12S["L12_r2"], "The reference run sprints with left and right held at once. The legal way is a double tap - and you have to finish turning first."),
    (L12S["L12_f1k"], "Big discovery: while one of these horned enemies is alive, the camera won't scroll up - so the platforms above never show up."),
    (L12S["L12_f1s"], "Some platforms sink and then launch you. That needs frame-perfect timing, so here we match the reference run exactly and replay its inputs."),
    (L12S["L12_g1640"], "When the search gets stuck, a second tool lines the toad up with the reference run pixel for pixel, then hands over."),
    (L12S["L12_g2120k"], "This enemy doesn't even exist until the camera climbs past it. Climb first, then come back down to fight."),
    (L12S["L12_g3080a"], "The big one waits for the random number generator. Every button press - even Select - changes it. So the AI presses buttons until it comes."),
    (L12S["L12_g3290"], "Circling platforms start moving when the camera first reaches them. So their timing depends on exactly how you climbed."),
    (L12S["L12_g3442"], "Here's the weird one: the reference run's left-right presses left its toad a fraction of a pixel off. We can never match that exactly."),
    (L12S["L12_g3442"] + 420, "One pixel doesn't sound like much. On a platform this narrow, it's the difference between landing and falling off the tower."),
    (L12S["L12_g4610"], "The wind faces. Stand in the open and the wind blows you right off the tower. So you grab a pole and hang on."),
    (L12S["L12_g4610"] + 420, "The face also locks the camera. Only after it leaves does the next platform appear - so we wait it out, then drop."),
    (L12S["L12_g5350"], "This platform only launches you if you snap up onto it from below. We stand on the reference run's exact pixel and copy its jump."),
    (L12S["L12_g5730"], "Wind face number two. Pole, wait, drop straight onto the higher platform - skipping the reference run's detour."),
    (L12S["L12_g6330"], "Number three. This time you have to jump into the wind on purpose - it carries you 230 pixels to the pole."),
    (L12S["L12_gtop"], "The top. The reference run uses a banned left-right trick to scroll the camera and end the level early. We have to actually climb it."),
    (L12S["L12_gtop"] + 250, "Two tiny platforms, then a spring. Hold A on the spring, the camera reaches the top, and the level ends."),
]


def fmt_srt(frame):
    t = max(0.0, (frame - 1) / FPS)
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h:02d}:{m:02d}:{t % 60:06.3f}".replace(".", ",")


def build(route, l13=()):
    events, caps = list(EVENTS), list(CAPTIONS)
    ins = [l for l in (LOGS / f"{route}.inputs.txt").read_text().splitlines() if not l.startswith("#")]
    total = len(ins)
    if l13:                                   # the Dark Queen: fight sections after the level-13 load
        f = 65202
        lens = [len(json.load(open(K / f"l4s_{s}.json"))) for s in l13]
        events.append((f, "LEVEL 13: ARMAGEDDON - THE DARK QUEEN. Beam search on the hit counter.||RAM $586: +12 per hit, "
                          "240 after 20 hits; the 21st finishes her. Damage taken ranks lower"))
        caps.append((f, "Armageddon. The Dark Queen. The game keeps her hit count in one byte of memory: 12 per hit. Twenty hits fill it - and it takes one more to finish her."))
        caps.append((f + 600, "The AI searches for whatever lands the next hit without getting hit back."))
        f += 2 + lens[0]
        for s, n in zip(l13[1:], lens[1:]):
            events.append((f + 2, "Still on the Dark Queen: the last hits.||Each search starts where the previous one stopped"))
            f += 2 + n
        KILL, CUT = 66560, 67226           # the queen's object gone / the cut to T. Bird (level byte -> 254), from the trace
        events.append((KILL, "THE DARK QUEEN IS DOWN - 21st hit.||The clock stops at the cut to Professor T. Bird"))
        events.append((CUT, f"TIME: {int((CUT - CLOCK) / FPS // 60)}:{(CUT - CLOCK) / FPS % 60:06.3f}||World record: 12:29.250. "
                            "Still to add: the Turbo Tunnel skip, faster Level 4 and 12"))
        caps.append((KILL, "Twenty-one hits. The Dark Queen is done - and the toad finished the fight at full health."))
        t = (CUT - CLOCK) / FPS
        caps.append((CUT, f"That's the game. {int(t // 60)} minutes {t % 60:.1f} seconds on the speedrun clock. "
                          "The world record is 12:29 - we're not there yet."))
        caps.append((CUT + 480, "Next up: the bike skip, a faster Level 4, and a lot less waiting on that tower."))
    events.sort()
    caps.sort()
    (LOGS / f"{route}.events.txt").write_text("\n".join(f"{f}\t{t}" for f, t in events) + "\n")
    rows = []
    for i, (f, t) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else total
        end = min(nxt - 6, f + 480, total)
        rows.append((f, max(end, f + 120), t))
    (LOGS / f"{route}.captions.txt").write_text("\n".join(f"{a}\t{b}\t{t}" for a, b, t in rows) + "\n")
    srt = []
    for i, (a, b, t) in enumerate(rows, 1):
        srt += [str(i), f"{fmt_srt(a)} --> {fmt_srt(b)}", t, ""]
    VIDEO.mkdir(exist_ok=True)
    (VIDEO / f"{route}.srt").write_text("\n".join(srt), encoding="utf-8")
    md = [f"# Battletoads AI run - narration script ({route})", "",
          "Timestamps are video time (power-on = 0:00). Captions are burned into the video and also in the .srt.", ""]
    for a, b, t in rows:
        s = (a - 1) / FPS
        md.append(f"**{int(s // 60)}:{s % 60:04.1f}**  {t}")
        md.append("")
    (VIDEO / f"{route}_script.md").write_text("\n".join(md), encoding="utf-8")
    keys = [(1, 2088250, 6.03, "first boot"), (2810, 107632706, 65.42, "Level 1 solved"),
            (6304, 141916836, 78.87, "Turbo Tunnel: to the bike"), (14594, 229930079, 117.82, "Turbo Tunnel done"),
            (27054, 575613634, 258.95, "Level 4 done"), (29704, 713968363, 316.06, "Level 6 done"),
            (34816, 741860904, 338.06, "Level 8 done"), (44999, 931448178, 415.71, "Terra Tubes done"),
            (47296, 972054418, 425.88, "Rat Race done"), (54702, 992711792, 430.96, "Clinger-Winger done"),
            (56798, 1075965334, 454.91, "Revolution: the camera locks"),
            (64697, 1281608570, 534.76, "Revolution: three wind faces"), (65201, 1331570496, 552.34, "The Revolution done")]
    if l13:
        sys.path.insert(0, str(HERE))
        from toads import tokens
        t = tokens.totals()
        keys.append((total, t["total"], t["cost"], "The Dark Queen"))
    (LOGS / f"{route}.tokens.json").write_text(json.dumps([{"frame": f, "tokens": n, "cost": c, "label": l}
                                                           for f, n, c, l in keys]))
    print(f"{len(events)} panel entries, {len(rows)} captions, {len(keys)} token keyframes; {total} frames")


if __name__ == "__main__":
    build(sys.argv[1], tuple(sys.argv[2:]))

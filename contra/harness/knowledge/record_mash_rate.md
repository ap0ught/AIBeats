# Contra (NES) No Turbo record: how fast and how long he mashes B

Run: Angrylanks, 9:48.183, https://www.youtube.com/watch?v=YgtFCclM1jM. Measured 2026-10-12 in the built-in browser from the 720p60 stream. Raw numbers are in `record_mash_rate.json`. Times are video seconds; the run is 12.000 to 600.183 (588.18 s, 35,291 frames).

## Headline

- **He has two mashing speeds and a slow tap, not one rate.** A fast mash at about 12.1 presses a second (bosses, base cores, tanks), a relaxed mash at about 8.5 a second (most base rooms, the Waterfall boss, Alien's Lair), and single shots about every 24 frames (2.5 a second) while running.
- **Burst: 13 presses in 60 frames, at 33 separate places. Never 14.**
- **Sustained, as measured:** 38 presses in 180 frames, 119 in 600 frames, 270 in 1,800 frames. These are lower bounds.
- **His longest unbroken stretch at 11 or more a second is about 10 seconds** (the heart). The Base 2 boss is a 13-second train averaging 11.7 a second with three dips.
- **At least 66 of the 588 one-second bins hold 11 or more presses (11%).** The AI run has 198 of 574 (34%) and one 43.7-second stretch. Nothing in the record looks like that.
- The handcam cannot show the 12-a-second mash. It delivers about 15 distinct images a second. The usable signal turned out to be the **button clicks on his microphone**.

## 1. What each signal can and cannot show

### Handcam: 15 images a second, not 30 or 60

- Measured over frames 600 to 9958 (sampled every second frame) and 3600 to 3929 (every frame).
- The hand picture changes every 4 video frames in 833 of 1,326 measured gaps, every 2 in 201, every 6 in 172. The most new images in any 2 seconds is 31 (15.5 a second).
- So the handcam's limit is 7.5 Hz. A 12 Hz press train can only appear as an alias at 3 Hz, mirrored at 12 Hz when the 60 fps video is analysed. That mirror is why the earlier note found "weak peaks at 11.5-13.5 Hz". Those peaks do not measure the rate; a 3 Hz hand movement would produce the same peaks.
- What the handcam does show: a clear 8.75 Hz peak (with its alias at 6.25 Hz) in six 2-second windows at the start of Base 1 rooms 1, 3 and 5. The audio gives 8.8 to 9.2 presses a second in the same windows.
- During 12 Hz trains the handcam shows nothing above noise. The thumb moves less than a pixel and the exposure blurs it.

### Microphone clicks: the main measurement

- The video's sound has short broadband ticks at 2.8 to 8.8 kHz. They are the controller's buttons, heard through his microphone.
- Why they are not game sound: game sound can only start on a console frame, so gaps would be about 40 or 50 samples at 600 Hz. The measured gaps are 47, 49, 47, 49, 50, 49, 48, 47.
- Why they are B presses: where bullets can be seen one by one, every bullet lines up with a click, and gaps in the bullets still have clicks (see section 3).
- Each press makes a press click and a weaker release click. In the relaxed mash the two are evenly spaced, so the click rate reads double (16 to 18 a second). I count those trains at half rate. The bullets in the Hangar and the handcam in Base 1 both confirm the half rate.
- How I got the sound: a Web Audio tap on the page's video element while it played once in real time. Nothing went to the speakers and nothing was saved outside the page. 0.22% of samples were lost in capture, so rates could read up to 0.25% high.
- A "train" is at least 4 clicks at steady 55 to 135 ms spacing. Up to 2 missing clicks in a row are bridged. Of 2,168 presses counted, 273 are bridged, not heard.

**Limits of the audio, measured:**
- **It misses soft presses.** In the Snow Field at frames 21715 to 21925 the picture shows him still mashing at about 12 a second, and the audio has only 8 weak clicks. Over the 47-second flat section of that stage the audio found roughly 35 to 60% of the dense mashing the picture shows.
- It cannot tell a single B tap from a jump press, so single taps are left out of the trains. There are 646 strong isolated clicks in the run; that is the most the single taps could add.
- So every total, fraction and sustained figure below is a **lower bound**. The burst and 3-second figures come from the loudest, cleanest trains and are firm.

### Game picture

- Used as the check, on stretches where centre-line Spread bullets fly across a dark background.
- Bullets undercount presses. With Spread, a press with no free bullet slot fires nothing, and when he fires into open space about one press in five is swallowed.
- Not usable at bosses (point-blank), in the base rooms, or on bright backgrounds.

## 2. The numbers

All from the audio trains unless stated. "Range" is the spread across five detector settings (stricter thresholds, no bridging and so on).

### Highest rate reached

| Window | Presses | Where | Range | Notes |
|---|---|---|---|---|
| 60 frames (1 s) | **13** | 33 separate places | 13 in every setting | Fastest 13 presses span 56.5 frames. 14 presses never fit in 60 frames (best 61.3). |
| 180 frames (3 s) | **38** | Base 2 boss, 265 s | 37 to 38 | 37 at four more places (531, 554, 589, 594 s). |
| 600 frames (10 s) | **119** | Heart, 588 s | 109 to 120 | 118 at the Base 2 boss. 109 if only clicks actually heard are counted. Then 108 (Base 1 room 1), 101 (Hangar). |
| 1,800 frames (30 s) | **270** | Alien's Lair into the heart, 569 s | 246 to 271 | Next best 228 (Base 2), 207 (Base 1), 200 (Hangar). Lower bound. |

Press spacing inside the fast mash: median 4.96 frames, middle half 4.76 to 5.20, 5% shorter than 4.43. So he often presses 4 frames apart. A rule of "at least 5 frames between presses" is stricter than his own play.

### How much of the run

| Measure | Value | Kind |
|---|---|---|
| Seconds inside a mash train | 205.9 of 588 (35%) | lower bound |
| Fast mash (train median 10.5 a second or more) | 120.2 s, 1,365 presses | lower bound |
| Relaxed mash | 85.7 s, 790 presses | lower bound |
| One-second bins with any train press | 287 (49%) | lower bound |
| One-second bins with 5 or more | 217 (37%) | lower bound |
| One-second bins with 11 or more | **66 (11%)**, range 45 to 68 | lower bound |
| One-second bins with 12 or more / with 13 | 48 / 8 | lower bound |
| Longest unbroken stretch at 11 or more a second | **9.9 s** (heart, from 588.3 s) | lower bound |
| Longest at 12 or more a second | 7.2 s (Base 2 boss) | lower bound |

Inferred, not measured: if the audio finds 60 to 80% of his fast mashing over the whole run, the true count of seconds at 11 or more would be about 85 to 110 (15 to 19%). The one section where I could check found less than that (35 to 60%), so the true figure could be higher still. I cannot pin it down.

### Average presses per second by stage

Stage = medals appearing to the next stage's medals.

| Stage | Seconds | Train presses | Per second | With isolated clicks | Seconds at 11+ |
|---|---|---|---|---|---|
| 1 Jungle | 65.0 | 158 | 2.43 | 3.55 | 1 |
| 2 Base 1 | 61.8 | 312 | 5.05 | 5.98 | 12 |
| 3 Waterfall | 65.5 | 142 | 2.17 | 3.53 | 3 |
| 4 Base 2 | 95.9 | 479 | 5.00 | 5.86 | 14 |
| 5 Snow Field | 101.9 | 254 | 2.49 | 4.09 | 7 |
| 6 Energy Zone | 68.9 | 176 | 2.55 | 3.73 | 7 |
| 7 Hangar | 74.7 | 288 | 3.86 | 4.73 | 13 |
| 8 Alien's Lair | 54.5 | 359 | 6.59 | 7.22 | 14 |
| Whole run | 588.2 | 2,168 | **3.69** | 4.78 | 66 |

The stage rows add up to 71 seconds at 11+ because each stage's one-second bins start at its own first frame; counted from the run start it is 66.

"Per second" is the lower bound. "With isolated clicks" adds every strong single click, jumps included, so it is too high for B alone. His true average sits between the two, or above if many presses were too soft to hear.

In stage 1 he holds the Machine Gun from 17.2 to 26.6 s. It fires by itself and there are no clicks at all in that time.

### Steady or bursts

Bursts with rests.

- 85 trains. The median gap between trains is 2.8 seconds.
- Base 1: one train per room (9.2, 4.5, 3.3, 4.7 s), silence for the walk between rooms, then 4.6 s on the boss.
- Base 2: the same pattern. Rooms 3 and 4 are one 14.7 s train at the relaxed 8.6 a second. The boss is 13.1 s at 12.2.
- Rooms usually start relaxed (about 8.7 a second) and switch to the fast mash for the cores.
- Outdoor stages: mostly single taps while running, with fast bursts of 2 to 6 seconds at tanks, turrets and bosses.
- The only long continuous pressing is Alien's Lair into the heart: 28 seconds at 7 or more a second, of which the last 10 are the fast mash.

## 3. How the two methods agree

| # | Stage, frames | Picture | Audio | Result |
|---|---|---|---|---|
| 1 | 5, 23236-23357, firing up | 22 bullets, 4.1 to 5.9 frames apart, three gaps of 9 to 14 | click slot every 4.9 frames; the bullet gaps have clicks | agree, audio has more presses than bullets |
| 2 | 7, 30140-30300, running | 17 bullets, about 7.7 a second | one strong click per bullet | agree, relaxed mash is 8 a second, not 16 |
| 3 | 5, 20900-21100, running | one bullet every 23 to 24 frames | isolated clicks every 21 to 29 frames | agree, single taps |
| 4 | 5, 21547-21715, running | rhythm 5.1 frames | 34 presses at 12.2 a second | agree |
| 5 | 5, 21715-21925, running | still about 12 a second | 8 weak clicks, no train | **audio misses it** |
| 6 | 6, 27450-27535, running | bullets 4.3 to 4.9 frames apart | presses every 5 frames | agree |
| 7 | 5, 22439-22582, running | one bullet every 22 to 26 frames | no train | agree, single taps |
| 8 | 5, 20400-23250, per second | dense mash about 12 s, taps about 20 s | trains cover about 5 s of the 12 | audio finds 35 to 60% |
| 9 | 3, 10790-10830, running | streaks 7.5 to 10 frames apart (rough) | presses every 7 frames | consistent, weak |
| 10 | 1, 2520-2720, running | not countable | 41 presses at 8.7 a second | no check |
| 11 | 2, three room starts (handcam) | 8.75 Hz peak | 8.8 to 9.2 a second | agree |

Where both can see, the rates match to within about half a press a second and the audio never showed presses the picture contradicts. The disagreement is one-sided: the audio goes quiet while he is still mashing.

## 4. What could not be resolved

- How many soft presses the microphone missed over the whole run. Checked in one 47-second section only.
- The base rooms, both base bosses, the wall bosses and the heart rest on audio alone. Bullets vanish at point-blank range, and these are exactly where the long fast trains are.
- Single B taps against jump presses.
- Whether the three dips in the Base 2 boss train are real pauses or unheard clicks.
- I did not finish a handcam pass of the whole run. I stopped it at 166 s once it was clear the camera delivers 15 images a second.

## 5. Recommendation

This part is judgement, not measurement.

Use four limits together. Each is a figure he reaches himself.

| Limit | Value | Cautious value | Evidence |
|---|---|---|---|
| Presses in any 60 frames | **13** | 12 | 13 at 33 places, never 14 |
| Presses in any 180 frames | **37** | 37 | 38 once, 37 four more times; 37 on heard clicks only |
| Presses in any 600 frames | **118** | 109 | 119 and 118 at two separate bosses; 109 on heard clicks only |
| Presses in any 1,800 frames | **270** | 246 | one window; next best 228 |

- **The burst rule is not the problem.** The current "one press every 5 frames" gives 12 in 60 frames, which is inside his 13. He also presses 4 frames apart about one time in twenty.
- **The 30-second limit is the one that answers the reviewer.** 270 in 1,800 frames is 9 a second on average. A 43.7-second stretch at 12 a second is 524 presses and breaks it by a wide margin. The 600-frame limit alone would not stop that stretch (it allows 11.8 a second for ever), so the 1,800-frame limit is needed.
- **The 270 is the weakest number here.** It comes from one stretch of the run and is a lower bound, because the audio misses soft presses. The evidence does not support a higher figure, and it does not rule one out. If the limit is to be defended in public, 246 is the figure every detector setting agrees he reaches.
- **Consider a pattern rule as well.** His fast mash comes in trains of 2 to 13 seconds separated by rests or by the relaxed 8.5 a second. A run that mirrors that shape (fast only at bosses, cores and tanks) is easier to defend than one that merely stays under a count.
- A whole-run comparison worth publishing beside the limits: he has at least 66 seconds at 11 or more presses, and averages at least 3.7 presses a second over the run.

# Ninja Gaiden record: press rate (turbo question)

Status, 2026-10-19: **the record's video cannot measure his press rate.** Below: why, what the TAS does, and the cap I propose.

## Why the record video gives no press data

1. **No handcam.** The webcam (lower left) shows the runner's face and upper body, not the controller.
2. **Microphone clicks are not usable.** I checked the audio band energies (100 Hz to 16 kHz, 5 ms steps) across the Jaquio fight, video frames 41300-42074, where the hardest mashing in the run happens.
   - The game sound is very quiet in the stream mix: before the fight starts the band energies sit near the noise floor.
   - The loud events are the runner's voice; he shouts at the kill, from 41762.
   - There is no regular click train like the one Contra's record had.
   - This was a short check, not a full scan of the run.
3. **The picture can only give a lower bound.** The video has 30 images a second, each a single NES frame (the other half of the frames are missing). The sword sprite is small at this resolution, so counting slashes this way would only bound the rate from below, and the bound would be well under the real rate. I did not attempt it.

## Community knowledge

- The board bans turbo but gives no number.
- The game's resources include **MashyMashy** (speedrun.com resources `qujir` and `24bvi`, by mitch3a). It is a mash-speed tester that has a "B with down" mode built "to simulate Ninja Gaiden Jaquio mashing". This tells us fast Down+B mashing (slash canceling) at the final bosses is a recognised skill in the community.
- I found no published figure for the presses per second that top players reach.
- A 2021 article on a damageless run says the runner turned the controller sideways to mash fast enough for seven hits in a few seconds. https://articles.retroware.com/2021/02/04/streamer-completes-world-first-100-damageless-run-of-ninja-gaiden/
- Generic NES speedrunning experience, and our own Contra measurement, put elite manual mashing at about 12-13 presses a second in bursts. Angrylanks's microphone clicks gave a best of 13 presses in 60 frames and never 14 (`G:\AI World Record\Contra\knowledge\record_mash_rate.md`).

## What the TAS does (and why we cannot copy it)

From the input log of TASVideos 4751M (39,084 frames):

| Button | Presses | Most in 60 frames | Most in 600 frames | Presses only 2 frames after the previous one |
|---|---|---|---|---|
| B | 1,022 | 25 | 152 | 551 |
| A | 1,496 | 30 | 164 | 628 |
| Up | 2,245 | 30 | 256 | 1,939 |
| Down | 1,943 | 30 | 256 | 1,602 |
| Left | 657 | 16 | 81 | 117 |
| Right | 725 | 25 | 76 | 146 |

- The TAS slash-cancels at **one press every 2 frames (30 a second)**. Its submission notes say the cancel "lets you attack with the sword as often as Down+B can be pressed and released—which is every two frames in a TAS".
- Most of its Up/Down presses come from the banned **Up+Down+Left** wall trick: 1,778 Up+Down events and 3,430 Up+Down frames. It also has 131 Left+Right events (1,221 frames).

## Proposed human press cap (draft; the coordinator decides)

The same as the Contra project's v1 rule. It is the conservative end of what elite NES players reach, and is not above what this record's runner could plausibly do.

- **A new press of the same button at most once every 5 frames, i.e. 12 per second.** Each press is held at least 2 frames and released at least 2 frames.
- **Sustained limits, borrowed from the Contra measurement:**
  - at most 109 new presses of one button in any 600 frames;
  - at most 246 in any 1,800 frames.
  - Ninja Gaiden needs fast mashing only at bosses (Jaquio and the demon above all), so this should cost little.
- **Never Left+Right, never Up+Down on the same frame.** Board rule plus the linked general rules.
- **Down+B is pressed with two fingers, not mapped to one button.** Mapping two inputs to one key is banned. In input terms that is free, but each button's own press counts against its own cap.
- **Where the cap bites:**
  - slash canceling at Jaquio (6-4b) and the demon (6-5);
  - the sword-based boss fights;
  - frame-tight wall climbs that alternate A presses, where wall climbing needs repeated jump presses.
- **A wall climb needs A pressed again for every wall jump.** The game's climbing pattern (TASVideos) is a wall jump that rises 15 px and peaks after 10-14 frames. A press every 5+ frames fits easily.

If the owner wants a measured cap instead, someone needs a different video of a top runner with a handcam, or with clean controller audio. One option is to search the other top-10 runs' videos (`research.md` section 2) for a handcam. Arcus's and blacksquall's runs are on YouTube/Twitch.

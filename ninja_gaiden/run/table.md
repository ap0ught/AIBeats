# Stage by stage, against the record (same on-screen event on both sides)

Event: the first frame whose picture shows the HUD TIMER digits of a stage. Segment = from one stage's event to the
next stage's (1-1 starts at Ryu first visible, frame 175; 6-5 ends at TIMER-000 first visible, frame 41,385).
Frames are NES frames. The record's numbers are its video frames x 60.0988/60, measured by the independent checker
(`verification/independent_check/record_stage_events.json`; all 22 agree with the project's `record_events.json`),
+/- 2 frames each. The HUD redraws its digits on a 6-frame cycle, so a single stage can move by up to +/- 5 frames
depending on the redraw phase; the cumulative numbers do not drift.

Source: `verification/independent_check/final/final_check.txt` (the independent check of the final file).

| stage | ours (frames) | record (frames) | ours - record | ahead at the stage's end |
|---|---|---|---|---|
| 1-1 | 2,302 | 2,313.8 | -11.8 | +11.8 |
| 1-2 | 834 | 841.4 | -7.4 | +19.2 |
| 2-1 | 2,820 | 2,904.8 | -84.8 | +104.0 |
| 2-2 | 3,042 | 3,101.1 | -59.1 | +163.1 |
| 2-3 | 821 | 833.4 | -12.4 | +175.4 |
| 3-1 | 1,604 | 1,602.6 | +1.4 | +174.1 |
| 3-2 | 2,336 | 2,327.8 | +8.2 | +165.9 |
| 3-3 | 917 | 911.5 | +5.5 | +160.4 |
| 4-1 | 2,150 | 2,191.6 | -41.6 | +202.0 |
| 4-2 | 2,298 | 2,303.8 | -5.8 | +207.8 |
| 4-3 | 2,564 | 2,557.2 | +6.8 | +201.0 |
| 4-4 | 767 | 785.3 | -18.3 | +219.3 |
| 5-1 | 2,374 | 2,460.0 | -86.0 | +305.3 |
| 5-2 | 2,362 | 2,458.0 | -96.0 | +401.4 |
| 5-3 | 2,891 | 2,984.9 | -93.9 | +495.3 |
| 5-4 | 805 | 805.3 | -0.3 | +495.6 |
| 6-1 | 1,574 | 1,584.6 | -10.6 | +506.2 |
| 6-2 | 3,170 | 3,153.2 | +16.8 | +489.4 |
| 6-3 | 3,003 | 2,912.8 | +90.2 | +399.2 |
| 6-4a | 821 | 819.3 | +1.7 | +397.5 |
| 6-4b | 1,011 | 997.6 | +13.4 | +384.2 |
| 6-5 | 744 | 749.2 | -5.2 | +389.4 |
| **total** | **41,210 = 11:25.704** | 41,599.4 = 11:32.183 | **-389.4 = -6.479 s** | |

The project's own ledger (`harness/knowledge/LOCKED_CHAIN.md`, "Locked stages") times each stage from RAM control
frame to the next stage's control frame against the record's estimated control frames. Its per-stage numbers differ
from this table by up to 5 frames for the reason above, and it ends at the same -389.4 frames.

Our stage loads and control frames (RAM), from the builders' two-replay report `NG_FINAL_v2.report.json`:

    1-1   load None  control 174  control_to_next_control 2300
    1-2   load 2322  control 2474  boss0 2560  control_to_next_control 834
    2-1   load 3156  control 3308  control_to_next_control 2822
    2-2   load 5978  control 6130  control_to_next_control 3037
    2-3   load 9015  control 9167  boss0 9247  control_to_next_control 826
    3-1   load 9841  control 9993  control_to_next_control 1602
    3-2   load 11443  control 11595  control_to_next_control 2335
    3-3   load 13778  control 13930  boss0 14100  control_to_next_control 918
    4-1   load 14696  control 14848  control_to_next_control 2150
    4-2   load 16846  control 16998  control_to_next_control 2299
    4-3   load 19145  control 19297  control_to_next_control 2561
    4-4   load 21706  control 21858  boss0 21880  control_to_next_control 771
    5-1   load 22477  control 22629  control_to_next_control 2369
    5-2   load 24846  control 24998  control_to_next_control 2363
    5-3   load 27209  control 27361  control_to_next_control 2891
    5-4   load 30100  control 30252  boss0 30306  control_to_next_control 805
    6-1   load 30905  control 31057  control_to_next_control 1576
    6-2   load 32481  control 32633  control_to_next_control 3167
    6-3   load 35648  control 35800  control_to_next_control 3005
    6-4a  load 38653  control 38805  boss0 38879  control_to_next_control 820
    6-4b  load 39473  control 39625  boss0 39878  control_to_next_control 1014
    6-5   load 40487  control 40639  boss0 40947

"""Record's stage 7 camera timeline (measured from the video) against one of our runs.

    python tools/s7_record_compare.py <our run name in logs/s7 (needs <name>.trace.json)> [step_px]

REC8[i] = video frame, counted from the stage's first medal frame (28262), at which the record's camera (left edge
of the screen, world x) first reached 8*i px. Measured 2026-10-12 by tracking the background's horizontal shift
between consecutive video frames (one field of the woven image, 49 rows x 256 columns, sum of absolute
differences over shifts -1..6 px); the sum of the shifts reached 3,583 at the boss (true value 3,584), so the
tracking lost 1 px in 3,584. NES frames = video frames x 60.0988 / 60.
Writes knowledge/s7_record_landmarks.json and prints the section table.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REC8 = [-12,90,98,106,113,123,131,138,146,154,163,173,181,188,196,204,211,221,229,236,244,252,259,269,277,284,292,300,307,315,325,332,340,348,355,363,373,380,388,396,403,413,422,430,438,446,453,461,470,478,486,494,501,509,518,526,534,542,549,557,565,574,580,584,590,593,601,609,618,626,634,641,651,659,668,676,684,691,699,707,714,724,732,741,749,757,764,774,782,789,797,805,812,822,830,839,847,854,862,872,893,901,908,918,926,933,941,949,956,964,974,981,989,997,1004,1012,1022,1029,1037,1045,1052,1060,1070,1077,1085,1093,1100,1108,1116,1125,1133,1141,1148,1156,1164,1173,1181,1189,1196,1204,1212,1221,1250,1258,1265,1275,1283,1290,1298,1306,1313,1323,1331,1338,1346,1354,1361,1371,1379,1386,1394,1402,1406,1411,1419,1429,1432,1438,1446,1454,1461,1471,1478,1486,1494,1502,1509,1519,1526,1534,1561,1571,1578,1586,1596,1603,1611,1621,1628,1636,1644,1651,1659,1669,1676,1684,1692,1699,1707,1715,1724,1732,1740,1749,1757,1765,1774,1782,1790,1797,1805,1813,1818,1822,1826,1832,1836,1841,1849,1859,1868,1876,1884,1891,1899,1907,1914,1924,1932,1939,1947,1955,1962,1972,1980,1987,1995,2003,2010,2020,2028,2035,2043,2051,2058,2068,2076,2083,2091,2099,2106,2114,2124,2131,2139,2147,2154,2162,2172,2179,2187,2195,2202,2210,2220,2227,2235,2243,2250,2258,2268,2275,2283,2293,2300,2308,2318,2325,2333,2341,2348,2352,2356,2360,2367,2371,2377,2385,2394,2402,2410,2419,2427,2435,2442,2450,2458,2467,2475,2483,2490,2498,2506,2513,2523,2531,2538,2546,2554,2561,2571,2579,2586,2594,2604,2611,2621,2629,2636,2644,2652,2659,2678,2686,2694,2702,2709,2719,2726,2734,2742,2750,2757,2769,2776,2784,2792,2799,2807,2817,2824,2832,2840,2847,2855,2863,2872,2880,2888,2895,2903,2911,2920,2928,2936,2943,2951,2959,2968,2986,2993,3001,3009,3018,3026,3051,3059,3068,3076,3084,3091,3099,3107,3116,3124,3132,3139,3147,3155,3162,3172,3180,3187,3195,3203,3210,3233,3241,3249,3256,3266,3274,3281,3289,3297,3304,3312,3322,3329,3337,3347,3354,3362,3372,3379,3387,3395,3402,3410,3420,3427,3435,3443,3450,3458,3470,3477,3485,3493,3500,3508,3518,3525,3533,3541,3548,3556,3566,3573,3581,3589,3596,3604,3612,3623,3631,3638,3646,3654,3662,3671,3679,3686,3694,3702,3710,3719,3727]
K = 60.0988 / 60.0
REC_EVENTS_VIDEO = {"medals_first": 0, "camera_reaches_3583_scroll_over": 3733, "door_core_first_explosion": 3788,
                    "control_lost": 3984, "first_black": 4226, "stage8_medals_first": 4481}
# what the record does at each stop (looked at in the video; offsets are video frames from the medals)
REC_STALLS = [
    {"video_from": 872, "frames": 13, "cam": 792, "what": "two rising walls on the step: he is already past both "
     "(in the air at x 895, y 81 at video 846: the second jump, from the top of wall 1), shoots a soldier on the "
     "ledge, lands on the step at x 920 and is held by the ledge's side wall while his third jump rises"},
    {"video_from": 1223, "frames": 21, "cam": 1129, "what": "stands on the lower floor (x 1257) waiting for the claw "
     "at 1270; the rolling cart is shot (explosion ahead of him at 1232)"},
    {"video_from": 1536, "frames": 19, "cam": 1433, "what": "B GRAB: on the cart 1424 from video 1404 (boarded by a "
     "late jump), jumps from it at about 1438 to the small ledge (y 144, x 1504), jumps again at about 1492 over "
     "the pill box (x 1552, y 96) and shoots it from above (it explodes at about 1530), lands on the pill box's "
     "own ledge (x 1561), flashing = Barrier by about 1550, and drops THROUGH that ledge (Down+A: the game holds "
     "Bill's X for 17 frames - that is the stop)"},
    {"video_from": 2659, "frames": 14, "cam": 2568, "what": "trio of rising walls: stands at x 2696 next to wall 1 "
     "firing; wall 1 blows up at 2662, he jumps, walls 2 and 3 blow up at about 2698 and 2710 (shot from the air). "
     "By the code's timer his Barrier ends at about video 2700; whether wall 1 died by touch or by bullets was not "
     "resolved"},
    {"video_from": 2974, "frames": 12, "cam": 2871, "what": "waits for the 8-segment claws at 3014.."},
    {"video_from": 3032, "frames": 19, "cam": 2918, "what": "waits again between the claws (3046)"},
    {"video_from": 3216, "frames": 14, "cam": 3083, "what": "ducks a gunner's shot under the low roof (prone at 3224)"},
]
REC_NOTES = {
    "route": "lower route on screen 1 (under the five claws), cart 624, rising walls by wall-top jumps, ledge with "
             "the three tall walls (shot while walking), lower floor under the claws 1270..1398, cart 1424, B grab, "
             "floor, step 1632, ledge 1696, cart 1824, floor, pit 2320 onto the cart 2376, Heartbreak Alley on the "
             "LOWER floor WITHOUT STOPPING (Barrier: invincible), trio shot down, six claws with two waits, gunners "
             "(one duck), boss.",
    "alley": "camera 2304 -> 2560 in 258 video frames: no stop at all. He is on the lower floor under the seeking "
             "claws (seen at video 2420).",
    "carts": "camera px gained against 1 px/frame: cart 624 about 11, cart 1424 about 13, cart 1824 about 14, cart "
             "2376 about 18.",
    "boss": "reveal scroll starts (camera 3488) at video 3638, ends 3733; he is in the air firing forward at 3650, "
            "3690 and 3720 (jump shots at the core's height during the scroll), on the ground at about x 140 at "
            "3745 and walks to the right cap aiming up-forward (x 160 at 3765, 173 at 3784); first explosion 3788 "
            "= 150 video frames after the scroll starts, 55 after it ends, about 94 after the door is created (56 "
            "frames into the scroll).",
    "pauses": "none seen: every stop of 7+ video frames is one of the stops listed.",
}


def rec_at(cam):
    """Record's NES frame (from the medals) at which its camera first reached `cam` (linear between 8-px marks)."""
    i = cam // 8
    if i + 1 >= len(REC8):
        return REC8[-1] * K
    a, b = REC8[i], REC8[i + 1]
    return (a + (b - a) * (cam - 8 * i) / 8.0) * K


def ours_first(trace):
    first = {}
    nxt = 0
    for i, r in enumerate(trace):
        if r[13] != 4:
            continue
        while r[0] >= nxt:
            first[nxt] = i
            nxt += 8
    return first


SECTIONS = [(0, "start (Bill drops in; the camera starts when he reaches x 128)"),
            (128, "screen 1, lower floor under five claws"), (352, "step 480, cart 624"),
            (512, "floor, claws 742/758, step 800"), (688, "two rising walls, ledge 928"),
            (832, "three tall walls"), (1088, "ledge end 1216, lower floor, claws 1270..1398"),
            (1280, "cart 1424, B pill box 1552"), (1456, "floor / step 1632 / ledge 1696"),
            (1664, "cart 1824, hanging walls"), (2048, "floor to the pit 2320"),
            (2192, "pit, cart 2376"), (2272, "Heartbreak Alley 2406..2566"),
            (2448, "step 2592, ledge 2656"), (2528, "trio of rising walls 2708..2772"),
            (2688, "floor, six claws 3014..3094"), (2976, "rising wall 3124, low roof, gunners 3296/3344"),
            (3232, "last step 3360, gunners 3480/3566"), (3488, "reveal scroll (96 px)"), (3584, None)]


def table_for(name):
    tr = json.loads((ROOT / "logs" / "s7" / f"{name}.trace.json").read_text())
    first = ours_first(tr)
    kill = next((i for i, r in enumerate(tr) if r[12]), None)
    rows = []
    for (c, label), (c2, _) in zip(SECTIONS[:-1], SECTIONS[1:]):
        ra, rb = rec_at(c), rec_at(c2)
        oa, ob = first.get(c), first.get(c2)
        if c2 >= 3584:
            ob = next((i for i, r in enumerate(tr) if r[0] >= 3583), None)
            rb = REC_EVENTS_VIDEO["camera_reaches_3583_scroll_over"] * K
        if c == 0:
            ra = 0.0
        rows.append({"cam_from": c, "cam_to": c2, "what": label, "record_nes_frame_at_end": round(rb, 1),
                     "ours_row_at_end": ob, "ours_minus_record_at_end": None if ob is None else round(ob - rb, 1),
                     "record_frames_in_section": round(rb - ra, 1),
                     "ours_frames_in_section": None if (ob is None or oa is None) else ob - oa,
                     "ours_minus_record_in_section": None if (ob is None or oa is None) else round((ob - oa) - (rb - ra), 1)})
    return {"run": name, "sections": rows, "door_hp0_row": kill, "segment": len(tr),
            "lag": sum(r[4] for r in tr), "pause_rows": sum(1 for r in tr if r[5])}


def main():
    names = sys.argv[1:] or ["ph90"]
    tabs = [table_for(n) for n in names]
    rk = REC_EVENTS_VIDEO["door_core_first_explosion"] * K
    rend = REC_EVENTS_VIDEO["stage8_medals_first"] * K
    hdr = "| camera px | section | record: frames in it / at its end | " + " | ".join(
        f"{t['run']}: in it / at its end (vs record)" for t in tabs) + " |"
    lines = [hdr, "|---|---|---|" + "---|" * len(tabs)]
    for i, (c, label) in enumerate(SECTIONS[:-1]):
        r0 = tabs[0]["sections"][i]
        cell = f"| {r0['cam_from']}-{r0['cam_to']} | {label} | {r0['record_frames_in_section']:.0f} / {r0['record_nes_frame_at_end']:.0f} |"
        for t in tabs:
            r = t["sections"][i]
            cell += (f" {r['ours_frames_in_section']} / {r['ours_row_at_end']} "
                     f"({r['ours_minus_record_at_end']:+.0f}) |")
        lines.append(cell)
    cell = f"| - | door core HP 0 (record: first explosion) | - / {rk:.0f} |"
    for t in tabs:
        cell += f" - / {t['door_hp0_row']} ({t['door_hp0_row'] - rk:+.0f}) |"
    lines.append(cell)
    cell = f"| - | stage 8 first frame = the segment | {rend - rk:.0f} / {rend:.0f} |"
    for t in tabs:
        cell += f" {t['segment'] - t['door_hp0_row']} / {t['segment']} ({t['segment'] - rend:+.0f}) |"
    lines.append(cell)
    table_md = "\n".join(lines)
    print(table_md)
    out = {
        "_about": "Record (Angrylanks 9:48.183, youtube YgtFCclM1jM) stage 7, measured from the video on 2026-10-12. "
                  "Video frame offsets are counted from the stage's first medal frame (video frame 28262). "
                  "NES frames = video x 60.0988/60. Camera = world x of the left screen edge (Bill is at camera + "
                  "128 while he runs). Made by tools/s7_record_compare.py.",
        "method": __doc__,
        "video_frame_of_medals": 28262,
        "record_events_video_offset": REC_EVENTS_VIDEO,
        "record_events_nes": {k: round(v * K, 1) for k, v in REC_EVENTS_VIDEO.items()},
        "record_camera_first_reached_every_8px_video_offset": REC8,
        "record_camera_every_128px_nes": {str(c): round(rec_at(c), 1) for c in range(0, 3584, 128)},
        "record_stops": REC_STALLS,
        "record_notes": REC_NOTES,
        "compared_runs": tabs,
    }
    p = ROOT / "knowledge" / "s7_record_landmarks.json"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(out, indent=1), encoding="utf-8")
    tmp.replace(p)
    (ROOT / "logs" / "s7" / "record_compare_table.md").write_text(table_md + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

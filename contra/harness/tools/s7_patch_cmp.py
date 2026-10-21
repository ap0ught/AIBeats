"""Rewrite the text blocks and main() of tools/s7_record_compare.py (keeps the measured REC8 list)."""
from pathlib import Path

p = Path(r"tools\s7_record_compare.py")
s = p.read_text(encoding="utf-8")
a = s.index("# what the record does at each stop")
b = s.index("def rec_at(cam):")
new_text = '''# what the record does at each stop (looked at in the video; offsets are video frames from the medals)
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


'''
s = s[:a] + new_text + s[b:]
a = s.index("def main():")
new_main = '''def table_for(name):
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
    table_md = "\\n".join(lines)
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
    (ROOT / "logs" / "s7" / "record_compare_table.md").write_text(table_md + "\\n", encoding="utf-8")


if __name__ == "__main__":
    main()
'''
s = s[:a] + new_main
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")

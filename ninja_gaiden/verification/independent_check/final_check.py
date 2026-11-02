"""Independent final check of a Ninja Gaiden (NES) Any% run against TheRetroRunner's 11:32.183.
Verifier's own code (work/verify): imports nothing from ng/, tools/, assemble.py, check_inputs.py or yt/.

  python work/verify/final_check.py <final inputs.txt> [--report logs/<final>.report.json] [--name final]
                                    [--tail 1500] [--reuse]

1. input rules (vrules.py, own counter)                              -> PASS / FAIL
2. fresh power-on replay on BizHawk 2.11.1 NesHawk (vreplay.py/.lua)  -> per-frame RAM, nametable, screenshots
   (waits for >= 2.5 GB free RAM; one EmuHawk; ~5-8 min for a whole run)
3. START seen (Ryu first in the picture) / END seen (TIMER-000 first in the picture), time at 60.0988 fps
4. margin vs the record (video-timed: Ryu first visible f1707 -> TIMER-000 first shown f43238 = 41,531 video
   frames at 60.000 fps = 692.183 s = 41,599.4 NES frames), with error bars
5. stage-by-stage: the HUD TIMER digits' first appearance in every stage, ours vs the record's video
6. (optional) agreement with the project's own report (assemble.py --serial report.json)
Writes work/verify/run/<name>/final_check.json + final_check.txt + end_sheet.png + start_sheet.png.
--reuse: skip the replay and analyse work/verify/run/<name>/ again.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vrules, vanalyze  # noqa: E402  (the verifier's own modules)

FPS = 60.0988
REC = {"start_v": 1707, "end_v": 43238, "time_s": 692.183, "video_fps": 60.0}
REC["nes_frames"] = REC["time_s"] * FPS            # 41,599.37
REC_ERR_NES = 2                                      # +/-: 30-images/s capture (1 NES frame per end) + pts jitter
ROMHASH = "CA513F841D75EFEB33BB8099FB02BEEB39F6BB9C"


def fmt(s):
    return f"{int(s // 60)}:{s % 60:06.3f}"


def sheet(d, rows, out, crop=None, scale=3):
    ims = []
    for r in rows:
        p = os.path.join(d, "shots", f"s{r:06d}.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            if crop:
                im = im.crop(crop)
            ims.append((r, im.resize((im.width * scale, im.height * scale), Image.NEAREST)))
    if not ims:
        return None
    w, h = ims[0][1].size
    cols = min(len(ims), 3 if crop else 4)
    S = Image.new("RGB", (cols * w, ((len(ims) + cols - 1) // cols) * (h + 14)), "white")
    dr = ImageDraw.Draw(S)
    for i, (r, im) in enumerate(ims):
        x, y = (i % cols) * w, (i // cols) * (h + 14)
        S.paste(im, (x, y + 14))
        dr.text((x + 3, y + 1), f"row {r}", fill="black")
    S.save(out)
    return out


def main():
    a = sys.argv[1:]
    inputs = a[0]
    name = a[a.index("--name") + 1] if "--name" in a else "final"
    tail = a[a.index("--tail") + 1] if "--tail" in a else "1500"
    report = a[a.index("--report") + 1] if "--report" in a else None
    L = []

    def p(*x):
        s = " ".join(str(y) for y in x)
        print(s, flush=True)
        L.append(s)

    problems = []
    # 1. rules
    rr = vrules.check(inputs)
    p(f"INPUT RULES: {rr['verdict']}  ({rr['info']['rows']} rows; L+R {len(rr['R2_LR'])}, U+D {len(rr['R2_UD'])}, "
      f"period {len(rr['R3_period'])}, hold {len(rr['R4_hold'])}, release {len(rr['R5_release'])}, "
      f"windows {len(rr['R6_windows'])}, bad tokens {len(rr['R1_bad_tokens'])})")
    for b, s in rr["info"]["per_button"].items():
        p(f"   {b:6s} presses {s['presses']:5d}  min start-to-start {s['min_start_to_start']}  min hold {s['min_hold']}  "
          f"max/600f {s['max_per_600']} (cap 109)  max/1800f {s['max_per_1800']} (cap 246)")
    if rr["info"]["open_at_end"]:
        p("   held at the last row (allowed; a 1-row press there would still be reported here):", rr["info"]["open_at_end"])
    short_open = [x for x in rr["info"]["open_at_end"] if x[2] < 2]
    if short_open:
        problems.append(f"WARNING: a press shorter than 2 rows at the very end of the file {short_open} "
                        f"(check that holding it 2 rows changes nothing)")
    if rr["verdict"] != "PASS":
        problems.append("input rules: " + rr["verdict"])
    # 2. replay
    if "--reuse" not in a:
        r = subprocess.run([sys.executable, os.path.join(HERE, "vreplay.py"), inputs, name, "--tail", tail])
        if r.returncode:
            problems.append("replay failed")
    o = vanalyze.analyse(name)
    d = os.path.join(HERE, "run", name)
    m = o["meta"]
    p(f"REPLAY: fresh power-on, core {m.get('pref_core')}, rom sha1 {m.get('romhash')}, first row played "
      f"{m.get('first_row_played')} (row 1 = the launch frame), rows {m.get('rows')}, RAM sha1 at the last row "
      f"{(o.get('ram_at_last_row_sha1') or '?')[:12]}, lag frames {o['lag_rows']}, HUD tiles = digits: {o.get('tile_is_digit')}")
    if m.get("romhash") != ROMHASH or m.get("pref_core") != "NesHawk" or "PPU Bus" not in m.get("domains", ""):
        problems.append("wrong ROM or core")
    if "DONE" not in m:
        problems.append("replay did not finish (no DONE in meta.txt)")
    bad = [k for k in m if k.startswith(("ERROR", "BAD_TOKEN"))]
    if bad:
        problems.append(f"replay meta has errors: {bad}")
    if o["lives_drop_rows"]:
        problems.append(f"lives lost at rows {o['lives_drop_rows']}")
    p(f"DEATHS (lives $76 drops): {len(o['lives_drop_rows'])} {o['lives_drop_rows']}")
    # 3. clock
    p(f"START: RAM control row {o['start_ram']} ($33=$97 in 1-1), Ryu first in the picture row {o['start_seen']}; "
      f"1-1 TIMER digits first in the picture row {o.get('start_digits_picture')} / in the nametable row "
      f"{o['stages'][0]['digits_nt'] if o['stages'] else None} (must be equal)")
    if o["stages"] and o.get("start_digits_picture") != o["stages"][0]["digits_nt"]:
        problems.append("picture vs nametable offset at the 1-1 digits")
    p(f"END:   6-5 timer $63=0 row {o['end_ram']}, nametable TIMER 000 row {o['end_nt']}, TIMER-000 first in the "
      f"picture row {o['end_seen']}")
    st = o["start_seen"] or 175
    sheet(d, list(range(st - 2, st + 2)), os.path.join(d, "start_sheet.png"), None, 2)
    if o.get("end_seen"):
        sheet(d, list(range(o["end_seen"] - 6, o["end_seen"] + 3)), os.path.join(d, "end_sheet.png"), (20, 14, 150, 42), 3)
    res = {"rules": rr["verdict"], "start_seen": o["start_seen"], "end_seen": o["end_seen"]}
    if o.get("frames") is None:
        p("NOT FINISHED: no END seen (the run did not reach TIMER-000 within the tail)")
        problems.append("no END")
    else:
        fr, sec = o["frames"], o["seconds"]
        margin_f = REC["nes_frames"] - fr
        margin_s = REC["time_s"] - sec
        p(f"OUR TIME (Ryu first visible -> TIMER-000 first visible): {fr} NES frames / 60.0988 = {sec:.3f} s = {fmt(sec)}")
        p(f"RECORD: 11:32.183 = {REC['time_s']} s = {REC['nes_frames']:.1f} NES frames "
          f"(its video f1707 -> f43238, 41,531 frames at 60.000 fps)")
        verdict = ("BEATS the record" if margin_f > REC_ERR_NES else
                   ("TIES within the error bars" if margin_f >= -REC_ERR_NES else "SLOWER than the record"))
        p(f"MARGIN: {margin_s:+.3f} s = {margin_f:+.1f} NES frames (record-side error bars +/-{REC_ERR_NES} frames = "
          f"+/-{REC_ERR_NES / FPS:.3f} s; ours exact)  -> {verdict}")
        res.update({"frames": fr, "seconds": sec, "time": fmt(sec), "margin_s": margin_s, "margin_frames": margin_f,
                    "verdict": verdict})
        if margin_f <= REC_ERR_NES:
            problems.append(f"margin {margin_f:+.1f} f is not outside the error bars")
        if o["end_nt"] is not None and o["end_seen"] != o["end_nt"]:
            p(f"   note: picture END {o['end_seen']} != nametable END {o['end_nt']} (expected equal; LOOK at end_sheet.png)")
    # 4. stages vs the record (same on-screen event: TIMER digits first drawn in the stage)
    recst = {e["stage"]: e for e in json.load(open(os.path.join(HERE, "record_stage_events.json")))}
    p("STAGES (event = HUD TIMER digits first drawn in the stage; cum = NES frames after Ryu first visible; the record's "
      "video frames x 60.0988/60; +/-2 f; jitter of up to 5 f per stage from the 6-frame HUD redraw cycle):")
    p(f"   {'stage':6s} {'load':>6s} {'digits':>7s} {'ours cum':>9s} {'rec cum':>9s} {'cum diff':>9s} {'stage split diff':>16s}  rooms")
    rows_out = []
    for s in o["stages"]:
        rv = recst.get(s["stage"])
        dg = s["digits_nt"]
        if dg is None or rv is None:
            continue
        oc = dg - st
        rc = (rv["timer_digits"] - REC["start_v"]) * FPS / REC["video_fps"]
        rows_out.append({"stage": s["stage"], "load": s["load"], "digits_row": dg, "ours_cum": oc, "rec_cum": rc,
                         "cum_diff": oc - rc, "rooms": s["rooms"]})
    if o.get("frames") is not None:
        rc = (REC["end_v"] - REC["start_v"]) * FPS / REC["video_fps"]
        rows_out.append({"stage": "END", "load": None, "digits_row": o["end_seen"], "ours_cum": o["frames"],
                         "rec_cum": rc, "cum_diff": o["frames"] - rc, "rooms": []})
    for k, x in enumerate(rows_out):
        x["split_diff"] = (rows_out[k + 1]["cum_diff"] - x["cum_diff"]) if k + 1 < len(rows_out) else None
        sd = f"{x['split_diff']:+16.1f}" if x["split_diff"] is not None else f"{'(open)':>16s}"
        p(f"   {x['stage']:6s} {str(x['load']):>6s} {x['digits_row']:7d} {x['ours_cum']:9d} {x['rec_cum']:9.1f} "
          f"{x['cum_diff']:+9.1f} {sd}  {x['rooms']}")
    res["stages"] = rows_out
    # 5. the project's report
    if report and os.path.exists(report):
        rep = json.load(open(report, encoding="utf-8"))
        clk = rep.get("clock", {})
        p(f"PROJECT REPORT {report}: clock {json.dumps(clk)[:300]}")
        ps = {x["stage"]: x for x in rep.get("stages", [])}
        dif = []
        for s in o["stages"]:
            q = ps.get(s["stage"])
            if q and q.get("load") != s["load"]:
                dif.append((s["stage"], "load", q.get("load"), s["load"]))
        stc, enc = clk.get("start"), clk.get("end")
        st_p = stc.get("seen") if isinstance(stc, dict) else clk.get("start_seen")
        en_p = enc.get("seen") if isinstance(enc, dict) else clk.get("end_seen")
        if st_p is not None and st_p != o["start_seen"]:
            dif.append(("START seen", st_p, o["start_seen"]))
        if en_p is not None and en_p != o["end_seen"]:
            dif.append(("END seen", en_p, o["end_seen"]))
        if rep.get("input_frames") == int(m.get("rows", -1)) and rep.get("ram_sha1_a"):
            same = rep["ram_sha1_a"] == o.get("ram_at_last_row_sha1")
            p(f"   RAM sha1 at the last row: project {rep['ram_sha1_a'][:12]} / verifier "
              f"{(o.get('ram_at_last_row_sha1') or '')[:12]} -> {'SAME' if same else 'DIFFERENT'}")
            if not same:
                dif.append(("RAM sha1", rep["ram_sha1_a"][:12], (o.get("ram_at_last_row_sha1") or "")[:12]))
        p(f"   differences from the project's report: {dif if dif else 'none'}")
        if dif:
            problems.append(f"differs from the project's report: {dif}")
        res["report_diffs"] = dif
    p("PROBLEMS: " + ("; ".join(problems) if problems else "none"))
    res["problems"] = problems
    json.dump(res, open(os.path.join(d, "final_check.json"), "w"), indent=1)
    open(os.path.join(d, "final_check.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    p(f"written: {os.path.join(d, 'final_check.txt')} (+ .json, start_sheet.png, end_sheet.png: LOOK at both sheets)")


if __name__ == "__main__":
    main()

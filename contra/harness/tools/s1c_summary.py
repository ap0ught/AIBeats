"""Rule v2: one table of the stage 1 / stage 5 results against the versions before (read from the report files).

    python tools/s1c_summary.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.inputs import read_inputs  # noqa: E402
from contra.stages.s1_common import press_report  # noqa: E402


def jl(p):
    p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def seg_rows(j):
    return [tuple(x for x in r.split("+") if x) for r in j["rows"]]


def main():
    print("STAGE 1 (frames = stage 1's first frame to stage 2's first frame)")
    for k in (0, 1, 37):
        old, new = jl(f"logs/s1/w{k}v2.seg.json"), jl(f"logs/s1/w{k}v3.seg.json")
        if new is None:
            print(f"  title_wait {k}: no v3 segment")
            continue
        po, pn = press_report(seg_rows(old)), press_report(seg_rows(new))
        rep, asm, chk = jl(f"logs/s1/s1_w{k}v3_full.report.json"), jl(f"logs/s1_w{k}v3_asm.report.json"), jl(f"logs/s1/s1_w{k}v3_full.check_v2.json")
        repo = jl(f"logs/s1/s1_w{k}v2_full.report.json")
        asmo = jl(f"logs/s1_w{k}v2_asm.report.json")
        st = (asm or {}).get("stages") or [{}]
        sto = (asmo or {}).get("stages") or [{}]
        print(f"  title_wait {k}: {old['frames'] - 1} -> {new['frames'] - 1} frames ({new['frames'] - old['frames']:+d}); B presses {po['presses']} -> "
              f"{pn['presses']}; most in 600 rows {po['most_600']} -> {pn['most_600']}, in 1800 {po['most_1800']} -> {pn['most_1800']}; "
              f"run phase rows {old.get('run_rows')} -> {new.get('run_rows')}, core HP 0 on row {old.get('boss_kill_row')} -> {new.get('boss_kill_row')}")
        print(f"      verdicts {new.get('verdicts')}; plan refused {len(new.get('plan_refused_rows', []))} rows, pad refused {new.get('pad_refused')}; "
              f"repairs {len(new.get('repairs', []))} (old {len(old.get('repairs', []))})")
        if rep:
            ev = rep["relative"]
            print(f"      replay after a core reboot: stage 1 = {ev.get('L2')} frames, weapon ${ev.get('weapon_L2', 0):02x}, deaths {rep['events'].get('deaths', [])}, "
                  f"lag frames in play {ev.get('lag_frames', [])} (old {(repo or {}).get('relative', {}).get('lag_frames', [])}), weapons {ev.get('weapons')}")
        if asm:
            print(f"      assemble.py: replays_match {asm.get('replays_match')}, RAM sha1 {str(asm.get('ram_sha1_a'))[:12]}, trace sha1 {str(asm.get('trace_sha1_a'))[:12]}, "
                  f"stage frames {st[0].get('frames')} (old {sto[0].get('frames')}), stage lag {st[0].get('lag_frames')} (old {sto[0].get('lag_frames')}), "
                  f"deaths {asm.get('deaths')}, pad ignored on {asm.get('controller_ignored_frames')} frames, input rows {asm.get('input_frames')}")
        if chk:
            b = chk["stats"]["B"]
            print(f"      check_inputs --windows 600:109,1800:246 on the power-on list: {'PASS' if chk['pass'] else 'FAIL'}; B {b['presses']} presses, "
                  f"most in 600 / 1800 frames {b.get('max_presses_in_600_frames')} / {b.get('max_presses_in_1800_frames')}")
    print("STAGE 5 (frames = stage 5's first frame to stage 6's first frame)")
    hist_c1 = [tuple(r) for r in read_inputs(ROOT / "chain1/runs/prior_s5_c1.inputs.txt")]
    for name, oldp, hist in (("d0", "logs/s5/d0v5", None), ("w1", "logs/s5/w1v5", None), ("w37", "logs/s5/w37v5", None),
                             ("c1", "chain1/logs/s5/c1", hist_c1)):
        old, new = jl(oldp + ".seg.json"), jl(f"logs/s5/{name}_v3.seg.json")
        if new is None:
            print(f"  {name}: no v3 segment")
            continue
        po, pn = press_report(seg_rows(old), hist or ()), press_report(seg_rows(new), hist or ())
        rep, repo, chk = jl(f"logs/s5/{name}_v3.report.json"), jl(oldp + ".report.json"), jl(f"logs/s5/{name}_v3_v2check.json")
        print(f"  {name}: {old['frames'] - 1} -> {new['frames'] - 1} frames ({new['frames'] - old['frames']:+d}); B presses {po['presses']} -> {pn['presses']}; "
              f"most in 600 rows {po['most_600']} -> {pn['most_600']}, in 1800 {po['most_1800']} -> {pn['most_1800']}")
        print(f"      marks old {old.get('marks')}")
        print(f"      marks new {new.get('marks')}")
        print(f"      verdicts {new.get('verdicts')}; plan refused {len(new.get('plan_refused_rows', []))} rows, pad refused {new.get('pad_refused')}; "
              f"repairs {len(new.get('repairs', []))} (old {len(old.get('repairs', []))}); parity jump before tank {new.get('tank_parity_jump')}; "
              f"UFO wait '{new.get('ufo_wait')}'; lag (solver) run {new.get('lag_run')} / all {new.get('lag_total')}")
        if rep:
            print(f"      open-loop replay on a fresh emulator: stage 5 = {rep.get('L6')} frames, weapon ${rep.get('weapon_L6', 0):02x}, deaths {rep.get('deaths')}, "
                  f"lag frames in play {rep.get('lag')} (old {(repo or {}).get('lag')}), UFO X {rep.get('ufo_x')}, UFO hittable -> HP 0 "
                  f"{rep.get('ufo_dead', 0) - rep.get('ufo_hittable', 0)} (old {(repo or {}).get('ufo_dead', 0) - (repo or {}).get('ufo_hittable', 0) if repo else None})")
        if chk:
            b = chk["stats"]["B"]
            print(f"      check_inputs --windows 600:109,1800:246 on history + segment ({chk['frames']} rows): {'PASS' if chk['pass'] else 'FAIL'}; "
                  f"B most in 600 / 1800 frames over the whole list {b.get('max_presses_in_600_frames')} / {b.get('max_presses_in_1800_frames')}")


if __name__ == "__main__":
    main()

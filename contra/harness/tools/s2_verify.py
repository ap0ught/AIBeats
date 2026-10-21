"""Open-loop replay of a base-stage segment on a fresh emulator + the input rules.

    python tools/s2_verify.py <stage 2|4> <tag> <state> [--hist logs/x.inputs.txt]

Loads <state> (the stage's first frame), plays logs/s<stage>/<tag>.inputs.txt with no feedback at all and reports:
the row on which the next stage's first frame ($2C == 4) falls (must be the last row), deaths, weapon and lives at
the end, lag frames, the room and boss timeline read from RAM, and check_inputs.py at its defaults (with the last
40 rows of --hist in front when given, so the press cap is checked across the stage boundary too).
Writes logs/s<stage>/<tag>_verify.json. Exit code 1 if anything is wrong.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.emulator import BizHawk, State  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages.base_common import BIT, make_fields  # noqa: E402


def main():
    a = sys.argv[1:]
    hist = None
    if "--hist" in a:
        i = a.index("--hist")
        hist = a[i + 1]
        del a[i:i + 2]
    stage, tag, state = int(a[0]), a[1], a[2]
    base = ROOT / "logs" / f"s{stage}"
    rows = [tuple(r) for r in read_inputs(base / f"{tag}.inputs.txt")]
    out = {"stage": stage, "tag": tag, "state": state, "rows": len(rows)}
    ev = []
    with BizHawk(log_name=f"s{stage}_verify_{tag}.log", fields=make_fields()) as e:
        s0 = e.load(state)
        out["start"] = {k: s0[k] for k in ("frame", "frame_fc", "rng", "level", "lroutine", "weapon", "lives")}
        lvl = s0["level"]
        prev = e.ram_all()
        lag = deaths = 0
        first4 = None
        boss_row = None
        for i, r in enumerate(rows):
            s = State.parse(e.cmd("stepx %02x" % sum(BIT[b] for b in r)))
            m = e.ram_all()
            n = i + 1
            lag += int(s["lagged"])
            if m[0x30] == lvl:
                if m[0x64] != prev[0x64]:
                    ev.append((n, f"room {m[0x64] + 1}"))
                    if m[0x40] & 0x80 and boss_row is None:
                        boss_row = n
                if m[0x87] != prev[0x87]:
                    ev.append((n, f"platings destroyed {m[0x87]}"))
                if m[0x86] != prev[0x86] and boss_row is not None:
                    ev.append((n, f"boss parts left {m[0x86]}"))
                if m[0x3B] and not prev[0x3B]:
                    ev.append((n, "boss defeated flag"))
                for k in range(16):
                    if m[0x4B8 + k] and m[0x528 + k] in (0x1C, 0x10) and (prev[0x598 + k] & 0x80) and not (m[0x598 + k] & 0x80):
                        ev.append((n, f"final part in slot {k} can be hit"))
            if (m[0xB4] & 1) and not (prev[0xB4] & 1):
                deaths += 1
                ev.append((n, "DEATH"))
            if first4 is None and m[0x30] != lvl and m[0x2C] == 4:
                first4 = n
                ev.append((n, "next stage first frame"))
            prev = m
        out["end"] = {"level": prev[0x30], "lroutine": prev[0x2C], "weapon": prev[0xAA], "lives": prev[0x32]}
    out.update(lag=lag, deaths=deaths, next_stage_row=first4, boss_room_row=boss_row, events=ev)
    if boss_row is not None:
        bd = next((n for n, t in ev if t == "boss defeated flag"), None)
        out["boss_frames"] = (bd - boss_row + 1) if bd else None        # rows from the boss room's first row to the flag
        out["exit_frames"] = (first4 - bd) if (bd and first4) else None
    chk_rows = (list(read_inputs(ROOT / hist))[-40:] if hist else []) + rows
    tmp = base / f"{tag}_chk.inputs.txt"
    write_inputs(tmp, chk_rows, "verify: history tail + segment")
    cp = subprocess.run([sys.executable, str(ROOT / "check_inputs.py"), str(tmp)], capture_output=True, text=True)
    out["check_inputs"] = "PASS" if cp.returncode == 0 else "FAIL"
    out["check_inputs_tail"] = cp.stdout.strip().splitlines()[-6:]
    tmp.unlink()
    ok = (first4 == len(rows) and deaths == 0 and out["end"]["weapon"] == 0x13 and out["check_inputs"] == "PASS")
    out["ok"] = ok
    (base / f"{tag}_verify.json").write_text(json.dumps(out, indent=1))
    print(f"stage {stage} {tag} from {state}: {len(rows)} rows; next stage's first frame on row {first4}; deaths {deaths}; "
          f"weapon ${out['end']['weapon']:02X}; lives {out['end']['lives']}; lag {lag}; boss {out.get('boss_frames')} + exit "
          f"{out.get('exit_frames')}; check_inputs {out['check_inputs']}; {'OK' if ok else 'NOT OK'}")
    for n, t in ev:
        print(f"   row {n}: {t}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

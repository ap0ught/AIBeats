"""One line per verified base-stage run: python tools/s2_summary.py <stage> <tag> ...   (reads <tag>_verify.json and
<tag>_report.json in logs/s<stage>/). Boss rows are counted from the boss room's first row."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
stage = int(sys.argv[1])
REC = {2: 3716, 4: 5761}[stage]
print("| run | start | rows | vs record | rooms (frames each) | boss room row | boss rows | platings gone | final part open | "
      "parts dead | exit | lag | lost pad reads | plans (s) | replay |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for tag in sys.argv[2:]:
    base = ROOT / "logs" / f"s{stage}"
    v = json.loads((base / f"{tag}_verify.json").read_text())
    r = json.loads((base / f"{tag}_report.json").read_text())
    b0 = v["boss_room_row"]
    ev = v["events"]
    pl = [n - b0 + 1 for n, t in ev if t.startswith("platings destroyed")]
    op = sorted(set(n - b0 + 1 for n, t in ev if t.startswith("final part") and n > b0 + 20))
    dead = [n - b0 + 1 for n, t in ev if t.startswith("boss parts left") and n > b0 + 20] or \
           [n - b0 + 1 for n, t in ev if t == "boss defeated flag"]
    boss = r.get("boss", {})
    plans = boss.get("plans", [])
    start = f"{v['state']}" + (f" + pause {r['pause_rows']}" if r.get("pause_rows") else "")
    print(f"| {tag} | {start} (fc {r.get('fc0')}, rng {r.get('rng0')}) | {v['rows']} | {REC - v['rows']:+d} | "
          f"{'/'.join(str(x['frames']) for x in r['rooms'])} | {b0} | {v.get('boss_frames')} | {pl[-1] if pl else '-'} | "
          f"{op[0] if op else '-'} | {'/'.join(map(str, dead))} | {v.get('exit_frames')} | {v['lag']} | "
          f"{len(boss.get('drops', []))} | {sum(p['secs'] for p in plans)} ({boss.get('method', '?')}) | "
          f"{'OK' if v['ok'] else 'NOT OK'}, check_inputs {v['check_inputs']} |")

"""Print the phase scan results (logs/s7/scan/*.jsonl) compactly.

    python tools/s7_scan_show.py [detail]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
recs = []
for p in sorted((ROOT / "logs" / "s7" / "scan").glob("*.jsonl")):
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            r = json.loads(line)
            r["_file"] = p.stem
            recs.append(r)
recs.sort(key=lambda r: ((r["fc"] or 0) & 127, r["fc"] or 0))
for r in recs:
    m = r.get("marks") or {}
    pr = r.get("procs") or {}
    print(f"{r['_file']:7s} fc {str(r['fc']):>4} ph {(r['fc'] or 0) & 127:3d} lead {r['lead']:3d} frames {str(r['frames']):>5} "
          f"rows {str(r['rows']):>5} lag {str(r['lag']):>3} {'ok ' if r['ok'] and r['verified'] else 'BAD'} "
          f"{r.get('name') or r['state']:18s} corridor {str((pr.get('precart') or {}).get('cost')):>4} "
          f"trio {str((pr.get('trio') or {}).get('rows')):>4} door {str((pr.get('boss') or {}).get('rows')):>4} "
          f"lower1 {m.get('lower1')} walls3 {m.get('walls3')} bgrab {m.get('bgrab')} lower4 {m.get('lower4')} "
          f"kill {m.get('boss_killed')} {r['seconds']}s")
    if len(sys.argv) > 1:
        print("        remedies", r.get("remedies"))

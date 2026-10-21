"""Append (or refresh) the "Second pass" section of knowledge/s7_notes.md.

    python tools/s7_write_notes.py

The section's text is knowledge/s7_notes_second_pass.src.md (hand written); the tables marked @@...@@ are filled
from knowledge/s7_phase_table.json (tools/s7_phase_table.py). The first pass's text is never touched: the section
is everything after the line "# Second pass (2026-10-12)".
"""
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "knowledge" / "s7_notes_second_pass.src.md").read_text(encoding="utf-8")
t = json.loads((ROOT / "knowledge" / "s7_phase_table.json").read_text(encoding="utf-8"))
rows = [r for r in t["table"] if r["ok"] and r["verified"] and str(r["check_inputs"]).endswith("PASS")]
frames = [r["frames"] for r in rows]
lines = ["| `$1A` on the first frame | `$1A & 127` | start state | segment | vs record 4,488 | lag | claw corridor cost | door: rows from scroll frame 16 |",
         "|---|---|---|---|---|---|---|---|"]
for r in rows:
    st = r["state"] + (f" + {r['lead_pause']}-frame pause" if r["lead_pause"] else "")
    lines.append(f"| {r['start_fc']} | {r['start_phase_mod128']} | `{st}` | **{r['frames']:,}** | {r['vs_record']:+d} | {r['lag']} | "
                 f"{r['claw_corridor']['cost']} | {r['door_rows']} |")
bad = [r for r in t["table"] if not (r["ok"] and r["verified"])]
for r in bad:
    lines.append(f"| {r['start_fc']} | {r['start_phase_mod128']} | `{r['state']}` | FAILED ({r['result']}) | | | | |")
table = "\n".join(lines)
ch = ["| stage 6 segment (first pass) | its start `$1A` | stage 6 frames | stage 7 start `$1A` | stage 7 frames | sum | vs record 8,631 |",
      "|---|---|---|---|---|---|---|"]
for c in (t["pairing_with_stage_6"] or {}).get("measured_chains", []):
    ch.append(f"| `logs/s6/{c['s6_run']}` | {c['s6_start_fc']} | {c['s6_frames']:,} | {c['s7_start_fc']} | {c['s7_frames']:,} "
              f"(`logs/s7/{c['s7_run']}`) | **{c['sum']:,}** | {c['vs_record_pair']:+d} |")
chains = "\n".join(ch)
ph90 = next((r["frames"] for r in rows if r["start_fc"] == 152), None)
out = (src.replace("@@TABLE@@", table).replace("@@CHAINS@@", chains).replace("@@NPHASES@@", str(len(rows)))
       .replace("@@BEST@@", f"{min(frames):,}").replace("@@WORST@@", f"{max(frames):,}")
       .replace("@@MEDIAN@@", f"{statistics.median(frames):,.0f}").replace("@@PH90@@", f"{ph90:,}" if ph90 else "not re-solved"))
p = ROOT / "knowledge" / "s7_notes.md"
old = p.read_text(encoding="utf-8")
marker = "# Second pass (2026-10-12)"
head = old.split(marker)[0].rstrip()
if head.endswith("---"):
    head = head[:-3].rstrip()
new = head + "\n\n---\n\n" + out[out.index(marker):]
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(new, encoding="utf-8")
tmp.replace(p)
print("wrote", p, "lines", new.count("\n"))

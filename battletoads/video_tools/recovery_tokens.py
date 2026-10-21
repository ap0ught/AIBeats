"""What the recovery (2026-10-09/10: the corrected clock and the faster run) cost in tokens, from the transcripts.

    python yt/recovery_tokens.py [until ISO time]     -> logs/recovery_tokens.json, prints a table

Counted the same way as toads/tokens.py (every reply's usage: input + cache write + cache read + output, priced by
model): the main session from the viewer's correction to `until`, plus every subagent / workflow transcript of the
recovery (those are not in toads.tokens.totals(), which reads the top-level session files only).
Each transcript is assigned to the part of the run it worked on.
"""
import glob
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from toads.tokens import cost_of, TRANSCRIPTS  # noqa: E402

SESSION = "d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89"
SUB = TRANSCRIPTS / SESSION / "subagents"
MARKER = "someone said this about the battletoads video"        # the owner relaying the viewer's correction
MARKER_END = "can you provide me with the full video"            # the owner asking for the run video
# label of the workflow agent (meta 'description') or agent id -> part of the run
PART = {"track:END": "queen", "track:L13": "queen", "track:CORE": "queen", "assemble:up15": "queen", "verify:up15": "queen",
        "track:L12": "tower", "track:EARLY": "level8", "chain:A": "level8", "chain:B": "level8", "chain:K": "karnath",
        "verify:up16b2": "queen", "port:up16b2": "queen",
        "track:C": "level8", "track:K2": "karnath", "final:up17": "queen", "verify:": "queen", "port:": "queen",
        "acf2e9734a3068dd2": "terra", "a20695568e93f50c5": "level8", "aecdf6e3ddef861b2": "tower1"}
WORKFLOWS = ["wf_b9f4ee9a-e8d", "wf_494a9b9c-8f2", "wf_3c1656de-7bc"]


def usage_of(path, since=None, until=None, seen=None):
    seen = set() if seen is None else seen
    tok, cost, n = 0, 0.0, 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            ts = o.get("timestamp", "")
            if (since and ts < since) or (until and ts > until):
                continue
            u = o.get("message", {}).get("usage")
            rid = o.get("requestId") or o.get("uuid")
            if not u or rid in seen:
                continue
            seen.add(rid)
            tok += (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                    + u.get("cache_read_input_tokens", 0) + u.get("output_tokens", 0))
            cost += cost_of(o.get("message", {}).get("model", ""), u)
            n += 1
    return tok, cost, n


def part_of(label):
    for k, v in PART.items():
        if label == k or (k.endswith(":") and label.startswith(k)):
            return v
    return "other"


def main(until=None):
    main_file = TRANSCRIPTS / f"{SESSION}.jsonl"
    since = None
    with open(main_file, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") == "user":
                c = o.get("message", {}).get("content")
                text = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                if MARKER in text:
                    since = o["timestamp"]
                    break
    rows = []
    main_until = until
    with open(main_file, encoding="utf-8", errors="replace") as f:      # the main session stops counting when the owner asks
        for line in f:                                                   # for the run video: after that it is video and Zelda work
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") == "user" and since and o.get("timestamp", "") > since:
                c = o.get("message", {}).get("content")
                text = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                if MARKER_END in text:
                    main_until = min(until, o["timestamp"]) if until else o["timestamp"]
                    break
    t, c, n = usage_of(main_file, since, main_until)
    rows.append(("main session (orchestration)", "queen", t, c, n))
    for wf in WORKFLOWS:
        for p in sorted(glob.glob(str(SUB / "workflows" / wf / "agent-*.jsonl"))):
            meta = json.loads(Path(p[:-6] + ".meta.json").read_text(encoding="utf-8")) if os.path.exists(p[:-6] + ".meta.json") else {}
            label = meta.get("description", Path(p).stem)
            t, c, n = usage_of(p, None, until)
            rows.append((f"{wf} {label}", part_of(label), t, c, n))
    for aid in ("acf2e9734a3068dd2", "a20695568e93f50c5", "aecdf6e3ddef861b2"):
        p = SUB / f"agent-{aid}.jsonl"
        if p.exists():
            t, c, n = usage_of(p, since, until)
            rows.append((f"agent {aid}", part_of(aid), t, c, n))
    parts = {}
    for name, part, t, c, n in rows:
        a = parts.setdefault(part, [0, 0.0])
        a[0] += t
        a[1] += c
        print(f"{name:52s} {part:8s} {t:>14,} tok  ${c:>8.2f}  {n} replies")
    out = {"since": since, "until": until, "rows": [dict(name=r[0], part=r[1], tokens=r[2], cost=round(r[3], 2), replies=r[4]) for r in rows],
           "parts": {k: {"tokens": v[0], "cost": round(v[1], 2)} for k, v in parts.items()},
           "total": {"tokens": sum(r[2] for r in rows), "cost": round(sum(r[3] for r in rows), 2)}}
    (HERE.parent / "logs" / "recovery_tokens.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["parts"]), out["total"], "since", since)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

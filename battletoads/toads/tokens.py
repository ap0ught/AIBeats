"""The token counter for the video: how much AI it took, sampled from the session transcripts.

Every reply Claude Code makes is logged with its usage in ~/.claude/projects/<project>/<session>.jsonl.
This module sums those from the moment the Battletoads project began, writes a timeline the overlay can
roll (or chunk) from, and lets the harness stamp named marks ("first boot", "found X", "turbo tunnel
solved", ...) with the running totals at that moment.

    python -m toads.tokens                 -> print totals so far
    python -m toads.tokens mark "text"     -> append a mark to logs/token_marks.jsonl
    python -m toads.tokens timeline        -> rewrite logs/tokens_timeline.json (one point per reply)

Costs are computed from RATES ($ per million tokens). Change RATES if the published prices differ; the
token counts themselves are exact.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
LOGS = PROJECT / "logs"
TRANSCRIPTS = Path(os.path.expanduser("~")) / ".claude" / "projects" / "G--AI-World-Record"

# The project's first message: the owner asking which game to do next (TMNT / Battletoads / Mario 3).
START = "2026-09-26T00:00:00Z"
START_MARKER = "Battletoads"           # first user message on/after START containing this word

# $ per million tokens: (input, cache write 5m, cache write 1h, cache read, output). From the claude-api skill's
# model table (cached 2026-06-24); cache writes at the standard 1.25x (5 min) / 2x (1 h) of input.
RATES = {
    "claude-opus-5-5": (4.0, 5.0, 8.0, 0.20, 20.0),
    "claude-fable-5-1": (10.0, 12.5, 20.0, 0.25, 50.0),
    "claude-opus-4-8": (5.0, 6.25, 10.0, 0.50, 25.0),
    "claude-opus-5": (5.0, 6.25, 10.0, 0.50, 25.0),
}
DEFAULT_RATE = RATES["claude-opus-5-5"]


def cost_of(model: str, u: dict) -> float:
    r = RATES.get(model, DEFAULT_RATE)
    cc = u.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens")
    w5m = cc.get("ephemeral_5m_input_tokens")
    total_w = u.get("cache_creation_input_tokens", 0)
    if w1h is None and w5m is None:
        w1h, w5m = total_w, 0
    w1h, w5m = w1h or 0, w5m or 0
    return (u.get("input_tokens", 0) * r[0] + w5m * r[1] + w1h * r[2]
            + u.get("cache_read_input_tokens", 0) * r[3] + u.get("output_tokens", 0) * r[4]) / 1e6


def _iter_messages():
    for p in sorted(glob.glob(str(TRANSCRIPTS / "*.jsonl"))):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                ts = o.get("timestamp")
                if not ts or ts < START:
                    continue
                yield o


def _user_text(o) -> str:
    c = o.get("message", {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def timeline() -> list[dict]:
    """One point per assistant reply since the project began, with cumulative totals."""
    msgs = sorted(_iter_messages(), key=lambda o: o["timestamp"])
    t_start = None
    for o in msgs:
        if o.get("type") == "user" and START_MARKER in _user_text(o):
            t_start = o["timestamp"]
            break
    if t_start is None:
        t_start = START
    seen = set()
    pts = []
    tot = {"in": 0, "cw": 0, "cr": 0, "out": 0, "replies": 0, "cost": 0.0}
    for o in msgs:
        if o.get("type") != "assistant" or o["timestamp"] < t_start:
            continue
        rid = o.get("requestId") or o.get("uuid")
        u = o.get("message", {}).get("usage")
        if not u or rid in seen:
            continue
        seen.add(rid)
        i, cw, cr, out = (u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0),
                          u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0))
        cost = cost_of(o.get("message", {}).get("model", ""), u)
        tot["in"] += i; tot["cw"] += cw; tot["cr"] += cr; tot["out"] += out
        tot["replies"] += 1; tot["cost"] += cost
        pts.append({"ts": o["timestamp"], "model": o.get("message", {}).get("model", ""),
                    "in": i, "cw": cw, "cr": cr, "out": out, "cost": round(cost, 4),
                    "cum_out": tot["out"], "cum_cw": tot["cw"], "cum_cr": tot["cr"], "cum_in": tot["in"],
                    "cum_total": tot["in"] + tot["cw"] + tot["cr"] + tot["out"],
                    "cum_cost": round(tot["cost"], 2), "replies": tot["replies"]})
    return pts


def totals() -> dict:
    pts = timeline()
    if not pts:
        return {"replies": 0, "out": 0, "cw": 0, "cr": 0, "in": 0, "total": 0, "cost": 0.0, "since": START}
    p = pts[-1]
    return {"replies": p["replies"], "out": p["cum_out"], "cw": p["cum_cw"], "cr": p["cum_cr"], "in": p["cum_in"],
            "total": p["cum_total"], "cost": p["cum_cost"], "since": pts[0]["ts"], "until": p["ts"]}


def mark(text: str, extra: dict | None = None) -> dict:
    """Stamp a named moment with the running totals (the harness calls this at milestones)."""
    LOGS.mkdir(parents=True, exist_ok=True)
    t = totals()
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "mark": text, **t}
    if extra:
        rec.update(extra)
    with open(LOGS / "token_marks.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def read_marks() -> list[dict]:
    """Milestones, oldest first. Parallel sessions once wrote into this file at the same instant and interleaved
    two lines; those are skipped rather than trusted."""
    out = []
    p = LOGS / "token_marks.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def fmt(n: int) -> str:
    return f"{n / 1e9:.2f}B" if n >= 1e9 else f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k" if n >= 1e3 else str(n)


def main(argv):
    if argv[1:2] == ["mark"]:
        rec = mark(" ".join(argv[2:]))
        print(json.dumps(rec))
        return
    if argv[1:2] == ["timeline"]:
        pts = timeline()
        LOGS.mkdir(parents=True, exist_ok=True)
        (LOGS / "tokens_timeline.json").write_text(json.dumps(pts))
        print(len(pts), "points ->", LOGS / "tokens_timeline.json")
        return
    t = totals()
    print(f"since {t['since']}: {t['replies']} replies")
    print(f"  output       {fmt(t['out']):>8}")
    print(f"  cache write  {fmt(t['cw']):>8}")
    print(f"  cache read   {fmt(t['cr']):>8}")
    print(f"  uncached in  {fmt(t['in']):>8}")
    print(f"  total        {fmt(t['total']):>8}   est. ${t['cost']:.2f}")


if __name__ == "__main__":
    main(sys.argv)

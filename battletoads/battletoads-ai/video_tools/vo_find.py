"""find where a phrase starts in a narration section (voice/words.json from vo_words.py)"""
import json, re
from pathlib import Path
_W = json.loads((Path(__file__).parent / "voice" / "words.json").read_text(encoding="utf-8"))


def _n(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find(sec, phrase, after=0.0):
    """start time (s, within the narration file) of the first occurrence of phrase at/after `after`"""
    ws = _W[sec]
    want = [_n(w) for w in phrase.split() if _n(w)]
    best = None
    for i in range(len(ws)):
        if ws[i][0] < after:
            continue
        k = 0
        hits = 0
        for j, w in enumerate(want):
            if i + j < len(ws) and _n(ws[i + j][2]) == w:
                hits += 1
        score = hits / len(want)
        if score == 1.0:
            return ws[i][0]
        if best is None or score > best[0]:
            best = (score, ws[i][0])
    if best and best[0] >= 0.6:
        return best[1]
    raise KeyError(f"{sec}: phrase not found: {phrase!r}")


def length(sec):
    return _W[sec][-1][1] if _W[sec] else 0.0

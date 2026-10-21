"""Word timestamps for every narration file in voice/ -> voice/words.json {"03": [[start, end, "word"], ...], ...}
(run with the VibeVoice venv: it has faster-whisper; HF_HUB_OFFLINE=1 uses the cached model)."""
import json
import os
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).parent
m = WhisperModel(os.environ.get("VV_WHISPER", "small"), device="cpu", compute_type="int8")
out = {}
for p in sorted((HERE / "voice").glob("*.wav")):
    segs, _ = m.transcribe(str(p), language="en", word_timestamps=True)
    out[p.stem] = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for s in segs for w in s.words]
    print(p.stem, len(out[p.stem]), "words", flush=True)
(HERE / "voice" / "words.json").write_text(json.dumps(out), encoding="utf-8")

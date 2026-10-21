"""refresh voice/words.json for the given sections only"""
import json, sys
from pathlib import Path
from faster_whisper import WhisperModel
HERE = Path(__file__).parent
p = HERE / "voice" / "words.json"
d = json.loads(p.read_text(encoding="utf-8"))
m = WhisperModel("small", device="cpu", compute_type="int8")
for k in sys.argv[1:]:
    segs, _ = m.transcribe(str(HERE / "voice" / f"{k}.wav"), language="en", word_timestamps=True)
    d[k] = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for s in segs for w in s.words]
    print(k, " ".join(w[2] for w in d[k][:30]))
p.write_text(json.dumps(d), encoding="utf-8")

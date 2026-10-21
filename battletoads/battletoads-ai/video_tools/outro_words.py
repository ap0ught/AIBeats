"""whisper word timestamps of the owner's outro -> out/outro_words.json [[start, end, word], ...]"""
import json
from pathlib import Path
from faster_whisper import WhisperModel
HERE = Path(__file__).parent
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(str(HERE / "out" / "outro_audio.wav"), language="en", word_timestamps=True)
words = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
(HERE / "out" / "outro_words.json").write_text(json.dumps(words), encoding="utf-8")
print(" ".join(w[2] for w in words))
print("speech ends at", words[-1][1])

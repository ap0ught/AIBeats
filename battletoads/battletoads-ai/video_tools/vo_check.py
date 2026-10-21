"""Transcribe narration takes to spot dropped or garbled words: python vo_check.py 09 07 (run with the VibeVoice venv)."""
import sys
from faster_whisper import WhisperModel

m = WhisperModel("base", device="cpu", compute_type="int8")
for k in sys.argv[1:]:
    segs, _ = m.transcribe(f"vo/{k}.wav", language="en", vad_filter=True)
    print(k, " ".join(s.text.strip() for s in segs), "\n", flush=True)

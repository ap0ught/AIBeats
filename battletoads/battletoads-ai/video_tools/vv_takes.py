"""Local VibeVoice takes in the owner's own voice (model loads once).

  "path/to/vibevoice-env\\Scripts\\python" -u vv_takes.py <ref.wav> <outdir> <take ids...>

Reads voice_text/<id>.txt, writes <outdir>/<id>.wav, then transcribes each take with faster-whisper and prints how
many of the script's words came back (a garble check; the ear test is the owner's). Uses the 7B VibeVoice-Large in
4-bit like the VibeVoice runner (fits the 8 GB card); VV_MODEL / VV_QUANT / VV_CFG override."""
import os, re, sys, time

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("VV_MODEL", r"models/VibeVoice-Large")
QUANT = os.environ.get("VV_QUANT", "4bit")
CFG = float(os.environ.get("VV_CFG", "1.3"))


def words(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("'", "")).split()


def chunks(text, max_words=22):
    """sentence pairs of at most ~max_words, so each piece gets its own natural delivery"""
    sents = re.findall(r"[^.?!]+[.?!]+", text) or [text]
    out, cur = [], ""
    for st in sents:
        st = st.strip()
        if cur and len((cur + " " + st).split()) > max_words:
            out.append(cur); cur = st
        else:
            cur = (cur + " " + st).strip()
    if cur:
        out.append(cur)
    return out


def join(parts, out, gap=0.42):
    import numpy as np, soundfile as sf
    xs, sr = [], 24000
    for p in parts:
        x, sr = sf.read(p)
        xs += [x, np.zeros(int(gap * sr))]
        os.remove(p)
    sf.write(out, np.concatenate(xs[:-1]), sr)


def tighten(path, keep=0.38, min_gap=0.55, thr_db=-42):
    """cap long silences: any pause longer than min_gap s is shortened to keep s (breaths stay, dead air goes)"""
    import numpy as np, soundfile as sf
    x, sr = sf.read(path)
    w = int(0.02 * sr)
    n = len(x) // w
    rms = np.array([np.sqrt(np.mean(x[i * w:(i + 1) * w] ** 2)) + 1e-9 for i in range(n)])
    quiet = 20 * np.log10(rms) < thr_db
    keep_mask = np.ones(len(x), bool)
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * w / sr > min_gap:
                cut0 = i * w + int(keep / 2 * sr)
                cut1 = j * w - int(keep / 2 * sr)
                keep_mask[cut0:cut1] = False
            i = j
        else:
            i += 1
    sf.write(path, x[keep_mask], sr)


def main():
    # vv_takes.py <ref> <outdir> <ids...>   or   vv_takes.py --jobs ref|outdir|id ref|outdir|id ...
    serve = sys.argv[1] == "--serve"                 # keep the model loaded; take jobs from vo_jobs/*.job
    if sys.argv[1] == "--jobs":
        jobs = [tuple(j.split("|")) for j in sys.argv[2:]]
    elif serve:
        jobs = []
    else:
        jobs = [(sys.argv[1], sys.argv[2], t) for t in sys.argv[3:]]
    import torch
    from vibevoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference
    from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor
    t0 = time.time()
    processor = VibeVoiceProcessor.from_pretrained(MODEL)
    kw = dict(torch_dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa")
    if QUANT == "4bit":
        from transformers import BitsAndBytesConfig
        kw.pop("torch_dtype")
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = VibeVoiceForConditionalGenerationInference.from_pretrained(MODEL, **kw)
    model.eval()
    try:
        model.set_ddpm_inference_steps(int(os.environ.get("VV_STEPS", "20")))
    except Exception:
        pass
    print("model ready in %.0fs (%s, %s)" % (time.time() - t0, os.path.basename(MODEL), QUANT), flush=True)
    from faster_whisper import WhisperModel
    whisper = WhisperModel("base", device="cpu", compute_type="int8")
    def job_stream():
        for j in jobs:
            yield j
        if not serve:
            return
        jd = os.path.join(HERE, "vo_jobs")
        os.makedirs(jd, exist_ok=True)
        print("serving: drop ref|outdir|id lines into vo_jobs/*.job", flush=True)
        while True:
            fs = sorted(f for f in os.listdir(jd) if f.endswith(".job"))
            if not fs:
                time.sleep(2)
                continue
            p_ = os.path.join(jd, fs[0])
            line = open(p_, encoding="utf-8").read().strip()
            os.remove(p_)
            if line == "quit":
                return
            yield tuple(line.split("|"))

    for ref, outdir, tid in job_stream():
        os.makedirs(outdir, exist_ok=True)
        text = " ".join(open(os.path.join(HERE, "voice_text", f"{tid.split('#')[0]}.txt"), encoding="utf-8").read().split())
        out = os.path.join(outdir, f"{tid}.wav")
        t1 = time.time()
        chunked = tid.endswith("#chunk")
        if chunked:
            out = out.replace("#chunk", "_chunked")
        pieces = chunks(text) if chunked else [text]
        parts = []
        for k, piece in enumerate(pieces):
            tmp = out if len(pieces) == 1 else out.replace(".wav", f"_part{k}.wav")
            inputs = processor(text=["Speaker 1: " + piece], voice_samples=[[ref]], padding=True,
                               return_tensors="pt", return_attention_mask=True)
            o = model.generate(**inputs, max_new_tokens=None, cfg_scale=CFG, tokenizer=processor.tokenizer,
                               generation_config={"do_sample": False}, verbose=False)
            processor.save_audio(o.speech_outputs[0], output_path=tmp)
            del o, inputs
            torch.cuda.empty_cache()
            parts.append(tmp)
        if len(parts) > 1:
            join(parts, out)
        tighten(out)
        segs, _ = whisper.transcribe(out, language="en", vad_filter=True)
        hyp = words(" ".join(s.text for s in segs))
        want = words(text)
        hit = sum(1 for w in want if w in set(hyp))
        print("[%s] %.0fs to make | words back %d/%d (%.2f)" % (tid, time.time() - t1, hit, len(want), hit / max(1, len(want))),
              flush=True)


if __name__ == "__main__":
    main()

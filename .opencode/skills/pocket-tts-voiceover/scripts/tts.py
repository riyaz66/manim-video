#!/usr/bin/env python3
"""Script text -> narration.wav with Pocket TTS (local, CPU). Optionally writes word timings into timeline.json.

  python .opencode/skills/pocket-tts-voiceover/scripts/tts.py --text-file projects/x/script.txt \
      --out projects/x/audio/narration.wav --timeline projects/x/timeline.json [--voice alba] [--pause 0.4]

Pocket TTS cannot insert pauses from text, so each sentence is generated separately and a silence gap is added
between sentences. Because we know each sentence's exact duration, word times are spread across the sentence span
(good enough for cues and captions). For tighter word timing, run assemblyai-transcribe on the wav afterwards.
Install: pip install pocket-tts scipy numpy   (API per github.com/kyutai-labs/pocket-tts)
"""
import argparse, json, os, re

def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def spread(tokens, s, e, first_id):
    w = [max(len(t), 1) for t in tokens]; tot = sum(w); out = []; t0 = s
    for i, (tok, wi) in enumerate(zip(tokens, w)):
        t1 = t0 + (e - s) * wi / tot
        out.append({"id": first_id + i, "text": tok, "start": round(t0, 3), "end": round(t1, 3)}); t0 = t1
    return out

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text"); g.add_argument("--text-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default="alba", help="built-in voice name, or path to a wav of YOUR OWN voice (clone only with consent)")
    ap.add_argument("--pause", type=float, default=0.4, help="seconds of silence between sentences")
    ap.add_argument("--lead", type=float, default=0.3, help="silence at the start")
    ap.add_argument("--timeline", help="write/update words[] and audio in this timeline.json")
    a = ap.parse_args()

    import numpy as np
    from scipy.io import wavfile
    from pocket_tts import TTSModel

    text = a.text if a.text is not None else open(a.text_file, encoding="utf-8").read()
    sentences = split_sentences(text)
    model = TTSModel.load_model()
    state = model.get_state_for_audio_prompt(a.voice)     # slow: load once, reuse for every sentence
    sr = model.sample_rate

    chunks = [np.zeros(int(sr * a.lead), dtype=np.float32)]
    t = a.lead; words = []
    for s in sentences:
        audio = np.asarray(model.generate_audio(state, s).numpy(), dtype=np.float32)
        dur = len(audio) / sr
        words += spread(s.split(), t, t + dur, len(words))
        chunks += [audio, np.zeros(int(sr * a.pause), dtype=np.float32)]
        t += dur + a.pause
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    wavfile.write(a.out, sr, np.concatenate(chunks))
    print(f"wrote {a.out} ({t:.1f} s, {len(sentences)} sentences)")

    if a.timeline:
        tl = json.load(open(a.timeline, encoding="utf-8")) if os.path.exists(a.timeline) else {
            "meta": {"mode": "ai_voice", "fps": 30, "width": 1920, "height": 1080, "captions": {"max_words": 7, "max_chars": 42}}, "scenes": []}
        tl["audio"] = {"file": os.path.relpath(a.out, os.path.dirname(os.path.abspath(a.timeline)))}
        tl["words"] = words
        with open(a.timeline, "w", encoding="utf-8") as f:
            json.dump(tl, f, indent=2, ensure_ascii=False)
        print(f"wrote {len(words)} words to {a.timeline}")

if __name__ == "__main__":
    main()

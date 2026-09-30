---
name: pocket-tts-voiceover
description: |
  Trigger when: (1) User picks ai_voice mode, (2) User writes script.txt for narration, (3) User runs tts.py or needs wav + words[] timings, (4) User mentions Pocket TTS, voice alba, or local TTS.

  Generate a narration wav from a script with Pocket TTS running locally on CPU, and write approximate word timings into timeline.json.

  Use AFTER script.txt is written. Optionally refine with assemblyai-transcribe.
---

# Pocket TTS voice-over (local)

Install once: `pip install pocket-tts scipy numpy` (needs Python 3.10+ and PyTorch 2.5+; CPU is fine).
Source: https://github.com/kyutai-labs/pocket-tts

## How to use

1. Write the narration to `projects/<name>/work/script.txt` - short sentences, spell out symbols ("forty-five degrees").
2. Run from the repo root:
   `python .opencode/skills/pocket-tts-voiceover/scripts/tts.py --text-file projects/<name>/work/script.txt --out projects/<name>/work/audio/narration.wav --timeline projects/<name>/work/timeline.json`
   Options: `--voice alba` (built-in name), `--pause 0.4` (gap between sentences), `--lead 0.3`.
3. The script writes the wav and `words[]` with start/end times spread across each sentence.
   For tighter word timing, run `assemblyai-transcribe` on the wav afterwards (it replaces `words[]`).

## Scripts

- [scripts/tts.py](scripts/tts.py) - per-sentence TTS + silence gaps; writes wav + `words[]`.

## Quick Reference

```bash
python .opencode/skills/pocket-tts-voiceover/scripts/tts.py --text-file projects/<name>/work/script.txt --out projects/<name>/work/audio/narration.wav --timeline projects/<name>/work/timeline.json --voice alba --pause 0.4 --lead 0.3
```

## Common Pitfalls to Avoid

1. **Symbols spoken literally** - spell out units/degrees in script.txt.
2. **First run is slow** - model download/load happens once per run.
3. **Expecting pauses from text** - the script adds `--pause` silence between sentences.
4. **Voice cloning without consent** - clone only the teacher's own voice or with explicit consent; never present cloned speech as a real recording.

## Notes

- `--voice` also accepts a wav path for voice cloning (see consent rule above).
- Listen to the result. Mispronounced terms: respell in `script.txt` (e.g. "Doe-pler") and regenerate.
- Languages: English plus French, German, Portuguese, Italian, Spanish (see the repo README).

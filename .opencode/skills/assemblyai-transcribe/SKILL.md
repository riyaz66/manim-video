---
name: assemblyai-transcribe
description: |
  Trigger when: (1) User picks teacher_voice mode, (2) User provides a lesson wav/mp3/m4a, (3) User runs transcribe.py or needs words[] timings, (4) User wants to refine ai_voice timings with cloud STT.

  Transcribe a recorded lesson (teacher's voice) or generated narration with AssemblyAI and write word-level timings into timeline.json.

  Use AFTER audio is in projects/<name>/work/audio/. Next: captions-and-assembly for fixes.
---

# AssemblyAI transcription

Uploads the audio to AssemblyAI (cloud), so only use recordings the teacher is happy to send.

## Setup

The API key lives in `scripts/local_secrets.py` (`ASSEMBLYAI_API_KEY = "..."`). No environment variable needed.
That file is git-ignored - never print it, commit it, or paste it into chat.

## How to use

1. Put the recording in `projects/<name>/work/audio/` (wav/mp3/m4a; most formats work).
2. Put physics terms in `projects/<name>/work/vocab.txt`, one per line (max 6 words each). They are sent as `keyterms_prompt`.
3. Run from the repo root:
   `python .opencode/skills/assemblyai-transcribe/scripts/transcribe.py projects/<name>/work/audio/lesson.wav --vocab projects/<name>/work/vocab.txt --out projects/<name>/work/timeline.json --context "Physics lesson on <topic>."`
   Add `--language en` if the language is known; otherwise it is auto-detected.
4. The script prints the transcript id (keep it), and fills `audio` and `words[]` (seconds) in the timeline.
5. Next: `captions-and-assembly` so the teacher can fix mis-heard words.

## Scripts

- [scripts/transcribe.py](scripts/transcribe.py) - upload, poll, convert ms to seconds, fill `audio` + `words[]`.
- [scripts/local_secrets.example.py](scripts/local_secrets.example.py) - key file shape (never commit the real one).

## Quick Reference

```bash
python .opencode/skills/assemblyai-transcribe/scripts/transcribe.py projects/<name>/work/audio/lesson.wav --vocab projects/<name>/work/vocab.txt --out projects/<name>/work/timeline.json --context "Physics lesson on <topic>." --language en
```

## Common Pitfalls to Avoid

1. **Uploading without consent** - cloud service; confirm the teacher is happy to send it.
2. **Printing the API key** - never print, commit, or paste `local_secrets.py`.
3. **Expecting perfect terms** - rare physics terms mis-hear; that is why caption-fix exists.
4. **Forgetting vocab format** - one term per line, max 6 words each.

## Notes

- If AssemblyAI rejects the vocabulary/context options, the script retries without them and says so.
- Times from the API are milliseconds; the script converts to seconds.

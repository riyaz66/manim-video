# Physics Video Studio

A physics teacher uses this repo to make explainer videos with Manim.
For ANY request to make, edit or fix a physics video, load the `physics-video-studio` skill first and follow it.

Skills (in `.opencode/skills/`, each self-contained with scripts):
- `physics-video-studio` - workflow and modes (start here)
- `pocket-tts-voiceover` - local text-to-speech (Pocket TTS)
- `assemblyai-transcribe` - speech-to-text word timings (AssemblyAI)
- `captions-and-assembly` - caption fixes, SRT, final ffmpeg assembly
- `manim-physics-scenes` - Manim scene rules, cue-sync helper, template
- `manim-composer` - plan vague idea into scene-by-scene `scenes.md` before coding
- `manimce-best-practices` - Manim Community Edition rules (`from manim import *`, `manim` CLI)
- `video-deck` - present lessons with Manim Slides (scene `Slide` + `next_slide()`, click back/forth live animation) + optional pptx frame decks

Global rules:
- Accuracy over polish. If unsure about physics, ask the teacher.
- Never rewrite the teacher's words; never print or commit `local_secrets.py`.
- `live-dictate/` at the repo root is a SEPARATE project (classroom dictate-canvas, Python server + browser frontend, Gemini-only). It has its own `plan.md`; do not mix it with `projects/<name>/` video-studio rules.
- Projects live in `projects/<name>/` with `work/` (all files) + `video/` (finished mp4s only) — copy `projects/_template/` which already contains both. Finished teaching decks (`.pptx` from `video-deck`) go in `projects/<name>/slides/`.
- Unique folders only: before creating, `Test-Path projects/<name>`; if it exists, use `<name>-2`, `<name>-3`, … Never overwrite or delete an existing project. Two agents must never share one folder.
- Captions are YouTube-small everywhere (`assemble.py` auto-scales: ~11px on 480p drafts, ~24px on 1080p finals). QA snapshots must show captions not covering the video.
- Drafts `-ql` (low quality OK); finals at least `-qh` (1080p). Ask before going higher (e.g. `-qk` 4K).

QA (frame check for misalignment):
- `captions.py cues work/timeline.json` must resolve before render.
- Draft `-ql`, then snapshot: `ffmpeg -y -ss <cue_sec> -i video/<name>_draft.mp4 -frames:v 1 work/out/qa_<cue>.png`.
- Or still: `manim -ql -s --media_dir work/out/media <scene.py> <Scene>`.
- Fix cue `at_word` or scene `f(clock)`, re-render draft, re-snapshot. `-qh` only after approval.

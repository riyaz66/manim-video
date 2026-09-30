---
name: captions-and-assembly
description: |
  Trigger when: (1) Captions need fixing via corrected.txt, (2) User runs captions.py srt/groups/cues/apply-text, (3) User runs assemble.py or needs muxed final mp4, (4) Cue warnings appear after a caption fix, (5) QA frame snapshots are needed.

  Let the teacher correct mis-heard caption words while keeping timings and animation cues, export SRT, and mux audio plus burned-in captions onto the rendered Manim video with ffmpeg.

  Use AFTER transcription/TTS and AFTER each Manim render.
---

# Captions and assembly

## How to use

### Fix captions

1. Give the teacher `assets/caption-editor.html` (open it in a browser). They load `work/timeline.json` and the audio, click a line to hear it, fix the wording, and download `corrected.txt`. Save it as `projects/<name>/work/corrected.txt`.
2. Apply it (keeps timings; 1:1 word swaps keep ids so cues survive):
   `python .opencode/skills/captions-and-assembly/scripts/captions.py apply-text projects/<name>/work/timeline.json projects/<name>/work/corrected.txt`
   A backup `timeline.json.bak` is written. Read any WARNING about cues and re-point those cues.

### Other commands (same script)

- `captions.py srt <timeline> <out.srt>` - caption file.
- `captions.py groups <timeline> <out.json>` - caption groups.
- `captions.py cues <timeline>` - resolve `scene.cue` names to seconds (sanity check before rendering).

### Assemble

`python .opencode/skills/captions-and-assembly/scripts/assemble.py projects/<name>/work/timeline.json <rendered.mp4> projects/<name>/video/<name>_final.mp4`
- Adds the narration audio (if `audio.file` exists) and burns in captions from `words[]`.
- Captions are YouTube-small by rule: `assemble.py` scales with video height (`FontSize=height*0.022`, min 10; `Outline=1` on drafts, `MarginV=height*0.02`). 480p draft -> ~11px, 1080p final -> ~24px. Never hardcode large fonts.
- `--no-captions` skips captions. Silent videos with no audio work too.
- Caption fixes only need this step again (seconds); no Manim re-render.
- Keep captions out of Manim scenes: no `add_subcaption`.

### QA snapshots

```bash
python .opencode/skills/captions-and-assembly/scripts/captions.py cues projects/<name>/work/timeline.json
ffmpeg -y -ss <cue_sec> -i projects/<name>/video/<name>_draft.mp4 -frames:v 1 projects/<name>/work/out/qa_<cue>.png
```

## Scripts

- [scripts/captions.py](scripts/captions.py) - apply-text (timings preserved), srt, groups, cues.
- [scripts/assemble.py](scripts/assemble.py) - ffmpeg mux audio + burned-in captions.

## Assets

- [assets/caption-editor.html](assets/caption-editor.html) - teacher UI: load timeline + audio, click-to-hear, download corrected.txt.

## Quick Reference

```bash
python .opencode/skills/captions-and-assembly/scripts/captions.py cues projects/<name>/work/timeline.json
python .opencode/skills/captions-and-assembly/scripts/captions.py srt projects/<name>/work/timeline.json projects/<name>/work/out/captions.srt
python .opencode/skills/captions-and-assembly/scripts/assemble.py projects/<name>/work/timeline.json <rendered.mp4> projects/<name>/video/<name>_draft.mp4
```

## Common Pitfalls to Avoid

1. **Rewriting teacher words by hand** - always go through `apply-text` so ids/timings survive.
2. **Ignoring cue WARNINGs** - if a fix removes a cue word, re-point `at_word` in `timeline.json`.
3. **Manim captions** - never bake captions into scenes; assembly burns them in.
4. **Final before QA** - snapshot cue frames first (check caption size is small, not covering video); `-qh` only after caption approval.
5. **Caption size** - never use large fixed fonts; `assemble.py` auto-scales YouTube-small.

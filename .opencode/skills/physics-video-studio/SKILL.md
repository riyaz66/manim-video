---
name: physics-video-studio
description: |
  Trigger when: (1) User wants a physics explainer video with Manim, (2) User runs /make-video or asks to make/edit/fix a physics video, (3) User mentions silent, ai_voice, or teacher_voice mode, (4) User wants synced captions over a physics animation.

  Orchestrator for accurate, captioned physics videos. Routes to pocket-tts-voiceover, assemblyai-transcribe, captions-and-assembly, and manim-physics-scenes.

  Start here for ANY video request. Use BEFORE writing scenes or audio.
---

# Physics video studio (orchestrator)

Turn a physics lesson into an accurate, captioned explainer video. Load the other skills as the steps need them.

## How to use

### Pick the mode (ask if the teacher didn't say)

| Mode | Audio comes from | Word timings come from |
|---|---|---|
| `silent` | none | plan durations |
| `ai_voice` | `pocket-tts-voiceover` | tts.py (sentence spans), optionally refined by `assemblyai-transcribe` |
| `teacher_voice` | teacher's recording | `assemblyai-transcribe` |

### Workflow

1. **Plan.** Pick a UNIQUE folder: run `Test-Path projects/<name>` first — if it exists (another agent may own it), use `<name>-2`, `<name>-3`, … Never overwrite, delete, or share an existing project folder. Then copy `projects/_template/` to `projects/<final-name>/` (creates `work/` + `video/` by default). Announce the final folder name. All project files live in `work/`; only finished mp4s go in `video/` for the teacher. Write `work/plan.md`: misconception, scene list, palette, physics sanity check. Write `work/physics.json`. Show the plan; wait for approval. For vague ideas, use `manim-composer` to draft `scenes.md` first.
2. **Audio + timings.** silent: skip. ai_voice: write `work/script.txt`, load `pocket-tts-voiceover`. teacher_voice: ask for the audio file, load `assemblyai-transcribe`.
3. **Fix captions first** (teacher_voice always; ai_voice if the teacher wants): load `captions-and-assembly`, open the caption editor, apply corrected text. Do this BEFORE placing cues if possible.
4. **Cues.** Read timed words in `work/timeline.json`; add `scenes[].cues[]` pointing at word ids (see `references/timeline-schema.md`).
5. **Scenes.** Load `manim-physics-scenes` (+ `manimce-best-practices` for craft, `manim-composer` for planning). Write scene(s) in `work/scenes/`, draft-render (`-ql`).
6. **Assemble.** Load `captions-and-assembly`; mux audio + YouTube-small burned-in captions. Output to `video/<name>_draft.mp4` and share that path only.
7. **QA + Final.** Snapshot cue frames (`ffmpeg -ss`) into `work/out/`, fix misalignment, re-draft. After teacher approves captions, render final at least `-qh` (1080p) to `video/<name>_final.mp4` and assemble again. Ask if they want higher (e.g. `-qk` 4K).

## References

- [references/timeline-schema.md](references/timeline-schema.md) - timeline.json shape, cue-by-word-id rules.

## Rules

- Layout: `projects/<name>/video/` holds ONLY finished mp4s for the teacher; everything else lives in `projects/<name>/work/` (plan, physics, timeline, script, audio, scenes, out).
- Unique folders: `Test-Path` before create; existing folder means another agent owns it — suffix `-2`, `-3`, … and announce. Never overwrite, merge, or delete.
- `work/timeline.json` is the single source of truth; captions are never typed into scenes.
- Never rewrite the teacher's words. Corrections go through `captions.py apply-text`.
- Physics numbers live in `work/physics.json`; scenes assert the sanity check.
- If unsure about a physics fact, say so and ask. Do not invent.
- Never print or share the contents of `local_secrets.py`.

## Quick Reference

```bash
# New project (unique folder — another AI agent may own a same-named one)
$name = "<name>"
if (Test-Path "projects/$name") { $i = 2; while (Test-Path "projects/$name-$i") { $i++ }; $name = "$name-$i" }
Copy-Item -Recurse projects/_template "projects/$name"
```

## Common Pitfalls to Avoid

1. **Skipping plan approval** - Always show plan + sanity check before building.
2. **Reusing an existing folder** - Always `Test-Path` first; a same-named folder may belong to another agent. Suffix and announce instead.
2. **Typing captions into Manim** - Captions come only from `timeline.json` via assembly.
3. **Cues by seconds** - Cues point at word ids, not times, so caption fixes survive.
4. **Final before caption approval** - Draft `-ql` only until the teacher approves captions.

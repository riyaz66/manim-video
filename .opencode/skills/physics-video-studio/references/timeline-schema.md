# timeline.json

```json
{
  "meta": { "title": "...", "mode": "silent|ai_voice|teacher_voice", "fps": 30, "width": 1920, "height": 1080,
            "captions": { "max_words": 7, "max_chars": 42 } },
  "audio": { "file": "audio/narration.wav" },
  "words": [ { "id": 0, "text": "Hello", "start": 0.30, "end": 0.61 } ],
  "scenes": [ { "id": "s1", "engine": "manim", "file": "scenes/projectile.py",
                "cues": [ { "name": "launch", "at_word": 3, "offset": 0.0 } ] } ]
}
```
- Times are seconds. `audio.file` is relative to the timeline's folder. Omit `audio` for silent videos.
- A cue points at a word **id**, not a time. Caption fixes keep ids for 1:1 swaps, so cues survive.
  If a fix removes a cue's word, `captions.py apply-text` prints a warning; re-point the cue.
- Cue names are addressed as `sceneId.cueName` (e.g. `s1.launch`).
- Choose cue words that mark a visual moment: "launched", "now watch", "notice that".

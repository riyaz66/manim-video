---
name: manim-physics-scenes
description: |
  Trigger when: (1) User needs the visual part of a physics video, (2) Code reads physics.json or timeline.json cues, (3) User mentions cue-synced motion, sanity-check assert, or f(clock) updaters, (4) Rendering a project scene with manim -ql/-qh.

  Write and render Manim Community Edition physics animations synced to timeline.json cues, with motion as a pure function of clock and a physics sanity check.

  Use AFTER cues are placed. Use WITH manimce-best-practices for craft and manim-composer for planning.
---

# Manim physics scenes

## Setup

`pip install manim`, plus ffmpeg and LaTeX (for equations). Use Manim **Community Edition** only (`from manim import *`, `manim` CLI).

## How to use

### Write a scene

1. Copy `assets/projectile_template.py` to `projects/<name>/work/scenes/<file>.py` and adapt it.
2. Read numbers from `work/physics.json`; assert the sanity check (the template shows how).
3. Sync with `scripts/sync.py`:
   - `t = tl.cue("s1.launch")` gives seconds into the narration.
   - `tl.wait_until(self, t)` pauses the scene until then.
   - End with `tl.wait_until(self, tl.end_time() + 0.5)` so the video covers all the audio.
4. Motion = f(clock): use updaters on `tau_phys(clock)`, not accumulated steps, so re-timing is safe. Stretch short physics (e.g. 2 s fall) across long narration (slow-motion) so the video stays live.
5. No captions and no audio inside Manim. `captions-and-assembly` adds both.

### Render

Draft: `manim -ql --media_dir projects/<name>/work/out/media projects/<name>/work/scenes/<file>.py <SceneClass>` (854x480, low quality is fine for drafts).
Final: at least `-qh` (1920x1080). Same command with `-qh`. Output lands under `projects/<name>/work/out/media/videos/<file>/<quality>/<SceneClass>.mp4`, then assemble to `video/<name>_final.mp4` for the teacher.
Higher (e.g. `-qk` 4K) only on request - ask the teacher.
Then load `captions-and-assembly`.

## Scripts

- [scripts/sync.py](scripts/sync.py) - `Timeline.cue("s1.name")` + `wait_until(scene, t)` + `end_time()`.

## Assets

- [assets/projectile_template.py](assets/projectile_template.py) - cue-synced scene with physics.json assert; copy and adapt.

## References

- [references/manim-rules.md](references/manim-rules.md) - palette, Monospace Text, labels with units, closed-form physics, sanity-check assert.
- `manimce-best-practices/rules/*.md` - Scene/mobject/animation/text/axes/updater/camera/CLI craft details.
- `manim-composer/templates/scenes-template.md` - scene-by-scene plan shape before coding.

## Quick Reference

```python
tl = Timeline("projects/<name>/timeline.json")
t_drop = tl.cue("s1.drop")
tl.wait_until(self, t_drop)
ball.add_updater(lambda m: m.move_to(pos(tau_phys(self.renderer.time))))
tl.wait_until(self, tl.end_time() + 0.5)
```

## Common Pitfalls to Avoid

1. **Real-time short physics over long audio** - video goes static; stretch with slow-motion label.
2. **FadeIn on updaters that change subobject count** - `add()` first or attach updaters after the `play`.
3. **Captions in Manim** - never use `add_subcaption`; captions come from `timeline.json`.
4. **LaTeX in drafts** - prefer Monospace `Text` for first-try renders.

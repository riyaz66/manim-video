---
name: video-deck
description: |
  Trigger when: (1) User wants to present or teach a lesson with slides or click-through animation, (2) User mentions manim-slides, next_slide, present, (3) User wants to step a Manim animation forth and back, (4) User wants a PPT / PowerPoint / slides of a video, (5) User runs generate_deck.py or manim-slides render/present.

  Two tools: Manim Slides (preferred - the scene itself becomes a presentation; right arrow plays each segment forward, left arrow plays it REVERSED) and a PPTX frame deck generated from a rendered mp4.

  Use AFTER scenes exist (Manim Slides) or AFTER the video exists (pptx). Never modifies timeline/physics/audio/captions.
---

# Lesson presentation

## 1. Manim Slides (preferred: click forth & back, real animation)

The scene itself becomes the presentation - no frame chopping, full render
quality, and going back plays the animation *in reverse* (manim-slides
pre-renders `_reversed.mp4` segments).

### Convert a scene (3 edits)

1. After `from manim import *` add: `from manim_slides import Slide`
2. `class X(Scene):` -> `class X(Slide):`
3. Split the waits at cue times with `self.next_slide()`:

```python
wait_live(self, t_release)   # was: wait_live(self, t_watch)
self.next_slide()            # slide 1 ends here - pressing right plays from the release
wait_live(self, t_watch)
self.next_slide()            # slide 2 ends here - pressing right makes the graph appear
```

`next_slide()` only records a boundary during render - timing and the full
video output are unchanged, so the normal video flow keeps working.

Working example: `projects/spring-shm/work/scenes/spring_osc.py`
(4 slides split at cues release / watch / period).

### Render + present (from `projects/<name>/work/`)

```bash
python -m manim_slides render -ql --media_dir out/media scenes/<file>.py <Scene>
python -m manim_slides present <Scene>
```

- Presenter is a Qt window on your desktop:
  - **Right arrow / click / Space** = next slide (plays forward)
  - **Left arrow** = previous slide (plays REVERSED - true back-and-forth)
  - **Esc** = quit
- Section videos + reversed segments land in `work/slides/` (git-ignored).
- The normal full mp4 still renders to `work/out/media/...` - captions/assembly
  flow unaffected.
- The presenter has **no narration audio** (narration lives in the final mp4);
  the teacher talks over it.

## 2. PPTX frame deck (fallback, from a rendered mp4)

`generate_deck.py` chops an mp4 into full-bleed slides (10 fps default,
auto-advance so it plays at video speed). Static frames - looks softer than
the video; prefer Manim Slides for presenting.

```bash
python .opencode/skills/video-deck/scripts/generate_deck.py projects/<name>
#  --manual step only, no autoplay   --intro add title slide   --fps N   --video X --out Y
python .opencode/skills/video-deck/scripts/verify_deck.py projects/<name>/slides/<name>_slides.pptx
```

Output: `projects/<name>/slides/<name>_slides.pptx` (frames cached in
`work/out/deck_frames/`, git-ignored).

## Output convention (repo-wide)

- Presentation deliverables live in `projects/<name>/slides/`.
- manim-slides render data lives in `projects/<name>/work/slides/` (cache).

## Common Pitfalls to Avoid

1. **`manim-slides` exe fails with `QtBindingsNotFoundError` on this machine** -
   always call it as `python -m manim_slides ...` (verified working); the bare
   exe launcher cannot import PySide6 here.
2. **next_slide() placement** - put it BEFORE the wait/play that shows the next
   moment, so pressing right *plays* that moment (e.g. graph FadeIn must come
   after the break).
3. **Expecting audio in the presenter** - it is silent; play the mp4
   separately if narration matters, or talk over it.
4. **Deck built before the final render** - regenerate the pptx after a `-qh`
   final lands (it prefers `_final.mp4` automatically).
5. **Long videos at 10 fps make 600+ slides** - use `--fps 6`.
6. **This pptx is not the captioned deliverable** - captions/audio stay in the
   mp4.

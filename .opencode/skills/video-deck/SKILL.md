---
name: video-deck
description: |
  Trigger when: (1) User wants a PPT / PowerPoint / slides of a video, (2) User says "turn the video into slides" / "video as animation in PowerPoint", (3) User wants to present or teach a lesson in class from slides, (4) User runs generate_deck.py or asks to refresh a project's deck.

  Convert a finished project video into a PowerPoint deck where every slide is one video frame, so the lesson plays forward like an animation inside PowerPoint (Next = forward, Previous = backward; auto-plays at video speed by default).

  Use AFTER the video exists (draft or final). Never modifies video, timeline or scenes.
---

# Video deck (video -> PowerPoint animation)

Turns `projects/<name>/video/<name>_<final|draft>.mp4` into
`projects/<name>/slides/<name>_slides.pptx`: one full-bleed slide per sampled
frame. In the slideshow, stepping next/previous scrubs the animation frame by
frame, and by default the deck also auto-advances at the sampling rate, so it
plays the whole lesson at video speed.

## How to use

1. Run from the repo root (after a draft or final render exists):
   `python .opencode/skills/video-deck/scripts/generate_deck.py projects/<name>`
2. Open `projects/<name>/slides/<name>_slides.pptx`, start the slideshow:
   - **plays automatically** (10 fps -> real-time), arrow keys still step frames.
   - `--manual` = no autoplay, only you step with Next/Previous.
   - `--fps 6` = fewer/slower slides for long videos; `--fps 15` = smoother.
   - `--intro` = add a title slide (project title from timeline.json) first.
   - `--video path.mp4` / `--out path.pptx` = override source and destination.

## Output convention (repo-wide)

- Finished decks live in `projects/<name>/slides/<name>_slides.pptx` (alongside
  `video/` for mp4s). Regenerate after re-rendering the video - it never
  overwrites anything but its own pptx.
- Frames are cached in `projects/<name>/work/out/deck_frames/` (git-ignored).

## Scripts

- [scripts/generate_deck.py](scripts/generate_deck.py) - video -> frame slides
  (ffmpeg one-pass sampling, python-pptx, `p:transition advTm` auto-advance).
- [scripts/verify_deck.py](scripts/verify_deck.py) - sanity check a deck:
  `python .opencode/skills/video-deck/scripts/verify_deck.py <path.pptx>`.

## Quick Reference

```bash
python .opencode/skills/video-deck/scripts/generate_deck.py projects/spring-shm
python .opencode/skills/video-deck/scripts/generate_deck.py projects/spring-shm --fps 6 --manual
python .opencode/skills/video-deck/scripts/verify_deck.py projects/spring-shm/slides/spring-shm_slides.pptx
```

## Common Pitfalls to Avoid

1. **Deck built before the final render** - regenerate once the `-qh` final lands
   (the deck picks `_final.mp4` over `_draft.mp4` automatically).
2. **Too many slides on long videos** - 60+ s videos at 10 fps make 600+ slides;
   use `--fps 6`.
3. **Distortion** - frames are stretched to the slide exactly; both are 16:9, so
   never re-encode the source video to a non-16:9 size.
4. **Relying on autoplay for inspection** - use `--manual` when the teacher wants
   to dwell on one moment; autoplay has no pause key (Esc leaves the show).
5. **This deck is not the captioned deliverable** - captions/audio stay in the
   mp4; the deck is a silent frame-by-frame companion for class presentation.

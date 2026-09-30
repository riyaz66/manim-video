# Free-fall from 20 m - two masses land together

Folder: `projects/free-fall-2` (`free-fall` was already taken by another run - never reused).

## Misconception

Heavier balls fall faster. Correction: with no air resistance the acceleration of *every*
dropped object is `g`, independent of mass - so both balls share the same `y(t)` and `v(t)`
and strike the ground at the same instant.

## Physics sanity check (in `physics.json`, asserted in the scene)

- `h = 20 m`, `g = 9.81 m/s^2`, `v0 = 0`
- fall time `T = sqrt(2h/g) = sqrt(40/9.81) = 2.0193 s` -> **2.02 s** (tol 0.02 s)
- impact speed `v = g*T = sqrt(2gh) = 19.81 m/s` -> **19.8 m/s** (tol 0.15 m/s)
- mass cancels: `y(t) = h - 0.5*g*t^2` for both balls (1 kg and 5 kg are labels only)
- The scene `assert`s both numbers before animating; a wrong constant fails the render
  loudly instead of producing a wrong video.

## Scene list (single Manim scene `FreeFall`, one idea)

Screen: 1920x1080, Monospace `Text` everywhere (no LaTeX - keeps first-try renders safe).

1. **Setup (0 - 1.5 s)** - Title: `Two balls, 20 m drop: same fall time`.
   Left: drop rig - ground line `ground: y = 0 m`, release line `release: y = 20 m`,
   height ruler ticks `0 / 10 / 20 m`, two balls (1 kg YELLOW small, 5 kg ORANGE large)
   with labels `m = 1 kg` and `m = 5 kg`. Constant banner `a = g = 9.81 m/s^2 (no air resistance)`.
   Right-top: empty position-time axes `t (s)` 0-2.5, `y (m)` 0-20, titled `position-time: y(t)`.
2. **Cue `s1.drop` (1.5 s)** - both balls release. Motion is a pure function of the clock:
   `tau(clock)` -> `y = h - 0.5*g*tau^2`, both balls use the *same* `y`, so they can never separate.
3. **Live graph** - a BLUE dot walks the axes while a `TracedPath` draws the parabola in real
   time (the graph grows with the fall, it is not pre-drawn).
4. **Cue `s1.velocity` (~2.5 s)** - GREEN velocity arrow alongside the balls, length `L = L0 * v/v_hit`
   so it stretches as `v = g*t`; readout updates every frame: `t = 0.83 s   y = 16.6 m   v = 8.1 m/s`
   (units always on screen).
5. **Cue `s1.impact` (~7.5 s)** - both balls reach `y = 0 m` on the *same frame*; arrow at full
   length; callout `t = 2.02 s   v = 19.8 m/s - together`, plus `mass does not matter`.
6. Hold ~2 s so the numbers are readable, then end.

Timing note: the real fall is 2.02 s but the drop beat is stretched to ~6 s so the graph and
arrow stay live and readable; the screen shows `slow motion x2.97` so nobody thinks it is real time.

## Palette (one per video)

Background BLACK, text WHITE Monospace, light ball YELLOW, heavy ball ORANGE, graph BLUE,
velocity arrow GREEN, ground/ruler GREY.

## Render plan (aiming for first/second-try success)

- One scene class, no MathTex/LaTeX, no external images, no audio in Manim, no captions in Manim.
- Motion = `f(clock)` via updaters (re-timing safe); `add()` mobjects before attaching updaters.
- Pre-flight: `python .opencode/skills/captions-and-assembly/scripts/captions.py cues <timeline>`
  resolves every cue to a second; scene asserts the sanity check at import-of-construct time.
- Draft `manim -ql`, then `ffmpeg -ss` snapshots at the drop/impact cues into `work/out/`,
  QA that labels+units are on screen and both balls share `y`, then `-qh` final after approval.

## As built (render attempt log)

- **Attempt 1 FAILED** - `Text.move_to((x, y))` needs a 3-vector (`ValueError` broadcast).
  Fixed with a `p2()` helper, and `work/out/layout_check.py` now calls `move_to` on every
  label so this class of error dies before a render.
- **Attempt 2 SUCCEEDED** (`manim -ql`, 157 frames, 10.467 s).
- Pre-render `layout_check.py` also caught 3 labels overflowing the 16:9 frame and they were
  resized/re-centred before attempt 1 - that is why only one render fix was needed.
- `captions.py cues` resolved before rendering: drop 1.5 s, velocity 2.5 s, impact 7.5 s.
- Cue-frame QA (`work/out/qa_*.png`), readout vs closed form:
  - t = 5.00 s video -> `1.18 s, 13.2 m, 11.6 m/s` (predicted 1.178 s, 13.19 m, 11.56 m/s)
  - t = 8.00 s video -> `2.02 s, 0.0 m, 19.8 m/s` (predicted 2.019 s, 0 m, 19.81 m/s)
  - both balls share one y(t), so they leave the release line and reach the ground on the
    same frame; graph curve grows live; green arrow reaches the ground exactly at 19.8 m/s.
- Silent mode: no narration, no burned captions (all teaching text is inside the scene);
  anchors in `timeline.json` words[] exist only so cues resolve.
- Draft output: `video/free-fall-2_draft.mp4` (480p15, `-ql`).

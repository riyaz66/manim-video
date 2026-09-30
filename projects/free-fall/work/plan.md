# Free-fall 20 m — two masses fall together

## Misconception
Heavier balls fall faster. Correction: without air resistance, acceleration is `g` for both, so position/velocity vs time are identical.

## Scene list (single scene `s1`, silent-ready)
- `s1` — left: two balls (1 kg YELLOW, 5 kg ORANGE) drop side-by-side from 20 m platform to ground line. Right-top: live position-time graph `y(t)`. Right-bottom: velocity arrow growing with `v = g·t` + numeric readout with units. Title + axis labels with units on screen.
- Cues (to add after audio/timings): `drop` → both start falling, `impact` → both hit together, `graph` → highlight y-t curve, `velocity` → highlight arrow.

## Palette
- Background BLACK, Text WHITE Monospace, Ball-light YELLOW, Ball-heavy ORANGE, Graph BLUE, Velocity arrow GREEN, Ground GREY.

## Physics sanity check
- `h = 20 m`, `g = 9.81 m/s²`, `v0 = 0`
- `t = √(2h/g) = √(40/9.81) = 2.019 s ≈ 2.02 s`
- `v = g·t = 19.81 m/s ≈ 19.8 m/s` (also `√(2gh)`)
- Mass cancels — both balls share same `y(t) = h - ½·g·t²`.
- Scene asserts `|T-2.019| < 0.02` and `|v-19.81| < 0.1`, else fails.
- First/second-try render: one Scene class, no LaTeX dependency for labels (Text only), pure `f(clock)` motion, no captions inside Manim.

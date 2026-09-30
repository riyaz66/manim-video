# Newton's gravitation - law, scaling, Earth & satellite

Folder: `projects/gravitation` (unique - `Test-Path` was clean; `projects/_template/` does not
exist in this checkout, so `work/`, `work/scenes/`, `work/out/`, `video/` were created by hand).

Mode: **silent** (teacher's choice) - no narration, no burned captions; every teaching line is
on screen. Three Manim scenes, concatenated into one mp4 (precedent: `projectile-range`).

## Misconception

"The gravitational force depends on how big/heavy each object is alone." Correction: it depends
on the **product** `m1*m2` **and** on `1/r^2` of the centre-to-centre separation - and the force
the two masses exert is one **pair**: equal in size, opposite in direction (Newton's 3rd law),
so `F on m1 = F on m2` exactly, whatever `m1 != m2`.

## Scene list (3 scenes, one file `scenes/gravity.py`)

### `s1` GravLaw (~30 s) - state the law and derive it
- Two labelled masses `m1` (YELLOW), `m2` (ORANGE) with a GREY dashed centre-to-centre line
  bracketed and labelled `r` (ruler ticks at both centres so `r` is unmistakably centre-to-centre).
- Derivation chain (MathTex, step-by-step TransformMatchingTex / FadeIn):
  1. `F \propto m_1` and `F \propto m_2`  ->  `F \propto m_1 m_2`
  2. `F \propto \dfrac{1}{r^2}`
  3. combine + define constant `G`  ->  `\boxed{F = G\dfrac{m_1 m_2}{r^2}}`
  4. units of `G`: `\mathrm{N\,m^2\,kg^{-2}}`
- **Equal-and-opposite pair**: two arrows of *identical* length (same RED), one on each mass,
  each pointing at the other, labelled `F on m2` and `F on m1`; highlight line
  `|\vec F_{12}| = |\vec F_{21}|`, `opposite direction`. Arrows are drawn from the mass centres
  along the centre line.

### `s2` Scaling (~30 s) - vary masses, then distance
- **Mass dependence**: baseline `m1, m2, r -> F`; then `2m1 -> 2F`, `3m2 -> 3F`,
  `2m1 and 3m2 -> 6F` (arrow length and a live `F/F0` readout both scale linearly).
- **Distance dependence**: the same pair, second mass slides out `r -> 2r -> 3r` with the
  separation bracket relabelled each time (`r`, `2r`, `3r`) and the force arrow shrinking
  `F -> F/4 -> F/9` (length exactly 1, 1/4, 1/9 of the baseline arrow).
- Closing summary strip: `r, 2r, 3r  ->  F, F/4, F/9` next to a small 1/x^2 curve sketch with
  three marked points.

### `s3` Earth & satellite (~35 s) - apply the law
- **Part A - `g`**: Earth (BLUE) with radius `R = 6.371 x 10^6 m` drawn from centre to surface,
  a small object `m` on the surface, downward force arrow.
  `F = G M m / R^2` and `F = m g`  ->  `g = GM/R^2`  ->
  `g = (6.67e-11 x 5.972e24)/(6.371e6)^2 = ` **`g = 9.81 m/s^2`** (boxed).
- **Part B - satellite**: same law, object at altitude `h = 400 km` (`r = R + h = 6.771 x 10^6 m`),
  circular orbit. Gravity arrow points at Earth's centre and is labelled as the centripetal force:
  `G M m / r^2 = m v^2 / r` -> `v = sqrt(GM/r) = 7.67 km/s`, `T = 2 pi r / v = 92.4 min`
  (ISS check). Satellite orbits live as `f(clock)` on a CYAN orbit circle, gravity arrow always
  pointing to the centre (pure `f(clock)` - no integrator).

Transitions: each scene ends with a `FadeOut` of its content + `hold` ~1 s, and starts from
black; concat is a clean cut at matching black frames (silent - no audio to preserve).

## Physics sanity check (in `physics.json`, asserted in every scene)

- `G = 6.67e-11 N m^2/kg^2` (3 s.f.), `M = 5.972e24 kg`, `R = 6.371e6 m`
  -> `g = GM/R^2 = 9.8136 m/s^2` -> **9.81 m/s^2** (assert `|g - 9.81| < 0.01`).
  *Note for the teacher:* CODATA `G = 6.674e-11` gives `g = 9.8195 -> 9.82`. Since the brief
  pins `g = 9.81`, the plan uses the standard textbook 3-s.f. `G = 6.67e-11`; say the word if
  you prefer CODATA `G` and `g = 9.82` on screen.
- Inverse square: `1/2^2 = 0.25`, `1/3^2 = 1/9 = 0.111111` - asserted exactly, arrow lengths
  drawn from these factors (not eyeballed).
- Mass dependence: force factors are exactly `1, 2, 3, 6` for `m`, `2m`, `3m`, `6m`.
- Third law: both arrows use the *same* length expression, assert `|F12 - F21| == 0`.
- Satellite: `v = sqrt(GM/r) = 7670.0 m/s` -> **7.67 km/s** (tol 5 m/s),
  `T = 2*pi*r/v = 5546.7 s = 92.45 min` -> **92.4 min** (tol 0.2 min).

## Palette (one per video)

Background BLACK, text WHITE Monospace (`Text`) + WHITE `MathTex` for equations,
mass1 YELLOW, mass2 ORANGE, force vectors RED (both arrows share one colour = one pair),
distance/rulers GREY, Earth BLUE, orbit + readouts CYAN, boxed key results GREEN.

## Build & QA

1. LaTeX smoke test first: one `manim -ql` render of a single `MathTex` (MiKTeX package risk).
2. Pre-render `work/out/layout_check.py`: measure every label with real Manim metrics and
   `move_to` it (catches 2-tuple/3-vector bugs + overflow before any render) - per free-fall-2.
3. Draft all three scenes at `-ql` (854x480, 15 fps), then `ffmpeg` QA snapshots into
   `work/out/`: the boxed `F = G m1 m2 / r^2` + both force arrows, the `r/2r/3r` bracket with
   `F/F/4/F/9`, the boxed `g = 9.81 m/s^2`, and a satellite frame.
4. Concat the three mp4s (re-encode, same fps/res) -> `assemble.py` -> `video/gravitation_draft.mp4`.
   Physics asserts fire at render time, so a wrong constant fails loudly instead of rendering.
5. After approval: re-render `-qh` (1920x1080) -> `video/gravitation_final.mp4`. `-qk` 4K only
   if you ask for it.

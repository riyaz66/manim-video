# Projectile range — derive it, chart it, then break it with drag

Mode: **silent** (no narration, no captions). Three Manim scenes, concatenated into one mp4.

## Misconception
"45° always gives the longest range." True only with no air resistance. Once drag is in, the best
angle drops below 45°, and the 30°/60° symmetry breaks.

## Scene list

### `s1` DeriveRange (~20 s) — equation transforms
MathTex chain, `TransformMatchingTex` between steps:
1. `x = v_0\cos\theta\,t`, `y = v_0\sin\theta\,t - \tfrac12 g t^2`
2. eliminate `t` → `y = x\tan\theta - \dfrac{g x^2}{2v_0^2\cos^2\theta}`
3. identity `\dfrac{1}{\cos^2\theta} = 1 + \tan^2\theta` → `y = x\tan\theta - \dfrac{gx^2}{2v_0^2}(1+\tan^2\theta)`
4. land: `y = 0`, divide by `x`, solve → `R = \dfrac{2v_0^2\sin\theta\cos\theta}{g} = \dfrac{v_0^2\sin 2\theta}{g}` (boxed)
5. numbers card: `v₀ = 20 m/s`, `g = 9.81 m/s²` → **R(45°) = 40.8 m**, **R(30°) = R(60°) = 35.3 m**

### `s2` FanAndCurve (~22 s) — trajectories then R(θ)
- Ground line + labelled axes; fan of 5 parabolas at **15°, 30°, 45°, 60°, 75°** drawn in sequence,
  angle labels at launch, landing dots. 45° lands furthest (40.8 m); 30°/60° land together (35.3 m).
- Fan fades out → `R(θ)` plot for θ ∈ [0°, 90°]: closed-form curve, peak marker at 45° = 40.8 m,
  paired markers at 30°/60° = 35.3 m with a "equal ranges" bracket.

### `s3` DragSim (~26 s) — small-step numerical sim
- EOM on screen: `\vec a = -g\,\hat j - k\,|\vec v|\,\vec v` with `k = 0.03 m⁻¹` (quadratic drag);
  step scheme shown as fixed Euler step `Δt = 1 ms` (frame-rate independent, per manim rules).
- Integrator validation: same stepper with `k = 0` lands at 40.77 m vs closed form 40.77 m (assert ≤ 0.1 m).
- Animate 45° launch twice: dashed YELLOW no-drag (40.8 m) vs solid BLUE with drag (22.2 m).
- Overlay `R(θ)` with drag on the dimmed no-drag curve: peak marker at **≈ 40° < 45°**,
  dashed 45° guide line left of it. Note the drag curve is asymmetric (30° → 21.2 m vs 60° → 18.5 m).

## Palette (one per video)
BLACK bg · WHITE Monospace text · YELLOW = no-drag / reference · BLUE = with drag ·
ORANGE = 45° highlight · GREEN = best-angle marker · GREY = axes & ground.

## Physics sanity check (asserted in scenes)
- Closed form, `g = 9.81`, `v₀ = 20`: R(45°) = 40.77 ≈ **40.8** (tol 0.5 m); R(30°) = 35.31 ≈ **35.3**;
  R(60°) = 35.31 ≈ **35.3**.
- No-drag Euler stepper (Δt = 1 ms) reproduces closed form within **0.1 m** at every fan angle.
- Quadratic drag `k = 0.03 m⁻¹` (volleyball/soccer-ball scale, Cd ≈ 0.5): R(45°) → **22.2 m**,
  best angle **40.25° ± 2°**, and R_drag < R_nodrag everywhere.

## Build & QA
1. Smoke-test LaTeX with one `manim -ql` render of `s1` first (MiKTeX may need packages).
2. Draft-render all three at `-ql`; QA snapshots of key frames into `work/out/` (equation steps,
   fan landing dots, drag peak marker). Fix and re-render as needed — expected.
3. Concat the three scene mp4s (ffmpeg, re-encode, same fps/res) → `assemble.py` →
   `video/projectile-range_draft.mp4`.
4. After approval: re-render `-qh` → `video/projectile-range_final.mp4`.

# Mass-spring oscillator - block, live sine graph, period T = pi

Folder: `projects/spring-shm` (unique - `Test-Path` was clean).

## Misconception

"The period depends on how hard/far you pull the block." Correction: for SHM,
`T = 2*pi*sqrt(m/k)` depends only on `m` and `k` - NOT on amplitude. Every cycle on the
traced graph takes the same `T`, whatever the displacement.

## Physics sanity check (in `physics.json`, asserted in the scene)

- `m = 1 kg`, `k = 4 N/m`, frictionless surface, `A = 0.10 m`
- `omega = sqrt(k/m) = sqrt(4) = 2 rad/s` (tol 0.01)
- `T = 2*pi*sqrt(m/k) = 2*pi/omega = pi = 3.14159 s` -> **3.14 s** (tol 0.02 s)
- `f = 1/T = 0.31831 Hz` -> **0.318 Hz** (tol 0.005)
- closed form only: `x(t) = A*cos(omega*t)`, `v(t) = -A*omega*sin(omega*t)` - no integrator,
  so frame rate can never change the period.

## Scene list (single Manim scene `SpringOsc`)

Screen 1920x1080, Monospace `Text` only (no LaTeX - keeps renders safe).

1. **Title + constants banner**: `T = 2*pi*sqrt(m/k) = 3.14 s`,
   `m = 1 kg    k = 4 N/m    omega = sqrt(k/m) = 2 rad/s`.
2. **Top-left: the oscillator** - wall + zigzag spring + block (`m = 1 kg`) sliding on a
   frictionless floor. Dashed equilibrium line `x = 0`, end stops labelled `+0.10 m` /
   `-0.10 m`, spring labelled `k = 4 N/m`. Live readout with units:
   `t = 1.20 s    x = -0.074 m    v = +0.149 m/s`. Block motion starts on the `release` cue.
3. **Cue `s1.watch` (the words "now watch the graph")** - the whole graph panel
   (axes, `t (s)` and `x (m)` labels, equation `x(t) = 0.10*cos(2*t)`) **FadeIns exactly on
   that spoken phrase**, the curve already drawn up to the current instant, then traced
   live by a dot + `TracedPath` as the block keeps moving.
4. **Cue `s1.period` (spoken "three point one four seconds")** - a bracket over exactly one
   cycle of the traced wave labelled `T = 3.14 s`, so the spoken number and the drawn
   period land together.
5. Hold after the narration so the finished graph is readable.

Timing: motion runs in **real time** (no slow-motion cheat) - one cycle really is 3.14 s on
screen, which is the point of the video.

---

## As-built + attempt log (spring-shm)

**Cue wiring** (AssemblyAI word timings, `captions.py cues` resolves all three):
- `s1.release` -> word 28 `"go."` = **10.138 s** (block starts here, graph t = 0)
- `s1.watch`   -> word 35 `"Now"`  = **14.309 s** (graph panel FadeIns on "Now watch the graph.")
- `s1.period`  -> word 55 `"3.14"` = **20.966 s** (bracket + `T = 3.14 s` on the spoken number)

**Audio**: Pocket TTS 23.0 s (5 sentences, 60 tokens) -> AssemblyAI 57 words; transcript
matches `script.txt` verbatim (spoken numbers rendered as digits: `4 newtons`, `3.14 seconds`).

**Render attempts** (pre-render gate: `out/layout_check.py`, physics + all labels + caption band):
1. 2 pre-render import errors caught by the gate (`CYAN` not in `from manim import *`;
   `ManimColor("cyan")` invalid -> `ManimColor("#00FFFF")`).
2. Render 1 OK but QA failed: (a) Manim `wait()` default `frozen_frame=None` froze the first
   long wait and never called updaters -> block/readout static until the first `play()`;
   (b) block `Rectangle` was never centred before `VGroup` -> whole rig offset;
   (c) no tick values (`include_numbers` would need TeX, which fails here -> hand-drawn `Text`).
3. Render 2 fixed (a)-(c); QA found a ~0.4 s gap between pre-drawn curve and trace (dot
   updater attached only after the 0.4 s FadeIn) -> dot/trace now added and attached first.
4. Render 3 clean but the `T = 3.14 s` label crowded the burned-caption band -> graph panel
   lifted (`AX_C.y = -0.65`), bracket moved inside the plot, caption-band guard added to
   `layout_check.py`.
5. **Render 4 = current draft** (480p15, 23.333 s, video > 23.0 s audio).

**QA (from `video/spring-shm_draft.mp4`)**:
| t (s) | frame check | result |
|---|---|---|
| 9.90 | before the release word | block held at `+0.10 m`, `t = 0.00 s`, spring stretched |
| 14.20 | 0.11 s before "Now" | **no graph** |
| 14.55 | during "Now watch the graph." | graph fading in, caption shows that exact phrase |
| 17.50 | mid-trace | `t = 7.37 s  x = -0.057 m  v = -0.165 m/s` vs closed form -0.057 / -0.165 |
| 21.30 | during "which is 3.14 seconds." | bracket over first cycle + `T = 3.14 s`, caption clear of all labels |

Traced wave peaks land at 0, 3.14, 6.28, 9.42 s; readout/formula agreement exact at every
sampled frame; `layout_check.py` reports `LAYOUT OK` (incl. caption-band + wave-band guards).


## Audio / captions

- Mode: **ai_voice** (Pocket TTS, local CPU) - see `work/script.txt`.
- The phrase `Now watch the graph.` is its own sentence in the script, so the cue can point
  at its word id and the graph cannot appear early or late by more than the word timing error.
- Captions are burned by `assemble.py` from `words[]`, i.e. straight from the same text the
  TTS spoke - captions and audio match by construction; optional AssemblyAI pass refines the
  word times (cloud) if the teacher wants frame-exact cue placement.

## Palette

Background BLACK, text WHITE Monospace, block YELLOW, spring GREY, floor/ruler GREY,
graph BLUE, velocity arrow GREEN, cue/period highlight CYAN.

## Render plan (first/second-try safety, learned from free-fall-2)

- Reuse `layout_check.py`: measure every label with real Manim metrics + call `move_to`
  (catches both overflow and 2-tuple/3-vector bugs) BEFORE any render.
- `captions.py cues` resolves every cue to a second before rendering.
- One scene class, `Text` only, motion = `f(clock)`, updaters attached after any FadeIn.
- Draft `-ql` -> cue-frame snapshots -> captions burned -> `video/spring-shm_draft.mp4`.

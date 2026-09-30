# Manim rules for physics videos

- Shared palette constants at the top of each file; one palette per video.
- Monospace `Text` fonts (Manim's Pango renderer kerns proportional fonts badly). Large text - readable on a phone.
- One idea per scene. Leave `wait()` time after each key reveal. Dim context (0.4 opacity), keep the focus at 1.0.
- Label axes, units and vectors. Show numbers with units.
- Use closed-form solutions or a fixed small-step integrator; never let frame rate change the physics.
- Put a sanity check in `physics.json` (e.g. expected range) and assert it in the scene.
- Optional community skills that help with Manim craft (install separately, see SETUP.md): `manimce-best-practices`,
  `manim-composer`. If any of them says to use `add_subcaption`, ignore that here: captions come from timeline.json.

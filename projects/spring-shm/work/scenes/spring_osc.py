"""Mass-spring oscillator: a block oscillates while its sine graph is traced beside it.

The graph panel appears exactly on the spoken cue "Now watch the graph." (word id in
timeline.json), the T bracket appears on the spoken "3.14 seconds."

All numbers come from work/physics.json and are sanity-checked (T = pi = 3.14 s).
Labels live in static_specs()/graph_specs() so work/out/layout_check.py can verify
sizes/positions BEFORE the first render.

Render (from repo root):
  manim -ql --media_dir projects/spring-shm/work/out/media projects/spring-shm/work/scenes/spring_osc.py SpringOsc

Note: waits use frozen_frame=False. With Manim's default (None) it freezes the first long
wait and never calls updaters, so the block/readout would stay frozen until the first play.
"""
import os, sys, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "..", "..", "..", ".opencode", "skills", "manim-physics-scenes", "scripts"))
from sync import Timeline

# Shared palette (one palette per video)
TEXT_C, BLOCK_C, SPRING_C, RIG_C, GRAPH_C = WHITE, YELLOW, GREY, GREY, BLUE
PERIOD_C = ManimColor("#00FFFF")   # cyan

# Layout: 1920x1080 => frame 14.222 x 8.0, x within [-7.111, 7.111], y within [-4, 4]
FLOOR_Y = 1.6                     # floor line
WALL_X = -6.7                     # spring wall
X0 = -4.0                         # equilibrium (x = 0) screen position
A_SCREEN = 1.7                    # screen half-travel for x = +/-A
SPRING_Y = 1.95                   # spring / block centre line
BLOCK_W, BLOCK_H = 0.9, 0.7
MLAB_DY = 0.55                    # "m = 1 kg" sits this far above the block centre
AX_C = (3.1, -0.65)                # graph axes centre (lifted clear of the caption band)
AX_XLEN, AX_YLEN = 6.9, 4.2
T_AXIS_MAX = 14.0                 # graph time axis covers the whole scene
X_TICK_Y = -3.0                   # hand-drawn tick numbers, under the (moved) time axis
BRACKET_Y = -2.55                 # period dimension line, inside the plot under the wave
T_LAB_XOFF = 0.9                  # label sits just right of the bracket arrow
T_LAB_Y = BRACKET_Y
CAPTION_BAND = (-3.56, -3.30)     # burned captions occupy this band, x within +/-1.6


def p2(pos):
    """Label positions are (x, y); Manim needs a 3-vector."""
    return np.array([pos[0], pos[1], 0.0])


def label(txt, size, pos, col):
    return Text(txt, font="Monospace", font_size=size, color=col).move_to(p2(pos))


def static_specs(A):
    """Labels on screen from frame 0: (text, font_size, pos, color, when)."""
    return [
        ("Mass-spring oscillator:  T = 2*pi*sqrt(m/k) = 3.14 s", 26, (0.0, 3.65), TEXT_C, "static"),
        ("m = 1 kg    k = 4 N/m    omega = sqrt(k/m) = 2 rad/s", 22, (0.0, 3.3), RIG_C, "static"),
        ("k = 4 N/m", 20, (-6.0, 2.9), TEXT_C, "static"),
        ("m = 1 kg", 20, (X0, SPRING_Y + MLAB_DY), BLOCK_C, "block"),
        (f"-{A:.2f} m", 18, (X0 - A_SCREEN, 0.85), RIG_C, "static"),
        ("x = 0", 18, (X0, 0.85), RIG_C, "static"),
        (f"+{A:.2f} m", 18, (X0 + A_SCREEN, 0.85), RIG_C, "static"),
        (f"t = 0.00 s    x = +{A:.3f} m", 20, (-4.0, 0.3), TEXT_C, "readout"),
        ("v = +0.000 m/s", 20, (-4.0, -0.1), TEXT_C, "readout"),
        ("t counts from the release", 18, (-4.0, -0.5), RIG_C, "static"),
    ]


def graph_specs(axes, T):
    """Labels that appear with the graph (or with the spoken period). Built from the real
    axes object so the layout check measures exactly what the scene draws."""
    specs = [
        ("x (m)", 20, (axes.c2p(0, 0)[0], 1.7), TEXT_C, "graph"),
        ("t (s)", 20, (6.6, -3.35), TEXT_C, "graph"),
        ("x(t) = 0.10*cos(2*t)", 20, (AX_C[0], 1.7), GRAPH_C, "graph"),
        (f"T = {T:.2f} s", 20, (axes.c2p(T, 0)[0] + T_LAB_XOFF, T_LAB_Y), PERIOD_C, "period"),
    ]
    for v in range(0, int(T_AXIS_MAX) + 1, 2):                      # time tick numbers
        specs.append((f"{v}", 18, (axes.c2p(v, 0)[0], X_TICK_Y), TEXT_C, "graph"))
    for v in (-0.10, -0.05, 0.00, 0.05, 0.10):                      # displacement tick numbers
        specs.append((f"{v:.2f}", 18, (axes.c2p(0, v)[0] - 0.5, axes.c2p(0, v)[1]), TEXT_C, "graph"))
    return specs


def wait_live(scene, t):
    """Wait until scene clock t, forcing updaters to run (see module docstring)."""
    gap = t - scene.renderer.time
    if gap > 1e-3:
        scene.wait(gap, frozen_frame=False)


class SpringOsc(Scene):
    def construct(self):
        tl = Timeline(os.path.join(PROJECT, "timeline.json"))
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        k = float(phys["constants"]["k_Npm"])
        m = float(phys["scenario"]["m_kg"])
        A = float(phys["scenario"]["amplitude_m"])

        # closed form: omega = sqrt(k/m), T = 2*pi*sqrt(m/k)  (assert vs physics.json)
        w = float(np.sqrt(k / m))
        T = float(2.0 * np.pi / w)
        exp = phys["sanity_check"]
        assert abs(T - exp["expected_period_s"]) <= exp["period_tolerance_s"], \
            f"period {T:.4f} s disagrees with physics.json sanity check"
        assert abs(w - exp["expected_omega_radps"]) <= exp["omega_tolerance_radps"], \
            f"omega {w:.4f} rad/s disagrees with physics.json sanity check"
        assert abs(1.0 / T - exp["expected_freq_hz"]) <= exp["freq_tolerance_hz"], \
            f"frequency {1/T:.4f} Hz disagrees with physics.json sanity check"

        t_release = tl.cue("s1.release")     # narration: "let go."
        t_watch = tl.cue("s1.watch")         # narration: "Now watch the graph."
        t_period = tl.cue("s1.period")       # narration: "3.14 seconds."

        # physics time counts from the release: one pure function drives block, graph, readout
        def tau(clock):
            return max(0.0, clock - t_release)

        def x_of(t_):
            return A * np.cos(w * t_)

        def v_of(t_):
            return -A * w * np.sin(w * t_)

        def x_screen(t_):
            return X0 + (x_of(t_) / A) * A_SCREEN

        # ---- static rig ---------------------------------------------------------
        wall = Line([WALL_X, SPRING_Y - 0.55, 0], [WALL_X, SPRING_Y + 0.55, 0],
                    color=RIG_C, stroke_width=7)
        floor = Line([WALL_X, FLOOR_Y, 0], [-1.0, FLOOR_Y, 0], color=RIG_C, stroke_width=5)
        marks = VGroup(*[
            DashedLine([mx, FLOOR_Y, 0], [mx, FLOOR_Y - 0.5, 0], color=RIG_C, stroke_width=3)
            for mx in (X0 - A_SCREEN, X0, X0 + A_SCREEN)
        ])
        self.add(wall, floor, marks)

        # ---- static labels ------------------------------------------------------
        specs = static_specs(A)
        for txt, size, pos, col, when in specs:
            if when == "static":
                self.add(label(txt, size, pos, col))
        rd1 = next(s for s in specs if s[4] == "readout" and s[0].startswith("t ="))
        rd2 = next(s for s in specs if s[4] == "readout" and s[0].startswith("v"))
        blk = next(s for s in specs if s[4] == "block")

        # ---- block: children positioned individually (group-centring would drift) --
        body = Rectangle(width=BLOCK_W, height=BLOCK_H, color=BLOCK_C,
                         fill_color=BLOCK_C, fill_opacity=1.0, stroke_width=2)
        body.move_to([x_screen(0.0), SPRING_Y, 0])
        mlab = label(blk[0], blk[1], (x_screen(0.0), SPRING_Y + MLAB_DY), blk[3])
        block = VGroup(body, mlab)
        self.add(block)

        def upd_block(g):
            bx = x_screen(tau(self.renderer.time))
            g[0].move_to([bx, SPRING_Y, 0])
            g[1].move_to([bx, SPRING_Y + MLAB_DY, 0])
        block.add_updater(upd_block)

        # ---- spring (zigzag recomputed from the clock) --------------------------
        spring = VMobject(color=SPRING_C, stroke_width=5)
        self.add(spring)

        def zigzag(x0, x1, y, coils=9, amp=0.17):
            L = x1 - x0
            lead = max(0.08, 0.10 * L)
            pts = [np.array([x0, y, 0.0]), np.array([x0 + lead, y, 0.0])]
            n = 2 * coils
            for i in range(1, n + 1):
                xx = x0 + lead + (L - 2 * lead) * i / n
                pts.append(np.array([xx, y + (amp if i % 2 else -amp), 0.0]))
            pts.append(np.array([x1 - lead, y, 0.0]))
            pts.append(np.array([x1, y, 0.0]))
            return pts

        spring.add_updater(lambda s: s.set_points_as_corners(
            zigzag(WALL_X, x_screen(tau(self.renderer.time)) - BLOCK_W / 2, SPRING_Y)))

        # ---- live readout (units always on screen) ------------------------------
        r1 = label(rd1[0], rd1[1], rd1[2], rd1[3])
        r2 = label(rd2[0], rd2[1], rd2[2], rd2[3])
        self.add(r1, r2)

        def upd_r1(m):
            t_ = tau(self.renderer.time)
            m.become(Text(f"t = {t_:.2f} s    x = {x_of(t_):+.3f} m",
                          font="Monospace", font_size=rd1[1], color=rd1[3]).move_to(p2(rd1[2])))
        def upd_r2(m):
            t_ = tau(self.renderer.time)
            m.become(Text(f"v = {v_of(t_):+.3f} m/s",
                          font="Monospace", font_size=rd2[1], color=rd2[3]).move_to(p2(rd2[2])))
        r1.add_updater(upd_r1)
        r2.add_updater(upd_r2)

        # ---- block is held until the release cue, then oscillates ---------------
        wait_live(self, t_watch)

        # ---- the graph appears exactly on "Now watch the graph." ----------------
        tau_now = tau(self.renderer.time)
        axes = Axes(x_range=[0, T_AXIS_MAX, 2], y_range=[-0.13, 0.13, 0.05],
                    x_length=AX_XLEN, y_length=AX_YLEN,
                    axis_config={"include_tip": False, "font_size": 20},
                    ).move_to([AX_C[0], AX_C[1], 0])
        # time axis drawn along the bottom of the plot (x = 0 stays a dashed zero line)
        axes.x_axis.shift(DOWN * (axes.c2p(0, 0)[1] - axes.c2p(0, -0.13)[1]))

        gspecs = graph_specs(axes, T)
        glabels = VGroup(*[label(s[0], s[1], s[2], s[3]) for s in gspecs if s[4] == "graph"])
        zero = DashedLine(axes.c2p(0, 0), axes.c2p(T_AXIS_MAX, 0),
                          color=RIG_C, stroke_width=2).set_opacity(0.5)
        history = axes.plot(lambda t: A * np.cos(w * t), x_range=[0.0, tau_now],
                            color=GRAPH_C, stroke_width=5)
        dot = Dot(axes.c2p(tau_now, x_of(tau_now)), color=GRAPH_C, radius=0.11)
        # dot + trace must run DURING the panel FadeIn, otherwise ~0.4 s of wave is
        # missing between the pre-drawn history and where the trace starts.
        trace = TracedPath(dot.get_center, stroke_color=GRAPH_C, stroke_width=5)
        dot.add_updater(lambda d: d.move_to(
            axes.c2p(tau(self.renderer.time), x_of(tau(self.renderer.time)))))
        graph_group = VGroup(axes, glabels, zero, history)
        self.add(trace, dot)

        self.play(FadeIn(graph_group), run_time=0.4)

        # ---- the period bracket appears on the spoken "3.14 seconds." ------------
        wait_live(self, t_period)
        bracket = DoubleArrow([axes.c2p(0, 0)[0], BRACKET_Y, 0], [axes.c2p(T, 0)[0], BRACKET_Y, 0],
                              buff=0, color=PERIOD_C, stroke_width=5, max_tip_length_to_length_ratio=0.08)
        per_spec = next(s for s in gspecs if s[4] == "period")
        per_lab = label(per_spec[0], per_spec[1], per_spec[2], per_spec[3])
        self.play(FadeIn(bracket), FadeIn(per_lab), run_time=0.4)

        wait_live(self, max(tl.end_time() + 1.0, tl.end_time()))

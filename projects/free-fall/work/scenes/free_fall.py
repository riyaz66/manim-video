"""Free-fall 20 m: two masses fall together, with live y-t graph and velocity arrow.
Render draft from repo root:
  manim -ql --media_dir projects/free-fall/work/out/media projects/free-fall/work/scenes/free_fall.py FreeFall
"""
import os, sys, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "..", "..", "..", ".opencode", "skills", "manim-physics-scenes", "scripts"))
import os, sys, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "..", "..", "..", ".opencode", "skills", "manim-physics-scenes", "scripts"))
from sync import Timeline

# Shared palette (one palette per video)
BALL_LIGHT, BALL_HEAVY, GRAPH_C, VEL_C, TEXT_C, GROUND_C = YELLOW, ORANGE, BLUE, GREEN, WHITE, GRAY

class FreeFall(Scene):
    def construct(self):
        tl = Timeline(os.path.join(PROJECT, "timeline.json"))
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = float(phys["constants"]["g"])
        h = float(phys["scenario"]["h_m"])
        T = float(np.sqrt(2.0 * h / g))
        v_hit = g * T
        exp = phys["sanity_check"]
        assert abs(T - exp["expected_fall_time_s"]) <= exp["fall_time_tolerance_s"] + 0.02, f"T {T:.3f}s disagrees"
        assert abs(v_hit - exp["expected_impact_speed_mps"]) <= exp["impact_speed_tolerance_mps"] + 0.1, f"v {v_hit:.2f} disagrees"

        t_drop = tl.cue("s1.drop")
        t_graph = tl.cue("s1.graph")
        t_vel = tl.cue("s1.velocity")
        t_impact = tl.cue("s1.impact")

        # Title + labels with units (Text only, no LaTeX for first-try render)
        title = Text("Two balls fall together: h = 20 m", font="Monospace", font_size=30, color=TEXT_C).to_edge(UP, buff=0.3)
        self.add(title)

        # Left rig coordinates
        ground_y, top_y = -2.8, 1.8
        x_light, x_heavy = -5.0, -3.8
        ground = Line([-6.2, ground_y, 0], [-2.6, ground_y, 0], color=GROUND_C, stroke_width=6)
        platform = Line([-6.2, top_y, 0], [-2.6, top_y, 0], color=GROUND_C, stroke_width=4)
        glabel = Text("ground (y = 0 m)", font="Monospace", font_size=20, color=TEXT_C).next_to(ground, DOWN, buff=0.1)
        hlabel = Text("drop: y = 20 m", font="Monospace", font_size=20, color=TEXT_C).next_to(platform, UP, buff=0.1)
        mlabel = Text("1 kg      5 kg", font="Monospace", font_size=20, color=TEXT_C).move_to([-4.4, top_y + 0.65, 0])
        self.add(ground, platform, glabel, hlabel, mlabel)

        def y_screen(y_phys):
            frac = max(0.0, min(y_phys / h, 1.0))
            return ground_y + frac * (top_y - ground_y)

        # Slow-motion stretch: 2.02 s physics spans drop->impact narration (~11 s video)
        # so graph + arrow stay live instead of freezing after 5 s.
        T_video = max(t_impact - t_drop, 0.5)
        slow = T / T_video
        slow_label = Text(f"slow motion x{slow:.2f}", font="Monospace", font_size=20, color=TEXT_C).move_to([-4.4, 0.2, 0])
        self.add(slow_label)

        def tau_phys(clock):
            frac = (clock - t_drop) / T_video
            return max(0.0, min(frac, 1.0)) * T

        def y_phys_at(tau):
            tau = max(0.0, min(tau, T))
            return h - 0.5 * g * tau ** 2

        def v_at(tau):
            return g * max(0.0, min(tau, T))

        ball_l = Dot([x_light, y_screen(h), 0], color=BALL_LIGHT, radius=0.18)
        ball_h = Dot([x_heavy, y_screen(h), 0], color=BALL_HEAVY, radius=0.28)
        ball_l.add_updater(lambda m: m.move_to([x_light, y_screen(y_phys_at(tau_phys(self.renderer.time))), 0]))
        ball_h.add_updater(lambda m: m.move_to([x_heavy, y_screen(y_phys_at(tau_phys(self.renderer.time))), 0]))
        self.add(ball_l, ball_h)

        # Right-top y-t graph
        axes = Axes(
            x_range=[0, T + 1.0, 1.0], y_range=[0, 20, 10],
            x_length=5.2, y_length=2.6,
            axis_config={"include_tip": False, "font_size": 18},
        ).move_to([2.8, 1.2, 0])
        axes_labels = Text("t (s) vs y (m)", font="Monospace", font_size=20, color=TEXT_C).next_to(axes, UP, buff=0.15)
        curve = axes.plot(lambda t: max(h - 0.5 * g * t * t, 0.0), x_range=[0, T], color=GRAPH_C, stroke_width=4)
        gdot = Dot(color=GRAPH_C, radius=0.1)
        gdot.add_updater(lambda m: m.move_to(axes.c2p(
            tau_phys(self.renderer.time),
            y_phys_at(tau_phys(self.renderer.time)),
        )))
        self.add(axes, axes_labels, curve, gdot)

        # Right-bottom velocity arrow + readout
        tl.wait_until(self, t_vel)
        arrow_base = np.array([1.2, -2.4, 0])
        arrow = Arrow(ORIGIN, RIGHT * 0.1, buff=0, color=VEL_C, stroke_width=8)
        arrow.put_start_and_end_on(arrow_base, arrow_base + RIGHT * 0.15)
        vlabel = Text("v arrow (m/s)", font="Monospace", font_size=20, color=VEL_C).move_to([3.4, -1.6, 0])
        readout = Text("v = 0.0 m/s  t = 0.00 s", font="Monospace", font_size=22, color=TEXT_C)
        readout.move_to([3.0, -2.9, 0])
        self.play(FadeIn(arrow), FadeIn(vlabel), FadeIn(readout), run_time=0.4)
        def upd_arrow(m):
            v = v_at(tau_phys(self.renderer.time))
            length = 0.15 + (v / v_hit) * 2.6
            m.put_start_and_end_on(arrow_base, arrow_base + RIGHT * length)
        def upd_readout(m):
            tau = tau_phys(self.renderer.time)
            m.become(Text(f"v = {v_at(tau):.1f} m/s  t = {tau:.2f} s", font="Monospace", font_size=22, color=TEXT_C).move_to([3.0, -2.9, 0]))
        arrow.add_updater(upd_arrow)
        readout.add_updater(upd_readout)

        tl.wait_until(self, t_impact + 0.2)
        hit = Text("hit together", font="Monospace", font_size=24, color=TEXT_C).move_to([-4.4, ground_y - 0.9, 0])
        self.play(FadeIn(hit), run_time=0.3)

        tl.wait_until(self, tl.end_time() + 0.5)

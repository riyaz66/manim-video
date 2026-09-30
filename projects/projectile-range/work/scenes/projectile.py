"""Example: projectile motion, synced to timeline.json cues.
Copy to projects/<name>/work/scenes/ and render a draft from the repo root:
  manim -ql --media_dir projects/<name>/work/out/media projects/<name>/work/scenes/projectile.py Projectile
Not run in the authoring environment - render one draft and fix anything Manim reports.
"""
import os, sys, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "..", "..", "..", ".opencode", "skills", "manim-physics-scenes", "scripts"))
from sync import Timeline

# Shared palette (one palette per video)
BALL, VX, TEXT_C = YELLOW, BLUE, WHITE

class Projectile(Scene):
    def construct(self):
        tl = Timeline(os.path.join(PROJECT, "timeline.json"))
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = phys["constants"]["g"]; v0 = phys["scenario"]["v0"]; a = np.radians(phys["scenario"]["angle_deg"])
        vx, vy = v0 * np.cos(a), v0 * np.sin(a)
        T = 2 * vy / g                                   # flight time
        R = vx * T                                       # range (checked against physics.json sanity_check)
        exp = phys["sanity_check"]
        assert abs(R - exp["expected_range_m"]) <= exp["tolerance_m"], f"range {R:.1f} m disagrees with sanity check"

        axes = Axes(x_range=[0, 45, 5], y_range=[0, 12, 2], x_length=11, y_length=4.5,
                    axis_config={"include_tip": False, "font_size": 22}).to_edge(DOWN, buff=0.6)
        xlab = Text("distance (m)", font="Monospace", font_size=22).next_to(axes, DOWN, buff=0.15)
        title = Text(f"v0 = {v0:g} m/s at {phys['scenario']['angle_deg']:g} deg", font="Monospace", font_size=28).to_edge(UP)
        self.add(axes, xlab, title)

        t_launch = tl.cue("s1.launch")
        t_vx = tl.cue("s1.show_vx")

        def pos(tau):                                    # position as a pure function of time since launch
            tau = max(0.0, min(tau, T))
            return axes.c2p(vx * tau, vy * tau - 0.5 * g * tau ** 2)

        ball = Dot(pos(0), color=BALL, radius=0.12)
        ball.add_updater(lambda m: m.move_to(pos(self.renderer.time - t_launch)))
        trail = TracedPath(ball.get_center, stroke_color=BALL, stroke_width=3)
        self.add(trail, ball)

        tl.wait_until(self, t_vx)
        arrow = Arrow(ORIGIN, RIGHT, buff=0, color=VX)
        arrow.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + RIGHT * vx * 0.12))
        label = Text("vx stays constant", font="Monospace", font_size=24, color=VX).to_edge(RIGHT).shift(UP * 1.5)
        self.play(FadeIn(arrow), FadeIn(label), run_time=0.4)

        tl.wait_until(self, max(t_launch + T + 1.0, tl.end_time() + 0.5))

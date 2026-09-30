"""Scene 2 of 3: fan of trajectories 15-75 deg, then range vs angle.
Render (from repo root):
  manim -ql --media_dir projects/projectile-range/work/out/media projects/projectile-range/work/scenes/fan_curve.py FanAndCurve
"""
import os, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

# Shared palette (one palette per video)
TXT, REF, DRAG_C, HILITE, BEST, AX = WHITE, YELLOW, BLUE, ORANGE, GREEN, GREY

FAN = (15, 30, 45, 60, 75)


class FanAndCurve(Scene):
    def construct(self):
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = phys["constants"]["g"]; v0 = phys["scenario"]["v0"]; sc = phys["sanity_check"]

        def rng(deg):
            return v0 ** 2 * np.sin(2 * np.radians(deg)) / g

        # Physics sanity check - the fan must reproduce the closed-form targets
        assert abs(rng(45) - sc["expected_range_45_m"]) <= sc["tolerance_m"], f"R(45) = {rng(45):.2f} m"
        assert abs(rng(30) - sc["expected_range_30_m"]) <= sc["tolerance_m"], f"R(30) = {rng(30):.2f} m"
        assert abs(rng(60) - sc["expected_range_60_m"]) <= sc["tolerance_m"], f"R(60) = {rng(60):.2f} m"
        assert abs(rng(30) - rng(60)) < 0.05, "30 and 60 deg must land together"

        # ---------------- part 1: fan of trajectories ----------------
        title1 = Text("Five angles, one speed", font="Monospace", font_size=38, color=TXT).to_edge(UP, buff=0.3)
        sub1 = MathTex(r"v_0 = 20\ \text{m/s}", font_size=32, color=AX).next_to(title1, DOWN, buff=0.2)
        axes1 = Axes(x_range=[0, 46, 10], y_range=[0, 21, 5], x_length=11.5, y_length=4.6,
                     axis_config={"font_size": 20, "include_numbers": True}, tips=None).to_edge(DOWN, buff=0.55)
        xlab1 = Text("distance (m)", font="Monospace", font_size=24).next_to(axes1, DOWN, buff=0.2)
        ylab1 = Text("height (m)", font="Monospace", font_size=24).rotate(PI / 2).next_to(axes1, LEFT, buff=0.3)
        self.play(FadeIn(title1), FadeIn(sub1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(axes1, shift=UP * 0.2), FadeIn(xlab1), FadeIn(ylab1), run_time=0.7)

        colors = {15: AX, 30: REF, 45: HILITE, 60: REF, 75: AX}
        # angle labels: above each apex (15 deg sits above its descending leg instead)
        label_pos = {15: (14.0, 2.9), 30: (17.65, 6.6), 45: (20.4, 11.6),
                     60: (17.65, 16.8), 75: (10.2, 20.3)}
        fan_mobs = [title1, sub1, axes1, xlab1, ylab1]

        def traj(deg, n=400):
            a = np.radians(deg)
            vx, vy = v0 * np.cos(a), v0 * np.sin(a)
            T = 2 * vy / g
            ts = np.linspace(0, T, n)
            return [axes1.c2p(float(vx * t), float(vy * t - 0.5 * g * t * t)) for t in ts]

        for deg in FAN:
            curve = VMobject(stroke_color=colors[deg], stroke_width=6 if deg == 45 else 4)
            curve.set_points_as_corners(traj(deg))
            albl = Text(f"{deg} deg", font="Monospace", font_size=20, color=colors[deg])
            albl.move_to(axes1.c2p(*label_pos[deg]))
            self.play(Create(curve), FadeIn(albl, shift=UP * 0.12), run_time=0.85)
            self.wait(0.3)
            fan_mobs.append(curve)
            fan_mobs.append(albl)

        # landing dots + summary (30/60 land together, as do 15/75)
        lands = VGroup()
        for deg in FAN:
            lands.add(Dot(axes1.c2p(rng(deg), 0), color=colors[deg], radius=0.09))
        self.play(*[FadeIn(d, scale=1.6) for d in lands], run_time=0.6)

        summary = VGroup(
            MathTex(rf"R(45^\circ) = {rng(45):.1f}\ \text{{m}}", font_size=32, color=HILITE),
            MathTex(rf"R(30^\circ) = R(60^\circ) = {rng(30):.1f}\ \text{{m}}", font_size=32, color=REF),
            MathTex(rf"R(15^\circ) = R(75^\circ) = {rng(15):.1f}\ \text{{m}}", font_size=32, color=AX),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(axes1.c2p(44, 17.5), aligned_edge=RIGHT)
        self.play(FadeIn(summary, shift=LEFT * 0.3), run_time=0.7)
        fan_mobs.append(lands)
        fan_mobs.append(summary)
        self.wait(2.0)

        # ---------------- part 2: range vs angle ----------------
        self.play(*[FadeOut(m) for m in fan_mobs], run_time=0.7)

        title2 = Text("Range vs launch angle", font="Monospace", font_size=38, color=TXT).to_edge(UP, buff=0.3)
        sub2 = Text("no air resistance", font="Monospace", font_size=24, color=AX).next_to(title2, DOWN, buff=0.22)
        axes2 = Axes(x_range=[0, 90, 15], y_range=[0, 45, 5], x_length=11.5, y_length=4.6,
                     axis_config={"font_size": 20, "include_numbers": True}, tips=None).to_edge(DOWN, buff=0.55)
        xlab2 = Text("launch angle (deg)", font="Monospace", font_size=24).next_to(axes2, DOWN, buff=0.2)
        ylab2 = Text("range R (m)", font="Monospace", font_size=24).rotate(PI / 2).next_to(axes2, LEFT, buff=0.3)
        self.play(FadeIn(title2), FadeIn(sub2, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(axes2, shift=UP * 0.2), FadeIn(xlab2), FadeIn(ylab2), run_time=0.7)

        curve = axes2.plot(lambda d: v0 ** 2 * np.sin(2 * np.radians(d)) / g,
                           x_range=[0, 90], color=REF, stroke_width=5)
        self.play(Create(curve), run_time=1.7)

        d45 = Dot(axes2.c2p(45, rng(45)), color=HILITE, radius=0.1)
        l45 = MathTex(rf"45^\circ \to {rng(45):.1f}\ \text{{m}}", font_size=34,
                      color=HILITE).next_to(d45, UP, buff=0.2)
        self.play(FadeIn(d45, scale=1.6), FadeIn(l45, shift=UP * 0.2), run_time=0.7)

        d30 = Dot(axes2.c2p(30, rng(30)), color=REF, radius=0.09)
        d60 = Dot(axes2.c2p(60, rng(60)), color=REF, radius=0.09)
        pair = DashedLine(axes2.c2p(30, rng(30)), axes2.c2p(60, rng(60)),
                          color=REF, stroke_width=3, dash_length=0.12)
        l3060 = MathTex(rf"R(30^\circ) = R(60^\circ) = {rng(30):.1f}\ \text{{m}}",
                        font_size=34, color=REF).move_to(axes2.c2p(45, 28))
        self.play(FadeIn(d30, scale=1.6), FadeIn(d60, scale=1.6), Create(pair), run_time=0.8)
        self.play(FadeIn(l3060, shift=UP * 0.2), run_time=0.6)
        self.wait(2.2)

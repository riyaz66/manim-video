"""Scene 1 of 3: derive R = v0^2 sin(2 theta)/g with equation transforms.
Render (from repo root):
  manim -ql --media_dir projects/projectile-range/work/out/media projects/projectile-range/work/scenes/derive_range.py DeriveRange
"""
import os, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

# Shared palette (one palette per video)
TXT, REF, DRAG_C, HILITE, BEST, AX = WHITE, YELLOW, BLUE, ORANGE, GREEN, GREY


class DeriveRange(Scene):
    def construct(self):
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = phys["constants"]["g"]; v0 = phys["scenario"]["v0"]; sc = phys["sanity_check"]

        def rng(deg):
            return v0 ** 2 * np.sin(2 * np.radians(deg)) / g

        r45, r30, r60 = rng(45), rng(30), rng(60)
        # Physics sanity check - fail the render if the numbers disagree with physics.json
        assert abs(r45 - sc["expected_range_45_m"]) <= sc["tolerance_m"], f"R(45) = {r45:.2f} m"
        assert abs(r30 - sc["expected_range_30_m"]) <= sc["tolerance_m"], f"R(30) = {r30:.2f} m"
        assert abs(r60 - sc["expected_range_60_m"]) <= sc["tolerance_m"], f"R(60) = {r60:.2f} m"

        title = Text("Range of a projectile", font="Monospace", font_size=40, color=TXT).to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.7)

        slot = UP * 1.15
        eqs = [
            MathTex(r"x = v_0\cos\theta\,t", r",\qquad", r"y = v_0\sin\theta\,t - \tfrac12 g t^2"),
            MathTex(r"y = v_0\sin\theta\left(\frac{x}{v_0\cos\theta}\right)", "-",
                    r"\frac12 g\left(\frac{x}{v_0\cos\theta}\right)^2"),
            MathTex(r"y = x\tan\theta", "-", r"\frac{g x^2}{2v_0^2\cos^2\theta}"),
            MathTex(r"y = x\tan\theta", "-", r"\frac{g x^2}{2v_0^2}", r"\left(1 + \tan^2\theta\right)"),
            MathTex(r"\tan\theta", "=", r"\frac{g x}{2v_0^2}", r"\left(1 + \tan^2\theta\right)"),
            MathTex(r"x = \frac{2v_0^2}{g}", r"\cdot", r"\frac{\tan\theta}{1 + \tan^2\theta}"),
            MathTex(r"x = \frac{2v_0^2}{g}", r"\sin\theta\cos\theta"),
            MathTex(r"R = \frac{v_0^2\sin 2\theta}{g}"),
        ]
        labels = [
            "parametric motion",
            "t = x / (v0 cos theta)",
            "simplify",
            "use 1/cos^2 = 1 + tan^2",
            "land:  y = 0,  x > 0",
            "solve for x",
            "tan / (1 + tan^2) = sin cos",
            "R = x,  2 sinA cosA = sin 2A",
        ]

        eq = eqs[0].move_to(slot)
        step_lbl = Text(labels[0], font="Monospace", font_size=22, color=AX).next_to(eq, DOWN, buff=0.5)
        self.play(Write(eq), FadeIn(step_lbl, shift=UP * 0.15), run_time=1.0)
        self.wait(1.2)

        for nxt, lab in zip(eqs[1:], labels[1:]):
            self.play(FadeOut(step_lbl), run_time=0.25)
            nxt = nxt.move_to(slot)
            self.play(TransformMatchingTex(eq, nxt), run_time=1.05)
            eq = nxt
            step_lbl = Text(lab, font="Monospace", font_size=22, color=AX).next_to(eq, DOWN, buff=0.5)
            self.play(FadeIn(step_lbl, shift=UP * 0.15), run_time=0.35)
            self.wait(0.75)

        box = SurroundingRectangle(eq, color=HILITE, buff=0.2)
        self.play(Create(box), run_time=0.7)
        self.wait(1.1)
        self.play(FadeOut(step_lbl), run_time=0.3)

        nums = VGroup(
            MathTex(rf"v_0 = {v0:g}\ \text{{m/s}},\qquad g = {g:g}\ \text{{m/s}}^2",
                    font_size=34, color=AX),
            MathTex(rf"R(45^\circ) = {r45:.1f}\ \text{{m}}", font_size=42, color=HILITE),
            MathTex(rf"R(30^\circ) = R(60^\circ) = {r30:.1f}\ \text{{m}}", font_size=42, color=REF),
        ).arrange(DOWN, buff=0.35).next_to(eq, DOWN, buff=0.6)

        self.play(FadeIn(nums[0], shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(nums[1], shift=UP * 0.2), run_time=0.5)
        self.wait(0.7)
        self.play(FadeIn(nums[2], shift=UP * 0.2), run_time=0.5)
        self.wait(1.8)

"""Scene 3 of 3: air drag, small-step numerical simulation, best angle < 45 deg.
Render (from repo root):
  manim -ql --media_dir projects/projectile-range/work/out/media projects/projectile-range/work/scenes/drag_sim.py DragSim
"""
import os, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

# Shared palette (one palette per video)
TXT, REF, DRAG_C, HILITE, BEST, AX = WHITE, YELLOW, BLUE, ORANGE, GREEN, GREY


class DragSim(Scene):
    def construct(self):
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = phys["constants"]["g"]; v0 = phys["scenario"]["v0"]; sc = phys["sanity_check"]
        k = phys["drag"]["k_per_m"]; dt = phys["drag"]["dt_s"]

        def rng(deg):
            return v0 ** 2 * np.sin(2 * np.radians(deg)) / g

        def sim(deg, k_val):
            """Fixed small-step Euler integration. Returns [(x, y), ...], last point on y = 0."""
            a = np.radians(deg)
            x = y = t = 0.0
            vx, vy = v0 * np.cos(a), v0 * np.sin(a)
            pts = [(0.0, 0.0)]
            while t < 60.0:
                v = np.hypot(vx, vy)
                vx += (-k_val * v * vx) * dt
                vy += (-g - k_val * v * vy) * dt
                x += vx * dt; y += vy * dt; t += dt
                if y < 0.0:
                    px, py = pts[-1]
                    f = py / (py - y)
                    pts.append((px + (x - px) * f, 0.0))
                    break
                pts.append((x, y))
            return pts

        # ---- physics sanity checks: validate the stepper before trusting it ----
        R_k0 = sim(45, 0.0)[-1][0]
        assert abs(R_k0 - rng(45)) <= sc["integrator_tolerance_m"], \
            f"stepper k=0 gives {R_k0:.2f} m vs closed form {rng(45):.2f} m"
        R_d45 = sim(45, k)[-1][0]
        assert abs(R_d45 - sc["drag_range_45_m"]) <= 0.5, f"drag R(45) = {R_d45:.2f} m"

        grid = np.arange(0.0, 90.5, 1.0)
        drag_ranges = [sim(d, k)[-1][0] for d in grid]
        bi = int(np.argmax(drag_ranges))
        best, Rbest = grid[bi], drag_ranges[bi]
        assert abs(best - sc["drag_best_angle_deg"]) <= sc["drag_best_angle_tol_deg"], \
            f"best angle = {best} deg"
        assert best < 45, "air drag must push the best angle below 45 deg"
        for d in (20, 30, 45, 60, 70):
            assert sim(d, k)[-1][0] < rng(d), f"drag range must be shorter at {d} deg"

        # ---------------- part A: the model ----------------
        title = Text("Air drag", font="Monospace", font_size=40, color=TXT).to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.7)

        eom = MathTex(r"\vec{a} = -g\,\hat{j} - k\,|\vec{v}|\,\vec{v}", font_size=48).move_to(UP * 1.6)
        kline = MathTex(rf"k = {k:g}\ \text{{m}}^{{-1}}", font_size=36, color=DRAG_C).next_to(eom, DOWN, buff=0.5)
        scheme = VGroup(
            MathTex(r"\vec{v}_{n+1} = \vec{v}_n + \vec{a}_n\,\Delta t", font_size=34),
            MathTex(r"\vec{x}_{n+1} = \vec{x}_n + \vec{v}_n\,\Delta t", font_size=34),
            MathTex(r"\Delta t = 1\ \text{ms}", font_size=34, color=REF),
        ).arrange(DOWN, buff=0.3).next_to(kline, DOWN, buff=0.6)
        note = Text("fixed small steps - the physics never depends on the frame rate",
                    font="Monospace", font_size=22, color=AX).to_edge(DOWN, buff=0.35)

        self.play(Write(eom), run_time=1.0)
        self.play(FadeIn(kline, shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(scheme, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(note, shift=UP * 0.15), run_time=0.5)
        self.wait(2.2)
        self.play(*[FadeOut(m) for m in (eom, kline, scheme, note)], run_time=0.6)

        # ---------------- part B: 45 deg launch, drag vs no drag ----------------
        sub = Text("45 deg launch: same stepper, k = 0 vs k = 0.03",
                   font="Monospace", font_size=26, color=AX).next_to(title, DOWN, buff=0.25)
        axes1 = Axes(x_range=[0, 46, 10], y_range=[0, 12, 3], x_length=11.5, y_length=4.6,
                     axis_config={"font_size": 20, "include_numbers": True}, tips=None).to_edge(DOWN, buff=0.55)
        xlab1 = Text("distance (m)", font="Monospace", font_size=24).next_to(axes1, DOWN, buff=0.2)
        ylab1 = Text("height (m)", font="Monospace", font_size=24).rotate(PI / 2).next_to(axes1, LEFT, buff=0.3)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.5)
        self.play(FadeIn(axes1, shift=UP * 0.2), FadeIn(xlab1), FadeIn(ylab1), run_time=0.7)

        # closed form (no drag), dashed reference
        a45 = np.radians(45)
        Tnd = 2 * v0 * np.sin(a45) / g
        nd_pts = [axes1.c2p(v0 * np.cos(a45) * tt, v0 * np.sin(a45) * tt - 0.5 * g * tt ** 2)
                  for tt in np.linspace(0, Tnd, 400)]
        nd_curve = DashedVMobject(VMobject().set_points_as_corners(nd_pts), num_dashes=70)
        nd_curve.set_stroke(REF, 4)

        full45 = sim(45, k)
        drag_pts = full45[::4]
        if drag_pts[-1] != full45[-1]:
            drag_pts.append(full45[-1])
        dr_curve = VMobject(stroke_color=DRAG_C, stroke_width=5)
        dr_curve.set_points_as_corners([axes1.c2p(px, py) for px, py in drag_pts])

        self.play(Create(nd_curve), Create(dr_curve), run_time=2.2)

        leg = VGroup(
            MathTex(rf"R_{{\text{{no drag}}}} = {rng(45):.1f}\ \text{{m}}", font_size=32, color=REF),
            MathTex(rf"R_{{\text{{drag}}}} = {R_d45:.1f}\ \text{{m}}", font_size=32, color=DRAG_C),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(axes1.c2p(38.5, 9.5), aligned_edge=LEFT)
        dot_nd = Dot(axes1.c2p(rng(45), 0), color=REF, radius=0.09)
        dot_dr = Dot(axes1.c2p(R_d45, 0), color=DRAG_C, radius=0.09)
        self.play(FadeIn(leg, shift=LEFT * 0.3), FadeIn(dot_nd, scale=1.6), FadeIn(dot_dr, scale=1.6),
                  run_time=0.8)
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in (sub, axes1, xlab1, ylab1, nd_curve, dr_curve, leg, dot_nd, dot_dr)],
                  run_time=0.7)

        # ---------------- part C: range vs angle with drag ----------------
        sub2 = Text("best angle drops below 45 deg", font="Monospace", font_size=26, color=BEST).next_to(
            title, DOWN, buff=0.25)
        axes2 = Axes(x_range=[0, 90, 15], y_range=[0, 45, 5], x_length=11.5, y_length=4.6,
                     axis_config={"font_size": 20, "include_numbers": True}, tips=None).to_edge(DOWN, buff=0.55)
        xlab2 = Text("launch angle (deg)", font="Monospace", font_size=24).next_to(axes2, DOWN, buff=0.2)
        ylab2 = Text("range R (m)", font="Monospace", font_size=24).rotate(PI / 2).next_to(axes2, LEFT, buff=0.3)
        self.play(FadeIn(sub2, shift=UP * 0.15), run_time=0.5)
        self.play(FadeIn(axes2, shift=UP * 0.2), FadeIn(xlab2), FadeIn(ylab2), run_time=0.7)

        c_nd = axes2.plot(lambda d: rng(d), x_range=[0, 90], color=REF, stroke_width=4,
                          stroke_opacity=0.55)
        self.play(Create(c_nd), run_time=1.6)

        c_d = VMobject(stroke_color=DRAG_C, stroke_width=5)
        c_d.set_points_as_corners([axes2.c2p(d, r) for d, r in zip(grid, drag_ranges)])
        self.play(Create(c_d), run_time=1.6)

        g45 = DashedLine(axes2.c2p(45, 0), axes2.c2p(45, rng(45)), color=HILITE,
                         stroke_width=3, dash_length=0.12)
        g40 = DashedLine(axes2.c2p(best, 0), axes2.c2p(best, Rbest), color=BEST,
                         stroke_width=3, dash_length=0.12)
        l45 = MathTex(r"45^\circ", font_size=32, color=HILITE).move_to(axes2.c2p(45, 3.5)).shift(RIGHT * 0.42)
        l40 = MathTex(rf"{best:.0f}^\circ", font_size=32, color=BEST).move_to(axes2.c2p(best, 3.5)).shift(LEFT * 0.42)
        self.play(Create(g45), FadeIn(l45, shift=UP * 0.15), run_time=0.6)
        self.play(Create(g40), FadeIn(l40, shift=UP * 0.15), run_time=0.6)

        d_nd = Dot(axes2.c2p(45, rng(45)), color=HILITE, radius=0.09)
        d_d = Dot(axes2.c2p(best, Rbest), color=BEST, radius=0.1)
        lbest = MathTex(rf"{best:.0f}^\circ:\ {Rbest:.1f}\ \text{{m}}", font_size=30,
                        color=BEST).move_to(axes2.c2p(35, 27))
        leg2 = VGroup(
            MathTex(r"\text{no drag}", font_size=30, color=REF),
            MathTex(r"\text{with drag}", font_size=30, color=DRAG_C),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(axes2.c2p(78, 37.5), aligned_edge=LEFT)
        self.play(FadeIn(d_nd, scale=1.6), FadeIn(d_d, scale=1.6),
                  FadeIn(lbest, shift=UP * 0.2), FadeIn(leg2, shift=LEFT * 0.3), run_time=0.8)
        self.wait(3.0)

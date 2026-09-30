"""Free-fall from 20 m: two balls of different mass land together, with a live
position-time graph and a velocity arrow alongside.

All numbers come from work/physics.json and are sanity-checked (2.02 s, 19.8 m/s).
On-screen labels live in label_specs() so work/out/layout_check.py can verify
sizes/positions BEFORE the first render.

Draft render (from repo root):
  manim -ql --media_dir projects/free-fall-2/work/out/media projects/free-fall-2/work/scenes/free_fall.py FreeFall
"""
import os, sys, json
import numpy as np
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "..", "..", "..", ".opencode", "skills", "manim-physics-scenes", "scripts"))
from sync import Timeline

# Shared palette (one palette per video)
TEXT_C, BALL_LIGHT, BALL_HEAVY, GRAPH_C, VEL_C, GROUND_C = WHITE, YELLOW, ORANGE, BLUE, GREEN, GREY

# Layout: 1920x1080 => frame 14.222 x 8.0, x within [-7.111, 7.111], y within [-4, 4]
GROUND_Y, TOP_Y = -1.6, 2.1          # screen y for y = 0 m and y = 20 m
RIG_L, RIG_R = -6.9, -2.0            # drop-rig horizontal extent
X_BALL_L, X_BALL_H = -5.1, -3.9      # the two drop lanes
X_VEL = -6.4                         # velocity-arrow column (alongside the fall)
AX_C = (3.4, 1.15)                   # position-time graph centre
READOUT_POS = (3.12, -2.05)
CALLOUT_POS = (2.92, -2.75)
MASS_LINE_POS = (2.4, -3.4)
R_BALL_L, R_BALL_H = 0.17, 0.27      # radii: heavy ball drawn bigger


def p2(pos):
    """label positions are (x, y); Manim needs a 3-vector."""
    return np.array([pos[0], pos[1], 0.0])


def label_specs(slow_text, T, v_hit):
    """Every on-screen label: (text, font_size, pos, color, when).

    when = "static"   -> on screen from frame 0
         = "readout"  -> live numbers (t, y, v)
         = "impact"   -> shown when both balls strike
         = "together" -> shown when both balls strike
    """
    readout_txt = f"t = {T:.2f} s    y = {0.0:.1f} m    v = {v_hit:.1f} m/s"
    callout_txt = f"IMPACT  t = {T:.2f} s   v = {v_hit:.1f} m/s"
    return [
        ("Two balls, 20 m drop: same fall time", 28, (0.0, 3.7), TEXT_C, "static"),
        ("a = g = 9.81 m/s^2 (no air resistance) - mass cancels", 22, (0.0, 3.35), GROUND_C, "static"),
        ("20 m", 20, (-1.65, TOP_Y), TEXT_C, "static"),
        ("10 m", 20, (-1.65, 0.5 * (GROUND_Y + TOP_Y)), GROUND_C, "static"),
        ("0 m", 20, (-1.65, GROUND_Y), TEXT_C, "static"),
        ("ground, y = 0 m", 22, (-4.0, -2.05), TEXT_C, "static"),
        ("1 kg", 22, (X_BALL_L, 2.5), BALL_LIGHT, "static"),
        ("5 kg", 22, (X_BALL_H, 2.5), BALL_HEAVY, "static"),
        ("v (m/s)", 20, (X_VEL, 2.5), VEL_C, "static"),
        ("19.8 m/s", 18, (X_VEL + 0.1, -2.05), VEL_C, "static"),
        (slow_text, 18, (-4.3, -2.6), GROUND_C, "static"),
        ("y (m)", 20, (1.0, 2.95), TEXT_C, "static"),
        ("t (s)", 20, (AX_C[0], -0.8), TEXT_C, "static"),
        ("position-time:  y(t) = 20 - 4.91*t^2", 20, (AX_C[0], -1.3), GRAPH_C, "static"),
        ("same time, same speed - mass does not matter", 22, MASS_LINE_POS, BALL_HEAVY, "static"),
        (readout_txt, 24, READOUT_POS, TEXT_C, "readout"),
        (callout_txt, 28, CALLOUT_POS, VEL_C, "impact"),
        ("both hit together", 22, (-4.5, -1.05), TEXT_C, "together"),
    ]


class FreeFall(Scene):
    def construct(self):
        tl = Timeline(os.path.join(PROJECT, "timeline.json"))
        phys = json.load(open(os.path.join(PROJECT, "physics.json"), encoding="utf-8"))
        g = float(phys["constants"]["g"])
        h = float(phys["scenario"]["h_m"])
        m_light = float(phys["scenario"]["mass_light_kg"])
        m_heavy = float(phys["scenario"]["mass_heavy_kg"])

        # closed form: T = sqrt(2h/g), v = g*T  (assert against physics.json sanity_check)
        T = float(np.sqrt(2.0 * h / g))
        v_hit = g * T
        exp = phys["sanity_check"]
        assert abs(T - exp["expected_fall_time_s"]) <= exp["fall_time_tolerance_s"], \
            f"fall time {T:.4f} s disagrees with physics.json sanity check"
        assert abs(v_hit - exp["expected_impact_speed_mps"]) <= exp["impact_speed_tolerance_mps"], \
            f"impact speed {v_hit:.3f} m/s disagrees with physics.json sanity check"
        assert m_light != m_heavy, "the two balls must have different masses"

        t_drop = tl.cue("s1.drop")
        t_vel = tl.cue("s1.velocity")
        t_impact = tl.cue("s1.impact")
        T_video = max(t_impact - t_drop, 0.5)
        slow = T_video / T

        # One shared trajectory drives both balls, the graph dot and the readout,
        # so the two masses cannot separate (mass cancels without air resistance).
        def tau_phys(clock):
            return max(0.0, min((clock - t_drop) / T_video, 1.0)) * T

        def y_phys(tau):
            tau = max(0.0, min(tau, T))
            return h - 0.5 * g * tau * tau

        def v_phys(tau):
            return g * max(0.0, min(tau, T))

        def y_screen(y):
            return GROUND_Y + max(0.0, min(y / h, 1.0)) * (TOP_Y - GROUND_Y)

        # ---- static rig + graph -------------------------------------------------
        ground = Line([RIG_L, GROUND_Y, 0], [RIG_R, GROUND_Y, 0], color=GROUND_C, stroke_width=6)
        release = Line([RIG_L, TOP_Y, 0], [RIG_R, TOP_Y, 0], color=GROUND_C, stroke_width=4)
        mid = DashedLine([RIG_L, 0.5 * (GROUND_Y + TOP_Y), 0], [RIG_R, 0.5 * (GROUND_Y + TOP_Y), 0],
                         color=GROUND_C, stroke_width=2).set_opacity(0.4)
        self.add(ground, release, mid)

        axes = Axes(x_range=[0, 2.5, 0.5], y_range=[0, 20, 5], x_length=5.6, y_length=3.0,
                    axis_config={"include_tip": False, "font_size": 20},
                    ).move_to([AX_C[0], AX_C[1], 0])
        self.add(axes)

        # velocity gauge: fixed base at release height, tip reaches the ground at v_hit
        v_base = np.array([X_VEL, TOP_Y, 0])
        guide = Arrow(v_base, v_base + DOWN * (TOP_Y - GROUND_Y), buff=0,
                      color=GROUND_C, stroke_width=4).set_opacity(0.45)
        self.add(guide)
        arrow = Arrow(v_base, v_base + DOWN, buff=0, color=VEL_C, stroke_width=8)

        # labels (shared table, checked by layout_check.py before rendering)
        slow_text = f"slow motion {slow:.1f}x ({T:.2f} s over {T_video:.1f} s)"
        specs = label_specs(slow_text, T, v_hit)
        for txt, size, pos, col, when in specs:
            if when == "static":
                self.add(Text(txt, font="Monospace", font_size=size, color=col).move_to(p2(pos)))
        readout_spec = next(s for s in specs if s[4] == "readout")
        callout_spec = next(s for s in specs if s[4] == "impact")
        together_spec = next(s for s in specs if s[4] == "together")

        # ---- balls: same y(t) for both masses ----------------------------------
        ball_l = Dot([X_BALL_L, y_screen(h), 0], color=BALL_LIGHT, radius=R_BALL_L)
        ball_h = Dot([X_BALL_H, y_screen(h), 0], color=BALL_HEAVY, radius=R_BALL_H)
        self.add(ball_l, ball_h)
        ball_l.add_updater(lambda m: m.move_to(
            [X_BALL_L, y_screen(y_phys(tau_phys(self.renderer.time))), 0]))
        ball_h.add_updater(lambda m: m.move_to(
            [X_BALL_H, y_screen(y_phys(tau_phys(self.renderer.time))), 0]))

        # ---- live position-time curve (drawn as the ball falls) -----------------
        gdot = Dot(axes.c2p(0.0, h), color=GRAPH_C, radius=0.11)
        trace = TracedPath(gdot.get_center, stroke_color=GRAPH_C, stroke_width=5)
        self.add(trace, gdot)
        gdot.add_updater(lambda m: m.move_to(
            axes.c2p(tau_phys(self.renderer.time), y_phys(tau_phys(self.renderer.time)))))

        # ---- fall ---------------------------------------------------------------
        tl.wait_until(self, t_drop)          # balls released here
        tl.wait_until(self, t_vel)           # velocity arrow + live readout appear

        tau_now = tau_phys(self.renderer.time)
        arrow.put_start_and_end_on(v_base, v_base + DOWN * (TOP_Y - GROUND_Y) * v_phys(tau_now) / v_hit)
        txt, size, pos, col, _ = readout_spec
        readout = Text(txt, font="Monospace", font_size=size, color=col).move_to(p2(pos))
        # add first, attach updaters only after the FadeIn (subobject count must not change mid-play)
        self.play(FadeIn(arrow), FadeIn(readout), run_time=0.4)

        arrow.add_updater(lambda m: m.put_start_and_end_on(
            v_base, v_base + DOWN * max((TOP_Y - GROUND_Y) * v_phys(tau_phys(self.renderer.time)) / v_hit, 0.06)))

        def upd_readout(m):
            tau = tau_phys(self.renderer.time)
            m.become(Text(f"t = {tau:.2f} s    y = {y_phys(tau):.1f} m    v = {v_phys(tau):.1f} m/s",
                          font="Monospace", font_size=readout_spec[1], color=readout_spec[3])
                     .move_to(p2(readout_spec[2])))
        readout.add_updater(upd_readout)

        # ---- impact: both balls reach y = 0 m on the same frame -----------------
        tl.wait_until(self, t_impact)
        txt, size, pos, col, _ = callout_spec
        callout = Text(txt, font="Monospace", font_size=size, color=col).move_to(p2(pos))
        txt, size, pos, col, _ = together_spec
        together = Text(txt, font="Monospace", font_size=size, color=col).move_to(p2(pos))
        self.play(
            FadeIn(callout), FadeIn(together),
            Flash([X_BALL_L, GROUND_Y, 0], color=BALL_LIGHT, flash_radius=0.55, run_time=0.5),
            Flash([X_BALL_H, GROUND_Y, 0], color=BALL_HEAVY, flash_radius=0.55, run_time=0.5),
        )

        tl.wait_until(self, tl.end_time() + 0.5)

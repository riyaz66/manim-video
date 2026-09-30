"""LaTeX smoke test (MiKTeX package risk) - run before any real scene render:
  manim -ql --media_dir projects/gravitation/work/out/media projects/gravitation/work/out/latex_smoke.py LatexSmoke
"""
from manim import *

class LatexSmoke(Scene):
    def construct(self):
        a = MathTex(r"F = G\frac{m_1 m_2}{r^2}")
        b = MathTex(r"\boxed{g = \frac{GM}{R^2} = 9.81\,\mathrm{m/s^2}}")
        c = MathTex(r"\vec{F}_{12} = -\vec{F}_{21}", r"\;\;", r"6.67\times10^{-11}\,\mathrm{N\,m^2\,kg^{-2}}")
        d = MathTex(r"F \propto \frac{1}{r^2}", r"\quad", r"T = \frac{2\pi r}{v}")
        e = Text("Monospace label: r, 2r, 3r", font="Monospace", font_size=28)
        self.add(VGroup(a, b, c, d, e).arrange(DOWN, buff=0.35))

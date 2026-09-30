"""LaTeX smoke test - exercises every construct the three scenes use.
Render: manim -ql --media_dir projects/projectile-range/work/out/media projects/projectile-range/work/out/latex_smoke.py LatexSmoke
"""
from manim import *


class LatexSmoke(Scene):
    def construct(self):
        eqs = VGroup(
            MathTex(r"x = v_0 \cos\theta\, t"),
            MathTex(r"y = x\tan\theta - \frac{g x^2}{2v_0^2\cos^2\theta}"),
            MathTex(r"\frac{1}{\cos^2\theta} = 1 + \tan^2\theta"),
            MathTex(r"\vec{a} = -g\,\hat{j} - k\,|\vec{v}|\,\vec{v}"),
            MathTex(r"\boxed{R = \frac{v_0^2 \sin 2\theta}{g}}"),
            MathTex(r"\Delta t = 1\ \text{ms}", tex_environment="align*"),
        ).arrange(DOWN, buff=0.3).scale(0.8)
        self.add(eqs)
        self.wait(0.5)

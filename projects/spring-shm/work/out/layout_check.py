"""Pre-render layout check for projects/spring-shm.

Measures every label from spring_osc.static_specs()/graph_specs() plus the graph axes
(with the x-axis shifted to the bottom, as in the scene) with real Manim metrics, and
exercises move_to - so overflow, overlap and 2-tuple/3-vector bugs die BEFORE a render.

  python projects/spring-shm/work/out/layout_check.py
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, "scenes"))

from manim import Text, Axes, DoubleArrow, DashedLine   # noqa: E402
import spring_osc as sc                                 # noqa: E402

FRAME_X, FRAME_Y = 14.2222 / 2, 8.0 / 2
MARGIN = 0.05


def main():
    phys = json.load(open(os.path.join(WORK, "physics.json"), encoding="utf-8"))
    k, m = float(phys["constants"]["k_Npm"]), float(phys["scenario"]["m_kg"])
    w = float(np.sqrt(k / m))
    T = float(2 * np.pi / w)
    exp = phys["sanity_check"]
    ok = True
    checks = [
        (abs(T - exp["expected_period_s"]), exp["period_tolerance_s"], f"T={T:.4f}s"),
        (abs(w - exp["expected_omega_radps"]), exp["omega_tolerance_radps"], f"omega={w:.4f}rad/s"),
        (abs(1 / T - exp["expected_freq_hz"]), exp["freq_tolerance_hz"], f"f={1/T:.5f}Hz"),
    ]
    for d, tol, msg in checks:
        if d > tol:
            ok = False
            print(f"FAIL physics {msg} (off by {d:.4f} > {tol})")
        else:
            print(f"ok   physics {msg} (within {tol})")

    # same axes object the scene builds (move_to + x_axis shift)
    axes = Axes(x_range=[0, sc.T_AXIS_MAX, 2], y_range=[-0.13, 0.13, 0.05],
                x_length=sc.AX_XLEN, y_length=sc.AX_YLEN,
                axis_config={"include_tip": False, "font_size": 20},
                ).move_to([sc.AX_C[0], sc.AX_C[1], 0])
    axes.x_axis.shift(np.array([0.0, -1.0, 0.0]) * (axes.c2p(0, 0)[1] - axes.c2p(0, -0.13)[1]))

    A = float(phys["scenario"]["amplitude_m"])
    specs = sc.static_specs(A) + sc.graph_specs(axes, T)

    boxes = []
    for txt, size, pos, col, when in specs:
        t = Text(txt, font="Monospace", font_size=size)
        t.move_to(sc.p2(pos))                    # must not raise
        wdt, hgt = t.width, t.height
        cx, cy = pos
        x0, x1, y0, y1 = cx - wdt / 2, cx + wdt / 2, cy - hgt / 2, cy + hgt / 2
        boxes.append((txt, x0, x1, y0, y1, when))
        bad = []
        if x0 < -FRAME_X + MARGIN or x1 > FRAME_X - MARGIN:
            bad.append(f"x [{x0:.2f},{x1:.2f}] outside +-{FRAME_X:.2f}")
        if y0 < -FRAME_Y + MARGIN or y1 > FRAME_Y - MARGIN:
            bad.append(f"y [{y0:.2f},{y1:.2f}] outside +-{FRAME_Y:.2f}")
        if bad:
            ok = False
            print(f"FAIL '{txt[:46]}' (size {size}): " + "; ".join(bad))
        else:
            print(f"ok   '{txt[:46]}' size={size} w={wdt:.2f} box=({x0:.2f},{y0:.2f})-({x1:.2f},{y1:.2f})")

    # axes bbox incl. ticks, and the shifted time axis
    for name, pt in (("axes.left", axes.get_left()), ("axes.right", axes.get_right()),
                     ("axes.top", axes.get_top()), ("axes.bottom", axes.get_bottom())):
        if not (-FRAME_X + MARGIN <= pt[0] <= FRAME_X - MARGIN and -FRAME_Y + MARGIN <= pt[1] <= FRAME_Y - MARGIN):
            ok = False
            print(f"FAIL {name} at {pt} outside frame")
    ax_bottom = axes.x_axis.get_center()[1]
    if abs(ax_bottom - (sc.AX_C[1] - sc.AX_YLEN / 2)) > 0.05:
        ok = False
        print(f"FAIL time axis at y={ax_bottom:.2f}, expected plot bottom "
              f"{sc.AX_C[1] - sc.AX_YLEN / 2:.2f}")
    else:
        print(f"ok   axes x[{axes.get_left()[0]:.2f},{axes.get_right()[0]:.2f}] "
              f"y[{axes.get_bottom()[1]:.2f},{axes.get_top()[1]:.2f}], time axis at y={ax_bottom:.2f}")

    # period bracket bbox
    br = DoubleArrow([axes.c2p(0, 0)[0], sc.BRACKET_Y, 0], [axes.c2p(T, 0)[0], sc.BRACKET_Y, 0],
                     buff=0, max_tip_length_to_length_ratio=0.08)
    if not (-FRAME_X + MARGIN <= br.get_left()[0] and br.get_right()[0] <= FRAME_X - MARGIN):
        ok = False
        print(f"FAIL bracket x [{br.get_left()[0]:.2f},{br.get_right()[0]:.2f}] outside frame")
    else:
        print(f"ok   period bracket x[{br.get_left()[0]:.2f},{br.get_right()[0]:.2f}] "
              f"({axes.c2p(T, 0)[0] - axes.c2p(0, 0)[0]:.2f} units for T={T:.3f} s)")

    # the wave band (must not collide with tick numbers / bracket / labels)
    top_y, bot_y = axes.c2p(0, A)[1], axes.c2p(0, -A)[1]
    print(f"ok   wave band y[{bot_y:.2f},{top_y:.2f}]; zero line at y={axes.c2p(0, 0)[1]:.2f}")

    # burned captions sit in a bottom-centre band: no label may live there
    cap_y0, cap_y1 = sc.CAPTION_BAND
    for b in boxes:
        if b[1] < 1.7 and -1.7 < b[2] and b[3] < cap_y1 and cap_y0 < b[4]:
            ok = False
            print(f"FAIL '{b[0][:34]}' sits in the caption band (y {b[3]:.2f}..{b[4]:.2f})")
    print(f"ok   caption band y[{cap_y0:.2f},{cap_y1:.2f}] x[-1.7,1.7] checked")

    # bracket + T label must sit clear of the traced wave (above or below it)
    if not (br.get_top()[1] < bot_y or br.get_bottom()[1] > top_y):
        ok = False
        print(f"FAIL bracket crosses the wave band")
    tlab = next(b for b in boxes if b[0].startswith("T = "))
    if not (tlab[4] < bot_y or tlab[3] > top_y):
        ok = False
        print(f"FAIL T label crosses the wave band (label y {tlab[3]:.2f}..{tlab[4]:.2f}, wave {bot_y:.2f}..{top_y:.2f})")
    else:
        print(f"ok   bracket/T label clear of the wave band")

    # pairwise overlaps between labels
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]:
                ok = False
                print(f"FAIL overlap: '{a[0][:34]}' ({a[5]}) <> '{b[0][:34]}' ({b[5]})")

    # label vs bracket (bracket is a mobject, not a Text label)
    for b in boxes:
        if b[1] < br.get_right()[0] and br.get_left()[0] < b[2] and b[3] < br.get_top()[1] and br.get_bottom()[1] < b[4]:
            ok = False
            print(f"FAIL bracket overlaps label '{b[0][:34]}'")

    for cls in ("TracedPath", "DoubleArrow", "DashedLine", "VGroup", "Rectangle", "VMobject"):
        if cls not in dir(__import__("manim")):
            ok = False
            print(f"FAIL manim.{cls} missing")
    print("ok   manim helpers present")

    print("LAYOUT OK" if ok else "LAYOUT FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

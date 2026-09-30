"""Pre-render layout check for projects/free-fall-2.

Measures every label in free_fall.label_specs() with the real Manim Text metrics and
fails if anything leaves the 1920x1080 frame or overlaps another label, so label
problems are fixed BEFORE the first render attempt.

  python projects/free-fall-2/work/out/layout_check.py
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, "scenes"))

from manim import Text, Arrow, DashedLine, DOWN   # noqa: E402
import free_fall as ff                            # noqa: E402

FRAME_X, FRAME_Y = 14.2222 / 2, 8.0 / 2
MARGIN = 0.05

def main():
    phys = json.load(open(os.path.join(WORK, "physics.json"), encoding="utf-8"))
    g, h = float(phys["constants"]["g"]), float(phys["scenario"]["h_m"])
    T = float(np.sqrt(2 * h / g))
    v_hit = g * T
    exp = phys["sanity_check"]
    ok = True
    if abs(T - exp["expected_fall_time_s"]) > exp["fall_time_tolerance_s"]:
        print(f"FAIL physics: T={T:.4f}s"); ok = False
    if abs(v_hit - exp["expected_impact_speed_mps"]) > exp["impact_speed_tolerance_mps"]:
        print(f"FAIL physics: v={v_hit:.3f}m/s"); ok = False
    print(f"physics: T={T:.4f} s (want {exp['expected_fall_time_s']}), v={v_hit:.3f} m/s (want {exp['expected_impact_speed_mps']})")

    T_video = 6.0
    slow_text = f"slow motion {T_video/T:.1f}x ({T:.2f} s over {T_video:.1f} s)"
    specs = ff.label_specs(slow_text, T, v_hit)

    boxes = []
    for txt, size, pos, col, when in specs:
        t = Text(txt, font="Monospace", font_size=size)
        t.move_to(ff.p2(pos))                 # must not raise (2-tuple vs 3-vector)
        cx, cy = pos
        w, hh = t.width, t.height
        x0, x1 = cx - w / 2, cx + w / 2
        y0, y1 = cy - hh / 2, cy + hh / 2
        boxes.append((txt, x0, x1, y0, y1))
        bad = []
        if x0 < -FRAME_X + MARGIN or x1 > FRAME_X - MARGIN:
            bad.append(f"x [{x0:.2f},{x1:.2f}] outside +-{FRAME_X:.2f}")
        if y0 < -FRAME_Y + MARGIN or y1 > FRAME_Y - MARGIN:
            bad.append(f"y [{y0:.2f},{y1:.2f}] outside +-{FRAME_Y:.2f}")
        if bad:
            ok = False
            print(f"FAIL '{txt[:44]}' (size {size}): " + "; ".join(bad))
        else:
            print(f"ok   '{txt[:44]}' size={size} w={w:.2f} h={hh:.2f} box=({x0:.2f},{y0:.2f})-({x1:.2f},{y1:.2f})")

    # pairwise overlaps
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]:
                ok = False
                print(f"FAIL overlap: '{a[0][:34]}' <> '{b[0][:34]}'")

    # arrows / helpers used by the scene must exist with the signatures we rely on
    for cls in ("Arrow", "TracedPath", "Flash", "DashedLine", "Dot"):
        try:
            __import__("manim").__dict__[cls]
            print(f"ok   manim.{cls}")
        except KeyError:
            ok = False; print(f"FAIL manim.{cls} missing")
    v_base = np.array([ff.X_VEL, ff.TOP_Y, 0.0])
    arr = Arrow(v_base, v_base + DOWN, buff=0, stroke_width=8)
    arr.put_start_and_end_on(v_base, v_base + DOWN * 0.617)   # must not raise
    print(f"ok   Arrow.put_start_and_end_on -> tip {arr.get_end()}")

    print("LAYOUT OK" if ok else "LAYOUT FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Convert a project video into a PowerPoint animation deck.

One slide per sampled video frame, full-bleed. Pressing Next/Previous in the
PowerPoint slideshow steps the video forward/backward like an animation.
By default slides also auto-advance at the sampling rate, so the slideshow
plays the lesson at video speed (arrow keys still step frame-by-frame).

Usage:
    python .opencode/skills/video-deck/scripts/generate_deck.py projects/<name>
    python ... generate_deck.py projects/<name> --fps 10      # smoother/more slides
    python ... generate_deck.py projects/<name> --manual      # step only, no autoplay
    python ... generate_deck.py projects/<name> --intro       # add a title slide first
    python ... generate_deck.py projects/<name> --video x.mp4 --out y.pptx

Source video (first that exists): --video, video/<name>_final.mp4,
video/<name>_draft.mp4, work/out/joined.mp4.

Output (default): projects/<name>/slides/<name>_slides.pptx
Frames cached in projects/<name>/work/out/deck_frames/ (git-ignored, rebuildable).
Reads only - never touches the video, timeline or scenes.
"""
from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Inches, Pt

INK = RGBColor(0x16, 0x1A, 0x28)
MUTED = RGBColor(0x5A, 0x64, 0x72)
ACCENT = RGBColor(0x1E, 0x88, 0xE5)


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {p.stderr.strip()[:300]}")
    return p.stdout


def ffprobe_dur(path: Path) -> float | None:
    if shutil.which("ffprobe") is None:
        return None
    try:
        return float(run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0",
                          str(path)]).strip())
    except Exception:
        return None


def delivered_video(proj: Path) -> Path | None:
    video = proj / "video"
    for pat in ("*_final.mp4", "*_draft.mp4"):
        hits = sorted(video.glob(pat), key=lambda p: p.stat().st_mtime)
        if hits:
            return hits[-1]
    joined = proj / "work" / "out" / "joined.mp4"
    return joined if joined.exists() else None


def extract_frames(src: Path, fps: float, out_dir: Path) -> list[Path]:
    """One-pass ffmpeg sampling: f_00001.jpg ... at `fps` frames/second."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    run(["ffmpeg", "-y", "-i", str(src), "-vf", f"fps={fps}",
         "-q:v", "4", str(out_dir / "f_%05d.jpg")])
    return sorted(out_dir.glob("f_*.jpg"))


def set_auto_advance(slide, ms: int) -> None:
    """Insert <p:transition advClick="1" advTm="ms"><p:cut/></p:transition>."""
    sld = slide._element
    for old in sld.findall(qn("p:transition")):
        sld.remove(old)
    tr = parse_xml(
        f'<p:transition {nsdecls("p")} spd="none" advClick="1" advTm="{int(ms)}">'
        f"<p:cut/></p:transition>")
    anchor = sld.find(qn("p:clrMapOvr"))
    if anchor is None:
        anchor = sld.find(qn("p:cSld"))
    anchor.addnext(tr)


def intro_slide(prs, title: str, video_name: str, mode: str):
    blank = prs.slide_layouts[6]
    sl = prs.slides.add_slide(blank)
    bar = sl.shapes.add_textbox(Inches(0.0), Inches(2.6), Inches(0.35), Inches(1.6))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    tb = sl.shapes.add_textbox(Inches(0.9), Inches(2.15), Inches(11.6), Inches(1.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = INK
    tb2 = sl.shapes.add_textbox(Inches(0.9), Inches(3.9), Inches(11.6), Inches(1.6))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "video animation as slides \u2014 \u25b6 plays it, \u25c0\u25b6 steps frames"
    p.font.size = Pt(20)
    p.font.color.rgb = ACCENT
    p2 = tf2.add_paragraph()
    p2.text = (f"{video_name}   \u00b7   mode: {mode}   \u00b7   "
               f"generated {datetime.date.today().isoformat()}")
    p2.font.size = Pt(14)
    p2.font.color.rgb = MUTED
    p2.space_before = Pt(10)
    return sl


def build(proj: Path, out_pptx: Path, video_arg: str | None, fps: float,
          manual: bool, intro: bool) -> int:
    src = Path(video_arg) if video_arg else delivered_video(proj)
    if src is None or not src.exists():
        print(f"ERROR: no video found in {proj} (video/*.mp4)", file=sys.stderr)
        return 2
    dur = ffprobe_dur(src)
    if not dur:
        print(f"ERROR: ffprobe could not read {src}", file=sys.stderr)
        return 2

    frames_dir = proj / "work" / "out" / "deck_frames"
    frames = extract_frames(src, fps, frames_dir)
    if not frames:
        print("ERROR: ffmpeg extracted no frames", file=sys.stderr)
        return 2

    title, mode = proj.name, "?"
    try:
        import json
        tl = json.loads((proj / "work" / "timeline.json").read_text(encoding="utf-8"))
        title = str((tl.get("meta") or {}).get("title") or proj.name)
        mode = str((tl.get("meta") or {}).get("mode") or "?")
    except Exception:
        pass

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    adv_ms = max(40, round(1000 / fps))

    n = 0
    if intro:
        s = intro_slide(prs, title, src.name, mode)
        if not manual:
            set_auto_advance(s, max(3000, adv_ms))
        n = 1

    for f in frames:                     # full-bleed: video ratio == slide ratio
        sl = prs.slides.add_slide(blank)
        sl.shapes.add_picture(str(f), 0, 0,
                              width=prs.slide_width, height=prs.slide_height)
        if not manual:
            set_auto_advance(sl, adv_ms)
        n += 1

    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_pptx)
    mb = out_pptx.stat().st_size / 1e6
    play = "manual next/prev" if manual else f"auto-plays {adv_ms} ms/frame"
    print(f"DECK OK  {out_pptx}  slides={n} frames={len(frames)} "
          f"fps={fps:g} {play} source={src.name} size={mb:.1f}MB")
    if len(frames) > 1800:
        print(f"NOTE: {len(frames)} slides is a lot - consider --fps 6")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Video -> PowerPoint frame-by-frame animation deck")
    ap.add_argument("project", help="projects/<name> (or bare name)")
    ap.add_argument("--fps", type=float, default=10.0,
                    help="frames per second sampled from the video (default 10)")
    ap.add_argument("--manual", action="store_true",
                    help="no autoplay: step slides yourself with next/previous")
    ap.add_argument("--intro", action="store_true",
                    help="add a title slide before the animation")
    ap.add_argument("--video", help="override the source video")
    ap.add_argument("--out", help="output .pptx (default <proj>/slides/<name>_slides.pptx)")
    a = ap.parse_args()

    p = Path(a.project)
    if not p.exists():
        p = Path("projects") / a.project
    if not p.is_dir():
        print(f"ERROR: project not found: {a.project}", file=sys.stderr)
        return 2
    if a.fps <= 0 or a.fps > 60:
        print("ERROR: --fps must be in (0, 60]", file=sys.stderr)
        return 2
    out = Path(a.out) if a.out else p / "slides" / f"{p.name}_slides.pptx"
    return build(p, out, a.video, a.fps, a.manual, a.intro)


if __name__ == "__main__":
    sys.exit(main())

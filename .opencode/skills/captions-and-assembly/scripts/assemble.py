#!/usr/bin/env python3
"""Mux narration audio and burned-in captions onto a rendered Manim video with ffmpeg.

  python .opencode/skills/captions-and-assembly/scripts/assemble.py projects/x/timeline.json projects/x/out/media/videos/projectile/480p15/Projectile.mp4 projects/x/out/final.mp4 [--no-captions]

Fixing a caption or the audio only needs this step again - no Manim re-render.
Silent mode: if the timeline has no audio file, only captions (if any) are burned in.
"""
import json, os, subprocess, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
import captions

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 3: sys.exit(__doc__)
    tl_path, video, out = map(os.path.abspath, args)
    tl = captions.load(tl_path); base = os.path.dirname(tl_path)
    outdir = os.path.dirname(out); os.makedirs(outdir, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-i", video]
    audio = tl.get("audio", {}).get("file")
    audio_path = os.path.join(base, audio) if audio else None
    has_audio = bool(audio_path and os.path.exists(audio_path))
    if has_audio: cmd += ["-i", audio_path]
    want_caps = "--no-captions" not in sys.argv and tl.get("words")
    if want_caps:
        srt = os.path.join(outdir, "captions.srt")
        with open(srt, "w", encoding="utf-8") as f:
            for i, g in enumerate(captions.groups(tl), 1):
                f.write(f"{i}\n{captions.ts(g['start'])} --> {captions.ts(g['end'])}\n{g['text']}\n\n")
        # YouTube-small captions, scaled to video height so drafts and finals match.
        # 480p draft -> ~11px, 1080p final -> ~24px (was fixed 24 = huge on drafts).
        height = 480
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=height", "-of", "csv=p=0", video],
                capture_output=True, text=True, check=True)
            height = max(240, int(probe.stdout.strip().split()[0]))
        except Exception:
            pass
        fontsize = max(10, round(height * 0.022))
        outline = 1 if fontsize <= 14 else 2
        marginv = max(8, round(height * 0.02))
        style = f"FontSize={fontsize},Outline={outline},Shadow=0,Alignment=2,MarginV={marginv}"
        cmd += ["-vf", f"subtitles=captions.srt:force_style='{style}'"]   # relative name; ffmpeg runs in outdir
    cmd += ["-map", "0:v"] + (["-map", "1:a", "-c:a", "aac"] if has_audio else [])
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", out]
    print(" ".join(cmd)); subprocess.run(cmd, check=True, cwd=outdir)
    print("wrote", out)

if __name__ == "__main__": main()

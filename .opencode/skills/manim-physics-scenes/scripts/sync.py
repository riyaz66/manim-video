"""Timeline helper for Manim scenes. Pure Python (no manim import), so it is easy to test.

Usage inside a Scene:
    tl = Timeline("projects/demo/timeline.json")
    t_launch = tl.cue("s1.launch")           # seconds into the narration
    tl.wait_until(self, t_launch)            # pauses the scene until that moment
    tl.wait_until(self, tl.end_time() + 0.5) # make sure the video covers all the audio
Animate motion as a function of the scene clock (self.renderer.time), e.g. position = f(clock - t_launch).
"""
import json

class Timeline:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            self.data = json.load(f)
        self.words = {w["id"]: w for w in self.data.get("words", [])}

    def cue(self, name):
        """name is 'sceneId.cueName'. Resolved from the word the cue points at (survives caption fixes)."""
        scene_id, cue_name = name.split(".", 1)
        for sc in self.data.get("scenes", []):
            if sc["id"] == scene_id:
                for c in sc.get("cues", []):
                    if c["name"] == cue_name:
                        w = self.words.get(c["at_word"])
                        if w is None:
                            raise KeyError(f"cue {name} points at removed word id {c['at_word']}; re-point it")
                        return w["start"] + c.get("offset", 0.0)
        raise KeyError(f"cue {name} not found in timeline.json")

    def end_time(self):
        ws = self.data.get("words", [])
        return max((w["end"] for w in ws), default=0.0)

    @staticmethod
    def wait_until(scene, t):
        gap = t - scene.renderer.time
        if gap > 1e-3:
            scene.wait(gap)

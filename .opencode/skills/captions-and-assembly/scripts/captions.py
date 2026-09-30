#!/usr/bin/env python3
"""Caption tools driven by timeline.json word timings.

  apply-text <timeline> <corrected.txt>   keep timings, swap in corrected wording
  srt <timeline> <out.srt>                caption file
  groups <timeline> <out.json>            caption groups for the HyperFrames scene
  cues <timeline>                         resolve cue names to seconds
"""
import json, re, sys, difflib, shutil

def norm(t): return re.sub(r"[^\w]", "", t.lower())
def load(p):
    with open(p, encoding="utf-8") as f: return json.load(f)
def save(p, d):
    with open(p, "w", encoding="utf-8") as f: json.dump(d, f, indent=2, ensure_ascii=False)

def spread(tokens, s, e, ids):
    """Share the span s..e between tokens in proportion to their length."""
    w = [max(len(t), 1) for t in tokens]; tot = sum(w); out = []; t0 = s
    for tok, wi, i in zip(tokens, w, ids):
        t1 = t0 + (e - s) * wi / tot
        out.append({"id": i, "text": tok, "start": round(t0, 3), "end": round(t1, 3)})
        t0 = t1
    return out

def apply_text(tl, text):
    old, new = tl["words"], text.split()
    a, b = [norm(w["text"]) for w in old], [norm(t) for t in new]
    nid = max((w["id"] for w in old), default=-1) + 1
    out, dropped = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        toks = new[j1:j2]
        if tag == "equal":
            for k, t in enumerate(toks):
                w = dict(old[i1 + k]); w["text"] = t; out.append(w)
        elif tag == "delete":
            dropped += [old[i]["id"] for i in range(i1, i2)]
        elif tag == "replace":
            if len(toks) == i2 - i1:            # 1:1 swap keeps ids, so cues survive
                for k, t in enumerate(toks):
                    w = dict(old[i1 + k]); w["text"] = t; out.append(w)
            else:
                dropped += [old[i]["id"] for i in range(i1, i2)]
                ids = list(range(nid, nid + len(toks))); nid += len(toks)
                out += spread(toks, old[i1]["start"], old[i2 - 1]["end"], ids)
        elif tag == "insert":
            ids = list(range(nid, nid + len(toks))); nid += len(toks)
            if out:                              # share the previous word's time slot
                prev = out.pop()
                out += spread([prev["text"]] + toks, prev["start"], prev["end"], [prev["id"]] + ids)
            elif old:
                s = max(0.0, old[0]["start"] - 0.25 * len(toks))
                out += spread(toks, s, old[0]["start"], ids)
            else:
                out += spread(toks, 0.0, 0.3 * len(toks), ids)
    tl["words"] = out
    warns = []
    for sc in tl.get("scenes", []):
        for c in sc.get("cues", []):
            if c["at_word"] in dropped:
                warns.append(f"cue '{c['name']}' pointed at removed word id {c['at_word']} - re-point it")
    return warns

def groups(tl):
    cfg = tl.get("meta", {}).get("captions", {})
    mw, mc = cfg.get("max_words", 7), cfg.get("max_chars", 42)
    out, cur = [], []
    def flush():
        if cur:
            out.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                        "text": " ".join(w["text"] for w in cur), "word_ids": [w["id"] for w in cur]})
            cur.clear()
    for w in tl["words"]:
        if cur and (len(cur) >= mw or len(" ".join(x["text"] for x in cur + [w])) > mc):
            flush()
        cur.append(w)
        if re.search(r"[.!?]$", w["text"]): flush()
    flush()
    return out

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    cmd, path = sys.argv[1], sys.argv[2]; tl = load(path)
    if cmd == "apply-text":
        shutil.copy(path, path + ".bak")
        with open(sys.argv[3], encoding="utf-8") as f: warns = apply_text(tl, f.read())
        save(path, tl); print(f"updated {path} (backup: {path}.bak)")
        for w in warns: print("WARNING:", w)
    elif cmd == "srt":
        with open(sys.argv[3], "w", encoding="utf-8") as f:
            for i, g in enumerate(groups(tl), 1):
                f.write(f"{i}\n{ts(g['start'])} --> {ts(g['end'])}\n{g['text']}\n\n")
        print("wrote", sys.argv[3])
    elif cmd == "groups":
        save(sys.argv[3], groups(tl)); print("wrote", sys.argv[3])
    elif cmd == "cues":
        byid = {w["id"]: w for w in tl["words"]}; res = {}
        for sc in tl.get("scenes", []):
            for c in sc.get("cues", []):
                w = byid.get(c["at_word"])
                res[f"{sc['id']}.{c['name']}"] = round(w["start"] + c.get("offset", 0), 3) if w else None
        print(json.dumps(res, indent=2))
    else: print(__doc__)

if __name__ == "__main__": main()

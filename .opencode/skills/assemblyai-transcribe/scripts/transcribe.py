#!/usr/bin/env python3
"""Audio file -> word-level timings in a project's timeline.json, using AssemblyAI (standard library only).

  python .opencode/skills/assemblyai-transcribe/scripts/transcribe.py projects/x/audio/lesson.wav \
      --vocab projects/x/vocab.txt --out projects/x/timeline.json [--language en] [--context "Physics lesson on ..."]

Flow (per the AssemblyAI quickstart): upload the file -> POST /v2/transcript -> poll -> read words (times in ms).
The API key is read from local_secrets.py next to this script.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

BASE = "https://api.assemblyai.com"

def api_key():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from local_secrets import ASSEMBLYAI_API_KEY
    except ImportError:
        sys.exit("Missing local_secrets.py - copy local_secrets.example.py to local_secrets.py and add your key.")
    if not ASSEMBLYAI_API_KEY or "paste" in ASSEMBLYAI_API_KEY:
        sys.exit("Put your AssemblyAI key in local_secrets.py")
    return ASSEMBLYAI_API_KEY

def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} from {url}: {e.read().decode(errors='replace')[:500]}")

def transcribe(path, keyterms, language, context, key):
    H = {"authorization": key}
    with open(path, "rb") as f:                      # raw bytes, as the docs require
        up = http(BASE + "/v2/upload", f.read(), {**H, "content-type": "application/octet-stream"}, "POST")

    def run(use_terms):
        body = {"audio_url": up["upload_url"]}
        if language: body["language_code"] = language
        else: body["language_detection"] = True
        if use_terms and keyterms: body["keyterms_prompt"] = keyterms[:1000]
        if use_terms and context: body["prompt"] = context
        job = http(BASE + "/v2/transcript", json.dumps(body).encode(), {**H, "content-type": "application/json"}, "POST")
        while True:
            r = http(f"{BASE}/v2/transcript/{job['id']}", headers=H)
            if r["status"] in ("completed", "error"):
                return r
            time.sleep(3)

    r = run(True)
    if r["status"] == "error" and (keyterms or context):
        print("Vocabulary/context options were rejected, retrying without them:", r.get("error"), file=sys.stderr)
        r = run(False)
    if r["status"] == "error":
        sys.exit("AssemblyAI error: " + str(r.get("error")))
    print("transcript id:", r.get("id"))            # keep this id; needed to fetch or delete the transcript later
    words = r.get("words") or [w for u in r.get("utterances", []) for w in u.get("words", [])]
    return [(w["text"], w["start"] / 1000.0, w["end"] / 1000.0) for w in words]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("--out", required=True)
    ap.add_argument("--vocab", help="text file, one physics term per line (max 6 words each)")
    ap.add_argument("--language", help="e.g. en. Omit to auto-detect")
    ap.add_argument("--context", help="one plain sentence about the audio, e.g. 'Physics lesson on projectile motion.'")
    a = ap.parse_args()
    terms = [l.strip() for l in open(a.vocab, encoding="utf-8") if l.strip()] if a.vocab else []
    words = transcribe(a.audio, terms, a.language, a.context, api_key())
    tl = json.load(open(a.out, encoding="utf-8")) if os.path.exists(a.out) else {
        "meta": {"mode": "teacher_voice", "fps": 30, "width": 1920, "height": 1080, "captions": {"max_words": 7, "max_chars": 42}}, "scenes": []}
    tl["audio"] = {"file": os.path.relpath(a.audio, os.path.dirname(os.path.abspath(a.out)))}
    tl["words"] = [{"id": i, "text": t, "start": round(s, 3), "end": round(e, 3)} for i, (t, s, e) in enumerate(words)]
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(tl, f, indent=2, ensure_ascii=False)
    print(f"wrote {len(words)} words to {a.out}")

if __name__ == "__main__":
    main()

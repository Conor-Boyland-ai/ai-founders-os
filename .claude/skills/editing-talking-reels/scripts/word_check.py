"""Word check: re-transcribe each FINAL and diff against the raw transcript. Every raw word must be in the final.
Spelling variants (5/five, gonna/going to) are fine. A missing or changed word next to a cut = a clip: fix before showing the user.
Usage (same working folder as screencast.py): python3 word_check.py jobs.json id[,id]"""
import json, difflib, re, sys
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
jobs = {j["id"]: j for j in json.load(open(sys.argv[1]))}
for k in sys.argv[2].split(","):
    segs, _ = m.transcribe(jobs[k]["out"], word_timestamps=True, condition_on_previous_text=False)
    fw = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]
    json.dump(fw, open(f"final_words_{k}.json", "w"))
    raw = json.load(open(f"words_{k}.json")); cuts = json.load(open(f"segs_{k}.json"))
    n = lambda ws: [re.sub(r"[^a-z0-9]", "", x["w"].lower()) for x in ws]
    a, b = n(raw), n(fw)
    print(f"== {k}: raw {len(a)} words, final {len(b)}")
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if op == "equal" or not a[i1:i2]: continue
        s, e = raw[i1]["s"], raw[i2 - 1]["e"]
        near = any(s - 0.3 < y and x < e + 0.3 for (_, x), (y, _) in zip(cuts, cuts[1:]))
        print(f"   {op} {a[i1:i2]} -> {b[j1:j2]} @raw {s:.2f}s {'<-- CUT NEARBY: inspect' if near else '(no cut nearby: transcriber variance)'}")

"""Word-level transcripts for raw clips.
Usage: python3 transcribe.py <id>=<raw video path> [<id>=<path> ...]
Writes words_<id>.json (list of {w, s, e}) into the current folder.
Retries with vad_filter=True if a clip comes back empty (happened once on 2026-09-29)."""
import json, os, sys
from faster_whisper import WhisperModel
# medium.en by default (2026-10-01): small.en misplaced words by 1s+ after fast lines, which broke retake cuts and pause cuts
m = WhisperModel(os.environ.get("WHISPER_MODEL", "medium.en"), device="cpu", compute_type="int8")
ALT = WhisperModel("small.en", device="cpu", compute_type="int8")
for arg in sys.argv[1:]:
    k, path = arg.split("=", 1)
    words = []
    for kw in (dict(condition_on_previous_text=False), dict(vad_filter=True)):
        segs, _ = m.transcribe(path, word_timestamps=True, **kw)
        words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
        if words: break
    json.dump(words, open(f"words_{k}.json", "w"))
    # backup pass with small.en: any model can drop a stretch of words, and the pause cutter keeps sound near words EITHER pass heard
    alt = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in ALT.transcribe(path, word_timestamps=True)[0] for w in s.words]
    json.dump(alt, open(f"words_{k}.alt.json", "w"))
    print(f"== {k}: {len(words)} words\n" + " ".join(x["w"] for x in words))

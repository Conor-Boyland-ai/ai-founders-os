"""Output-time word timings for animation cues. Run from the working folder: python3 <skill>/scripts/word_timings.py 4 5 -> ow_<id>.json"""
import json, sys
_a = sys.argv[1:]; sys.argv = ['x']
import reel_editor as B, laptop
jobs = {j["id"]: j for j in json.load(open("jobs.json"))}
for k in (_a or ["4", "5", "6"]):
    cfg = jobs[k]; cfg.setdefault("max_chars", 26)
    P = laptop.plan(cfg)
    out = [{"w": w["w"], "s": round(P["m"](w["s"]), 3), "e": round(P["m"](w["e"]), 3)} for w in P["words"]]
    json.dump({"total": P["total"], "words": out, "caps": P["caps"]}, open(f"ow_{k}.json", "w"))
    print(k, round(P["total"], 2))
    print(" ".join(f"{x['w']}@{x['s']:.2f}" for x in out))

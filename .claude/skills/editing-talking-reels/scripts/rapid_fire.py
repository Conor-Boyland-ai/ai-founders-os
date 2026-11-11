import json, re, sys, subprocess, os
SK = os.path.dirname(os.path.abspath(__file__)); S = os.getcwd(); sys.path.insert(0, SK)
import onset, grade
FF = onset.FF
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
def item_starts(words, labels):
    out, wi = [], 0
    for lab in labels:
        first = norm(lab.split()[0].replace("$",""))
        while wi < len(words) and not norm(words[wi]["w"]).startswith(first[:4]): wi += 1
        if wi >= len(words): raise SystemExit(f"could not find '{lab}'")
        out.append(words[wi]["s"]); wi += 1
    return out
def snap(ts, ends):
    out = []
    for t in ts:
        c = min(ends, key=lambda e: abs(e-t)) if ends else t
        out.append(c if abs(c-t) <= 0.5 else t)
    for i in range(1,len(out)):
        if out[i] <= out[i-1]: out[i] = max(ts[i], out[i-1]+0.2)
    return out
def run(r):
    n = r["id"]
    words = json.load(open(f"{S}/words_{n}.json"))
    A = onset.analyze(r["raw"])
    ends = [i*onset.STEP for i in range(1,len(A["active"])) if A["active"][i] and not A["active"][i-1]]  # voice onsets
    raw_s = item_starts(words, [l for l in r["match"]])
    s = snap(raw_s, ends)
    t0 = onset.voice_onset(A, words[0]["s"])
    t1 = onset.voice_offset(A, words[-1]["s"])
    s[0] = t0 + 0.05   # first item on screen from frame 0
    base = json.load(open(f"{SK}/rapid_fire_base.json"))
    base.update(wrap=r.get("wrap",False), item_gap=r.get("item_gap",0.0), max_item=r.get("max_item",60), title=r["title"], sub=r["sub"], cta=r["cta"], sample_only=False, trim_start=t0, duration=t1-t0,
                items=[{"t":t,"s":x} for t,x in zip(r["labels"], s)])
    cp = f"{S}/cfg_{n}.json"; json.dump(base, open(cp,"w"))
    subprocess.run(["python3", f"{SK}/rapid_fire_render.py", cp], check=True)
    out = r["out"]
    subprocess.run([FF,"-loglevel","error","-y","-ss",f"{t0:.3f}","-to",f"{t1:.3f}","-i",r["raw"],"-f","concat","-safe","0","-i",f"{S}/states2.txt",
      "-filter_complex","[0:v]setpts=PTS-STARTPTS,"+(grade.grade_filter(r["raw"], r.get("grade_strength",0.5), r.get("grade_lift",1.0)) if r.get("grade",True) else "null")+"[bg];[1:v]fps=30,format=rgba[ov];[bg][ov]overlay=eof_action=repeat:shortest=1,format=yuv420p[v];[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.005,afade=t=out:st=%.3f:d=0.03[a]" % (t1-t0-0.03),
      "-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","18","-c:a","aac","-b:a","160k",
      "-t",f"{t1-t0:.3f}","-movflags","+faststart",out], check=True)
    probe = subprocess.run([FF,"-hide_banner","-i",out],capture_output=True,text=True).stderr
    if "displaymatrix" in probe or "rotation" in probe:
        tmp = out+".fix.mp4"
        subprocess.run([FF,"-loglevel","error","-y","-display_rotation:v:0","0","-i",out,"-map","0","-c","copy","-movflags","+faststart",tmp],check=True)
        os.replace(tmp,out)
        assert "displaymatrix" not in subprocess.run([FF,"-hide_banner","-i",out],capture_output=True,text=True).stderr, "rotation tag still present"
    print(n, f"trim {t0:.2f}-{t1:.2f} ({t1-t0:.1f}s)", "shifts:", [round(b-a,2) for a,b in zip(raw_s,s)])
if __name__ == "__main__":
    for r in json.load(open(sys.argv[1])): run(r)

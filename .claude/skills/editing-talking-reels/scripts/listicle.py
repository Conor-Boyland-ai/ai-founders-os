import json, os, re, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import onset, grade
SK=os.path.dirname(os.path.abspath(__file__)); S=os.getcwd()
FF=onset.FF; W,H=1080,1920; FPS=30
def F(size, w):
    f=ImageFont.truetype(SK+"/fonts/Inter.ttf", size); f.set_variation_by_name(w); return f
def snap(t): return round(t*FPS)/FPS

def speech_segments(A, t0, t1, gap_cut=0.06, pad_in=0.02, pad_out=0.035):   # ruthless: every silence over 60 ms -> ~55 ms
    st=onset.STEP; act=onset.speech_mask(A); voiced=A["voiced"]
    i0,i1=int(t0/st),min(len(act),int(t1/st))
    runs=[]; cur=None; gap=0
    for i in range(i0,i1):
        if act[i]:
            if cur is None: cur=[i,i]
            else: cur[1]=i
            gap=0
        elif cur is not None:
            gap+=1
            if gap*st>=gap_cut: runs.append(cur); cur=None; gap=0
    if cur: runs.append(cur)
    segs=[]; loud=float(np.median(A["v"][A["voiced"]]))-10
    for a,b in runs:
        if voiced[a:b+1].sum()*st < 0.03 or A["v"][a:b+1].max() < loud: continue   # click / blip / quiet room noise -> drop (same bar as the clipped-voice check)
        segs.append([max(t0,a*st-pad_in), min(t1,(b+1)*st+pad_out)])
    segs[0][0]=t0; segs[-1][1]=t1
    merged=[]
    for a,b in segs:
        a,b=snap(a),snap(b)
        if merged and a<=merged[-1][1]: merged[-1][1]=max(b,merged[-1][1])
        else: merged.append([a,b])
    return merged

def mapper(segs):
    cum=[]; acc=0
    for a,b in segs: cum.append((a,b,acc)); acc+=b-a
    def m(t):
        for a,b,c in cum:
            if t<a: return c
            if t<=b: return c+(t-a)
        return acc
    return m, acc

def shadow_text(im, xy, text, f, fill="white", blur=5, alpha=190, anchor="la"):
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text(xy,text,font=f,fill=(0,0,0,alpha),anchor=anchor)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy,text,font=f,fill=fill,anchor=anchor)

def wrap(text,f,maxw):
    out,cur=[], ""
    for w in text.split():
        t=(cur+" "+w).strip()
        if f.getlength(t)<=maxw: cur=t
        else: out.append(cur); cur=w
    return out+[cur]

def frame(cfg, label, caption):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); L=cfg["layout"]
    size=L["title_size"]; tf=F(size,"SemiBold")
    while tf.getlength(cfg["title"])>W-2*L["margin"] and size>L.get("title_min",48): size-=1; tf=F(size,"SemiBold")
    tl=wrap(cfg["title"],tf,W-2*L["margin"])
    if len(tl)==2:  # balance the two lines
        ws=cfg["title"].split(); best=None
        for i in range(1,len(ws)):
            a=" ".join(ws[:i]); b=" ".join(ws[i:])
            d=abs(tf.getlength(a)-tf.getlength(b))
            if max(tf.getlength(a),tf.getlength(b))<=W-2*L["margin"] and (best is None or d<best[0]): best=(d,[a,b])
        if best: tl=best[1]
    y=L["title_y"]
    for line in tl:
        shadow_text(im,(W/2,y),line,tf,anchor="mt"); y+=int(size*1.18)
    if cfg.get("sub"):
        sf=F(L["sub_size"],"Medium"); shadow_text(im,(W/2,y+2),cfg["sub"],sf,anchor="mt"); y+=2+int(L["sub_size"]*1.25)
    label_y=y+L["label_gap"]
    if label:
        lf=F(L["label_size"],"Medium"); ls=L["label_size"]
        while lf.getlength(label)>W-2*L["margin"]: ls-=1; lf=F(ls,"Medium")
        # label sits on a black box so it stands out (the user, 2026-09-29)
        l,t,r,b=ImageDraw.Draw(im).textbbox((W/2,label_y),label,font=lf,anchor="mt")
        px,py=int(ls*0.5),int(ls*0.32)
        box=Image.new("RGBA",(W,H),(0,0,0,0))
        ImageDraw.Draw(box).rounded_rectangle((l-px,t-py,r+px,b+py),radius=int(ls*0.3),fill=(0,0,0,235))
        im.alpha_composite(box)
        ImageDraw.Draw(im).text((W/2,label_y),label,font=lf,fill="white",anchor="mt")
    if caption:
        cf=F(L["cap_size"],"SemiBold"); y=L["cap_y"]
        for line in wrap(caption,cf,W-2*L["cap_margin"]):
            shadow_text(im,(W/2,y),line,cf,anchor="mt",blur=6,alpha=210); y+=int(L["cap_size"]*1.2)
    return im

def fix(text, reps):
    for a,b in reps: text=re.sub(a,b,text,flags=re.I)
    return text

def run(cfg, only_frames=False):
    k=cfg["id"]; raw=cfg["raw"]; words=json.load(open(f"{S}/words_{k}.json"))
    A=onset.analyze(raw)
    t0=onset.voice_onset(A, words[0]["s"]); t1=min(onset.voice_offset(A, words[-1]["s"]), len(A["active"])*onset.STEP)
    segs=speech_segments(A,t0,t1); m0,total=mapper(segs)
    st_=onset.STEP; removed_voice=0
    for (a1,b1),(a2,b2) in zip(segs,segs[1:]):
        removed_voice+=int(A["voiced"][int(round(b1/st_)):int(round(a2/st_))].sum())
    assert removed_voice==0, f"a cut would remove {removed_voice*5}ms of voice"
    act=A["active"]; st=onset.STEP
    onsets=[i*st for i in range(1,len(act)) if act[i] and not act[i-1]]
    def m(t):
        near=[o for o in onsets if abs(o-t)<=0.25]
        return m0(min(near,key=lambda o:abs(o-t)) if near else t)
    # captions: chunk words
    FUNC={"a","an","the","to","of","and","or","but","for","as","that","they","you","your","is","are","was","with","on","in","at","about","because","how","if","so","it's","i","my","their","its","be","by","from","into","than","then","when","what","like","not","this","just","any","who","we","me","to","do","don't","can't","it","has","have","had","every","even","no","more","all","some","can","could","will","would","should","may","might","nobody","one","very","really","you're","we're","they're","i'm","i'll","you'll","we'll","that's","there's","i've","you've","we","if","or","times"}
    # 1) split into clauses at punctuation or real pauses
    clauses=[]; cur=[]
    for i,w in enumerate(words):
        cur.append(w); nxt=words[i+1] if i+1<len(words) else None
        if nxt is None or w["w"][-1:] in ".?!,;:" or nxt["s"]-w["e"]>0.3: clauses.append(cur); cur=[]
    # 2) split long clauses at the most natural point (never after a function word)
    MAXC=cfg.get("max_chars",28)
    txt=lambda ws:" ".join(x["w"] for x in ws)
    bare=lambda w:re.sub(r"[^a-z']","",w["w"].lower())
    def split(ws):
        if len(txt(ws))<=MAXC or len(ws)<3: return [ws]
        best=None
        for i in range(1,len(ws)):
            L,R=ws[:i],ws[i:]
            cost=abs(len(txt(L))-len(txt(R)))/len(txt(ws))
            if bare(L[-1]) in FUNC: cost+=3
            if len(L)==1 or len(R)==1: cost+=2
            if bare(R[0]) in FUNC: cost-=0.3
            if best is None or cost<best[0]: best=(cost,i)
        i=best[1]; return split(ws[:i])+split(ws[i:])
    chunks=[p for c in clauses for p in split(c)]
    caps=[]
    for c in chunks:
        txt=" ".join(x["w"] for x in c)
        txt=fix(txt, cfg.get("fixes",[]))
        txt=re.sub(r"[.,]+$","",txt).strip()
        if cfg.get("lower",True): txt=txt.lower()
        for a,b in cfg.get("post",[]): txt=re.sub(a,b,txt)
        t=m(c[0]["s"])
        if caps and t<=caps[-1][0]+0.12: t=max(m0(c[0]["s"]), caps[-1][0]+0.12)
        caps.append([t, txt])
    merged=[]
    for i,(t,txt) in enumerate(caps):
        nxt=caps[i+1][0] if i+1<len(caps) else total
        if merged and merged[-1][2]:   # previous was too short: fold it into this one
            pt,ptxt,_=merged.pop(); t,txt=pt,ptxt+(", " if ptxt.split()[-1] in ("one","two","three","four","five","finally") else " ")+txt
        merged.append([t,txt,(nxt-t)<0.35 and i+1<len(caps)])
    caps=[[t,x] for t,x,_ in merged]
    # labels: find marker word sequences in order
    toks=[re.sub(r"[^a-z0-9]","",w["w"].lower()) for w in words]
    labs=[]; pos=0
    for marker,label in cfg["labels"]:
        mt=marker.lower().split()
        while pos<len(toks) and toks[pos:pos+len(mt)]!=mt: pos+=1
        if pos>=len(toks): raise SystemExit(f"marker not found: {marker}")
        labs.append([m(words[pos]["s"]), label]); pos+=len(mt)
    # timeline of states
    events=sorted(set([0.0]+[c[0] for c in caps]+[l[0] for l in labs]))
    def at(t, lst):
        v=None
        for tt,x in lst:
            if tt<=t+1e-6: v=x
        return v
    os.makedirs(f"{S}/st_{k}",exist_ok=True)
    lines=[]; states=[]
    for i,t in enumerate(events):
        end=events[i+1] if i+1<len(events) else total
        if end-t<1e-3: continue
        states.append((t,end,at(t,labs),at(t,caps)))
    if only_frames: return states, segs, total
    for i,(t,end,lab,cap) in enumerate(states):
        frame(cfg,lab,cap).save(f"{S}/st_{k}/s{i:03d}.png")
        lines.append(f"file 'st_{k}/s{i:03d}.png'\nduration {end-t:.4f}\n")
    lines.append(f"file 'st_{k}/s{len(states)-1:03d}.png'\n")
    open(f"{S}/st_{k}.txt","w").write("".join(lines))
    parts=[]; labels_v=[]
    for i,(a,b) in enumerate(segs):
        fa,fb=int(round(a*FPS)),int(round(b*FPS))
        parts.append(f"[0:v]trim=start_frame={fa}:end_frame={fb},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={fa/FPS:.6f}:end={fb/FPS:.6f},asetpts=PTS-STARTPTS[a{i}]")
        labels_v.append(f"[v{i}][a{i}]")
    total=sum(int(round(b*FPS))-int(round(a*FPS)) for a,b in segs)/FPS
    out=cfg["out"]
    gf=grade.grade_filter(raw, cfg.get("grade_strength",0.5), cfg.get("grade_lift",1.0)) if cfg.get("grade",True) else "null"
    fc=(";".join(parts)+";"+"".join(labels_v)+f"concat=n={len(segs)}:v=1:a=1[bg0][ac];[bg0]"+gf+"[bg];"
        f"[ac]afade=t=in:d=0.005,afade=t=out:st={total-0.03:.3f}:d=0.03[a];"
        f"[1:v]fps={FPS},format=rgba[ov];[bg][ov]overlay=eof_action=repeat:shortest=1,format=yuv420p[v]")
    subprocess.run([FF,"-loglevel","error","-y","-i",raw,"-f","concat","-safe","0","-i",f"{S}/st_{k}.txt",
        "-filter_complex",fc,"-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","18",
        "-c:a","aac","-b:a","160k","-t",f"{total:.3f}","-movflags","+faststart",out],check=True)
    probe=subprocess.run([FF,"-hide_banner","-i",out],capture_output=True,text=True).stderr
    if "displaymatrix" in probe:
        tmp=out+".fix.mp4"; subprocess.run([FF,"-loglevel","error","-y","-display_rotation:v:0","0","-i",out,"-map","0","-c","copy","-movflags","+faststart",tmp],check=True); os.replace(tmp,out)
    print(k, f"raw {words[-1]['e']:.1f}s -> {total:.1f}s, {len(segs)} segments, {len(states)} overlay states")
if __name__=="__main__":
    jobs=json.load(open(sys.argv[1]))
    for j in jobs:
        if len(sys.argv)<3 or j["id"] in sys.argv[2].split(","): run(j)

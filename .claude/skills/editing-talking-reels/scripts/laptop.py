import json, os, re, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import onset, grade
SK=os.path.dirname(os.path.abspath(__file__)); S=os.getcwd()
FF=onset.FF; W,H=1080,1920; FPS=30; SFPS=30
def F(size, w):
    f=ImageFont.truetype(SK+"/fonts/Inter.ttf", size); f.set_variation_by_name(w); return f
def snap(t): return round(t*SFPS)/SFPS
def src_fps(raw):
    import re as _re
    pr=subprocess.run([FF,'-hide_banner','-i',raw],capture_output=True,text=True).stderr
    m=_re.search(r'(\d+(?:\.\d+)?) fps',pr); return float(m.group(1)) if m else 30.0

def speech_mask(A, tail=0.12):
    """His voice, plus consonant hiss (s, t, f) only where it touches a word, max `tail` s. Breaths and room noise don't count.
    (Approved cutter, 10/1. A pitch-based breath cutter was tried 10/1 night and left a swipe at every cut. Don't bring it back.)"""
    v=A["voiced"]; act=A["active"]; m=v.copy(); k=int(tail/onset.STEP); n=len(v)
    for i in range(1,n):                                     # hiss running straight out of a word
        if v[i-1] and not v[i]:
            j=i
            while j<n and j<i+k and act[j] and not v[j]: m[j]=True; j+=1
    for i in range(n-2,-1,-1):                               # hiss running straight into a word
        if v[i+1] and not v[i]:
            j=i
            while j>=0 and j>i-k and act[j] and not v[j]: m[j]=True; j-=1
    return m

def speech_segments(A, t0, t1, gap_cut=0.06, pad_in=0.02, pad_out=0.035, words=None):
    st=onset.STEP; act=speech_mask(A); voiced=A["voiced"]
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

def ring(im, cx, cy, r, frac, num, L):
    """Countdown ring: white arc showing time remaining, number in the middle."""
    d=ImageDraw.Draw(im); w=L["ring_width"]
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ds=ImageDraw.Draw(sh)
    ds.ellipse((cx-r-w,cy-r-w,cx+r+w,cy+r+w),fill=(0,0,0,L.get("ring_bg_alpha",110)))   # soft dark disc so the ring reads on bright backgrounds
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    d=ImageDraw.Draw(im); d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,70),width=w)   # faint full track
    d=ImageDraw.Draw(im)
    if frac>0: d.arc((cx-r,cy-r,cx+r,cy+r),start=-90,end=-90+360*frac,fill="white",width=w)
    f=F(L["ring_num_size"],"SemiBold")
    shadow_text(im,(cx,cy),str(num),f,anchor="mm",blur=4,alpha=170)

def frame(cfg, hook_on, caption, secs_left, frac):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); L=cfg["layout"]
    if hook_on:
        tf=F(L["hook_size"],"Bold"); sf=F(L["hook_sub_size"],"SemiBold")
        size=L["hook_size"]
        while tf.getlength(cfg["title"])>W-2*L["margin"]-2*L["hook_pad"] and size>40: size-=1; tf=F(size,"Bold")
        d=ImageDraw.Draw(im); y=L["hook_y"]
        tb=d.textbbox((W/2,y),cfg["title"],font=tf,anchor="mt")
        lines=[(cfg["title"],tf,tb)]
        if cfg.get("sub"):
            sb=d.textbbox((W/2,tb[3]+L["hook_gap"]),cfg["sub"],font=sf,anchor="mt"); lines.append((cfg["sub"],sf,sb))
        l=min(b[0] for _,_,b in lines)-L["hook_pad"]; r=max(b[2] for _,_,b in lines)+L["hook_pad"]
        t=lines[0][2][1]-L["hook_pad"]*0.6; bt=lines[-1][2][3]+L["hook_pad"]*0.6
        box=Image.new("RGBA",(W,H),(0,0,0,0))
        ImageDraw.Draw(box).rounded_rectangle((l,t,r,bt),radius=L["hook_radius"],fill=(255,255,255,245))
        im.alpha_composite(box)
        d=ImageDraw.Draw(im)
        y=L["hook_y"]
        for txt,f,b in lines:
            d.text((W/2,y),txt,font=f,fill=(10,10,10),anchor="mt"); y=b[3]+L["hook_gap"]
    if cfg.get("timer",True):
        ring(im,L["ring_x"],L["ring_y"],L["ring_r"],frac,secs_left,L)
    if caption:
        cf=F(L["cap_size"],"SemiBold"); y=L["cap_y"]
        for line in wrap(caption,cf,W-2*L["cap_margin"]):
            shadow_text(im,(W/2,y),line,cf,anchor="mt",blur=6,alpha=210); y+=int(L["cap_size"]*1.2)
    return im

def fix(text, reps):
    for a,b in reps: text=re.sub(a,b,text,flags=re.I)
    return text

def plan(cfg):
    """Cut plan shared by every talking-head format: retake drops, ruthless pause cuts, time mapping, caption chunks."""
    k=cfg["id"]; raw=cfg["raw"]; words=json.load(open(f"{S}/words_{k}.json"))
    global SFPS; SFPS=src_fps(raw)
    A=onset.analyze(raw); st_=onset.STEP
    drops=[]
    for d0,d1 in cfg.get("drop",[]):                       # retakes: drop from the end of the last kept word to the onset of the next kept word
        act=A["active"]; j=int(d0/st_)
        prev=[w["e"] for w in words if w["s"]<d0-0.02]; lo=int(round(max(prev)/st_)) if prev else 0   # never cut into the last kept word
        while j>lo and act[j-1]: j-=1                            # back to the dropped take's first sound
        k=j
        while k>lo and not act[k-1]: k-=1                        # back across the silence before it
        if k<j: a=k*st_+0.03                                     # cut starts right after the last kept sound
        else:                                                    # transcript put the take change inside the kept word's tail: cut at the first silence after it
            i=lo
            while i<len(act) and act[i]: i+=1
            a=i*st_+0.01
        ons=[j*st_ for j in range(int((d1-0.6)/st_),int((d1+0.3)/st_)) if A["active"][j] and not A["active"][j-1]]
        b=(min(ons,key=lambda o:abs(o-d1)) if ons else d1)-0.03
        drops.append([a,b])
    indrop=lambda t: any(a-0.01<=t<=b+0.01 for a,b in drops)
    words=[w for w in words if not any(d0-0.02<=w["s"]<d1-0.02 for d0,d1 in cfg.get("drop",[]))]
    words=[w for w in words if not any(abs(w["s"]-t)<0.02 for t in cfg.get("drop_caption_words",[]))]
    t0=onset.voice_onset(A, words[0]["s"]); t1=min(onset.voice_offset(A, words[-1]["s"]), len(A["active"])*onset.STEP)
    segs=speech_segments(A,t0,t1)
    for a,b in drops:                                       # subtract retake ranges
        out=[]
        for x,y in segs:
            if y<=a or x>=b: out.append([x,y])
            else:
                if x<a: out.append([x,snap(a)])
                if y>b: out.append([snap(b),y])
        segs=[s_ for s_ in out if s_[1]-s_[0]>0.05]
    m0,total=mapper(segs)
    removed_voice=0; where=[]                                # count only real voice (runs >= 30 ms, within 10 dB of his speech level), ignore clicks/room blips
    loud=float(np.median(A["v"][A["voiced"]]))-10
    for (a1,b1),(a2,b2) in zip(segs,segs[1:]):
        run_=0
        for i in range(int(round(b1/st_)),int(round(a2/st_))+1):
            v=i<len(A["voiced"]) and A["voiced"][i] and not indrop(i*st_)
            if v: run_+=1
            else:
                if run_*st_>=0.03 and A["v"][i-run_:i].max()>=loud: removed_voice+=run_; where.append(round((i-run_)*st_,2))
                run_=0
    assert removed_voice==0, f"a cut would remove {removed_voice*5}ms of voice outside the retakes at {where}"
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
    return dict(k=k,raw=raw,words=words,segs=segs,total=total,caps=caps,m=m,m0=m0)

def at(t, lst):
    v=None
    for tt,x in lst:
        if tt<=t+1e-6: v=x
    return v

def run(cfg, only_frames=False):
    P=plan(cfg); k,raw,words,segs,total,caps,m0=P['k'],P['raw'],P['words'],P['segs'],P['total'],P['caps'],P['m0']
    # hook box: on from frame 0 until the end of the first sentence (or hook_secs if given)
    if cfg.get("hook_secs"): hook_end=cfg["hook_secs"]
    else:
        first_end=next((w for w in words if w["w"][-1:] in ".?!"), words[min(len(words)-1,12)])
        hook_end=min(m0(first_end["e"])+0.2, 6.0)
    # countdown: whole seconds remaining, ticking every second
    clock=float(cfg.get("timer_start",90))                 # fake clock (the user 2026-10-01): always counts down from 90 so the reel ends before they expect
    if total>clock-5: clock=float(int(total)//15*15+30); print(f"!! reel is {total:.1f}s, timer raised to {clock:.0f}s")
    ticks=[float(k) for k in range(1,int(total)+1) if k<total]
    events=sorted(set([0.0,hook_end]+[c[0] for c in caps]+ticks))
    os.makedirs(f"{S}/st_{k}",exist_ok=True)
    lines=[]; states=[]
    for i,t in enumerate(events):
        end=events[i+1] if i+1<len(events) else total
        if end-t<1e-3: continue
        hk=t<hook_end-1e-6
        states.append((t,end,hk,None if (hk and not cfg.get('caps_during_hook',True)) else at(t,caps)))
    if only_frames: return states, segs, total
    render(cfg, P, [(t,end,(lambda t=t,lab=lab,cap=cap: frame(cfg,lab,cap,int(round(clock-t+0.4999)),(clock-t)/clock))) for t,end,lab,cap in states])

def render(cfg, P, states):
    """states = [(t, end, draw)] where draw() returns the 1080x1920 RGBA overlay for that span. Cuts the raw, grades it, burns overlays in."""
    k,raw,words,segs=P['k'],P['raw'],P['words'],P['segs']
    os.makedirs(f"{S}/st_{k}",exist_ok=True); lines=[]
    for i,(t,end,draw) in enumerate(states):
        draw().save(f"{S}/st_{k}/s{i:03d}.png")
        lines.append(f"file 'st_{k}/s{i:03d}.png'\nduration {end-t:.4f}\n")
    lines.append(f"file 'st_{k}/s{len(states)-1:03d}.png'\n")
    open(f"{S}/st_{k}.txt","w").write("".join(lines))
    # streaming cut: keep source frames n in [fa,fb) and audio samples in the same time ranges (no per-segment buffering)
    fr=[(int(round(a*SFPS)),int(round(b*SFPS))) for a,b in segs]
    vsel="+".join(f"between(n,{fa},{fb-1})" for fa,fb in fr)
    total=sum(int(round(b*SFPS))-int(round(a*SFPS)) for a,b in segs)/SFPS
    out=cfg["out"]
    gf=grade.grade_filter(raw, cfg.get("grade_strength",0.5), cfg.get("grade_lift",1.0)) if cfg.get("grade",True) else "null"
    # audio: sample-exact trims (aselect keeps whole ~21 ms audio frames, which drifted lip sync by ~2 ms per cut)
    n=len(fr); atr="".join(f"[as{i}]atrim=start={fa/SFPS:.6f}:end={fb/SFPS:.6f},asetpts=PTS-STARTPTS[at{i}];" for i,(fa,fb) in enumerate(fr))
    fc=(f"[0:v]select='{vsel}',setpts=N/({SFPS}*TB),fps={FPS},"+gf+"[bg];"
        f"[0:a]asplit={n}"+"".join(f"[as{i}]" for i in range(n))+";"+atr+"".join(f"[at{i}]" for i in range(n))+f"concat=n={n}:v=0:a=1[ac];"
        f"[ac]afade=t=in:d=0.005,afade=t=out:st={total-0.03:.3f}:d=0.03[a];"
        f"[1:v]fps={FPS},format=rgba[ov];[bg][ov]overlay=eof_action=repeat:shortest=1,format=yuv420p[v]")
    subprocess.run([FF,"-loglevel","warning","-y","-i",raw,"-f","concat","-safe","0","-i",f"{S}/st_{k}.txt",
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

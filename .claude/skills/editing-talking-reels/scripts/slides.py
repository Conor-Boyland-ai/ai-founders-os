"""Build a click-through slide deck (HTML) for laptop-tutorial reels.
Usage: python3 slides.py deck.json <out_folder>
deck.json: {"title": "...", "keyword_color": "#12A150", "slides": [
   {"kind":"image","file":"proof.png","note":"$ screenshot of sales"},
   {"kind":"title","text":"The Starving Buyers Formula"},
   {"kind":"steps","title":"Step 1","lines":["One Person","trying + failing"]},   # each line appears on its own click
   {"kind":"big","text":"LISTEN UP"},
   {"kind":"cta","text":"Comment","keyword":"BUYERS"} ]}
Images live in <out_folder>/images/. Missing images show a placeholder saying what goes there."""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards
spec=json.load(open(sys.argv[1])); out=sys.argv[2]
os.makedirs(os.path.join(out,"images"),exist_ok=True)
acc=spec.get("keyword_color","#12A150")
frames=[]   # every click = one frame
for s in spec["slides"]:
    k=s["kind"]
    if k=="steps":
        for n in range(len(s["lines"])+1):
            frames.append({"kind":"steps","title":s["title"],"lines":s["lines"][:n],"all":s["lines"]})
    elif k=="list" and s.get("static"):
        frames.append({"kind":"list","title":s.get("title",""),"lines":s["lines"],"all":s["lines"]})
    elif k=="list":   # overview list that builds line by line
        for n in range(0,len(s["lines"])+1):
            frames.append({"kind":"list","title":s.get("title",""),"lines":s["lines"][:n],"all":s["lines"]})
    elif k=="proof":
        fs=s["files"]
        if len(fs)>1:
            frames.append({"kind":"proof","files":fs,"notes":s.get("notes",[]),"n":0})
        for n in range(1,len(fs)+1): frames.append({"kind":"proof","files":fs,"notes":s.get("notes",[]),"n":n})
    elif k=="tease":
        c=s["card"]; s=dict(s); s["cardhtml"]=getattr(cards,c[0])(*c[1:]); frames.append(s)
    elif k=="step" and s.get("card"):
        c=s["card"]; fn=getattr(cards,c[0]); s=dict(s); s["cardhtml"]=fn(*c[1:]); frames.append(s)
    else: frames.append(s)
data=json.dumps(frames)
page=f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(spec['title'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#F7F5F0;--ink:#16171A;--muted:#6B6E76;--acc:{acc};}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif;overflow:hidden;cursor:none}}
#s{{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:6vh 8vw}}
.t{{font-weight:800;font-size:7.2vw;letter-spacing:-.02em;line-height:1.05}}
.rule{{width:16vw;height:.5vw;background:var(--acc);border-radius:1vw;margin-top:3vh}}
.st{{font-weight:800;font-size:5.2vw;letter-spacing:-.02em;color:var(--acc)}}
.ln{{font-weight:700;font-size:6vw;margin-top:1.5vh;line-height:1.1;letter-spacing:-.02em}}
.ln.sub{{font-weight:500;color:var(--muted);font-size:2.8vw}}
.hold{{visibility:hidden}}
.big{{font-weight:800;font-size:10vw;letter-spacing:-.03em}}
.big span,.kw{{color:var(--acc)}}
.li{{font-weight:600;font-size:3.4vw;margin-top:1.8vh;display:flex;gap:1.4vw;align-items:baseline}}
.li b{{color:var(--acc);font-weight:800}}
img{{max-width:84vw;max-height:84vh}}
.ph{{border:.35vw dashed #C9C6BE;border-radius:1.5vw;width:70vw;height:62vh;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:2.6vw;font-weight:600;padding:3vw}}
.pr{{display:flex;gap:3vw;align-items:center;justify-content:center;width:100%}} .pc img{{width:29vw;height:60vh;object-fit:contain}} .pr .ph{{width:26vw;height:46vh;font-size:1.6vw}} .pr .pc:only-child img{{width:88vw;height:84vh;object-fit:contain}} .pr .pc:only-child .ph{{width:70vw;height:62vh;font-size:2.6vw}} .st.sm{{font-size:3.4vw}} .ln.sm{{font-size:4.2vw;margin-top:.6vh}} .cw{{margin-top:4vh;display:flex;justify-content:center;zoom:1.25}} .cd{{background:#fff;border:.25vh solid #E4E0D6;border-radius:1.8vh;padding:3vh 2.2vw;box-sizing:border-box}} .tg{{font-size:1.1vw;font-weight:600;padding:.7vh 1vw;border-radius:2vh;background:#EEEBE3;color:#6B6E76}} .cta{{font-weight:800;font-size:8vw;letter-spacing:-.02em}}
#n{{display:none}}
</style></head><body><div id="s"></div><div id="n"></div>
<script>
const F={data};let i=0;const esc=t=>t.replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));
function r(){{const f=F[i],s=document.getElementById('s');let h='';
 if(f.kind=='title')h=`<div class=t>${{esc(f.text)}}</div><div class=rule></div>`;
 else if(f.kind=='big')h=`<div class=big>${{f.text.replace(/\\*(.+?)\\*/g,'<span>$1</span>')}}</div>`;
 else if(f.kind=='steps'){{h=`<div class=st>${{esc(f.title)}}</div>`;f.all.forEach((l,j)=>{{h+=`<div class="ln ${{j>0?'sub':''}} ${{j<f.lines.length?'':'hold'}}">${{esc(l)}}</div>`}})}}
 else if(f.kind=='list'){{h=f.title?`<div class=st style="margin-bottom:2vh">${{esc(f.title)}}</div>`:'';f.all.forEach((l,j)=>{{h+=`<div class="li ${{j<f.lines.length?'':'hold'}}"><b>${{j+1}}</b>${{esc(l)}}</div>`}})}}
 else if(f.kind=='image')h=`<img src="images/${{f.file}}" onerror="this.outerHTML='<div class=ph>[ ${{esc(f.note||f.file)}} ]<br><br>drop ${{f.file}} in the images folder</div>'">`;
 else if(f.kind=='step')h=f.cardhtml?`<div class="st sm">${{esc(f.title)}}</div><div class="ln sm">${{esc(f.name)}}</div><div class=cw>${{f.cardhtml}}</div>`:`<div class=st>${{esc(f.title)}}</div><div class=ln>${{esc(f.name)}}</div>`;
 else if(f.kind=='proof'){{h='<div class=pr>';f.files.forEach((fl,j)=>{{const nt=esc(f.notes[j]||fl);h+=`<div class="pc ${{j<f.n?'':'hold'}}"><img src="images/${{fl}}" data-note="${{nt}}" data-file="${{fl}}" onerror="ph(this)"></div>`}});h+='</div>'}}
 else if(f.kind=='blank')h='';
 else if(f.kind=='tease')h=`<div class=t style="font-size:5.6vw">${{esc(f.text)}}</div><div class=rule></div><div class=cw style="margin-top:6vh">${{f.cardhtml}}</div>`;
 else if(f.kind=='cta')h=`<div class=cta>${{esc(f.text)}} <span class=kw>${{esc(f.keyword)}}</span></div>`;
 s.innerHTML=h;document.getElementById('n').textContent=(i+1)+'/'+F.length}}
function ph(el){{const d=document.createElement('div');d.className='ph';d.innerHTML=el.dataset.note+'<br><br>'+el.dataset.file;el.replaceWith(d)}}
function go(d){{i=Math.max(0,Math.min(F.length-1,i+d));r()}}
document.addEventListener('keydown',e=>{{if(['ArrowRight',' ','PageDown','Enter'].includes(e.key))go(1);else if(['ArrowLeft','PageUp','Backspace'].includes(e.key))go(-1);else if(e.key=='f')document.documentElement.requestFullscreen()}});
document.addEventListener('click',()=>go(1));document.addEventListener('contextmenu',e=>{{e.preventDefault();go(-1)}});
i=Math.min(F.length-1,parseInt((location.hash||'#0').slice(1))||0);r();
</script></body></html>"""
open(os.path.join(out,"index.html"),"w").write(page)
print(out, len(frames), "clicks")

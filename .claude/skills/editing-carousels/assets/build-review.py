"""
Batch review page — every carousel in posting order on one page. The COVER of each is live:
drag/zoom the photo, drag/size/align the title, set the darkness. "Save framing" downloads cover-framing.json;
then run apply-framing.py to render the covers exactly as the user set them.

Usage: python3 assets/build-review.py <batch-dir>
Needs in <batch-dir>: batch.json (order, slots, decks), captions.py (CAPTIONS), cNN-*-export/ slides,
and editor/ (srcNN.jpg photos, cNN-title-{left,center,right}.png overlays, title-boxes.json)
from prep-covers.sh. Optional: cover-framing.json (saved framing, loaded as the starting point).
"""
import sys, os, json, glob, html, time
B = os.path.abspath(sys.argv[1]); sys.path.insert(0, B)
from captions import CAPTIONS
cfg = json.load(open(os.path.join(B, 'batch.json')))
box = json.load(open(os.path.join(B, 'editor/title-boxes.json')))
saved = json.load(open(os.path.join(B, 'cover-framing.json'))) if os.path.exists(os.path.join(B, 'cover-framing.json')) else {}
v = str(int(time.time()))
cards = []
for i, n in enumerate(cfg['order']):
    d = cfg['decks'][str(n)]; slides = sorted(glob.glob(os.path.join(B, d['name'] + '-export/slide-*.png')))
    rest = ''.join('<figure><img src="%s?v=%s" loading="lazy"><figcaption>%d</figcaption></figure>' % (os.path.relpath(p, B), v, j + 2) for j, p in enumerate(slides[1:]))
    flag = '<span class="flag">%d slides · post manually</span>' % len(slides) if len(slides) > 10 else '<span class="tag">%d slides</span>' % len(slides)
    cards.append(f'''<section class="card" data-n="{n}">
<header><div class="pos">{i+1}</div><div><div class="slot">{html.escape(cfg['slots'][i])}</div><h2>{html.escape(d['title'])}</h2><div class="meta">{d['series']} {flag}</div></div></header>
<div class="strip"><div class="cover"><div class="frame"><img class="photo" src="editor/src{n:02d}.jpg" draggable="false"><div class="dark"></div><img class="title" src="editor/c{n:02d}-title-left.png" draggable="false"><div class="foot l"></div><div class="foot r">&rarr;</div></div>
<div class="ctl">Photo zoom <input class="pz" type="range" min="1" max="2.5" step="0.01"></div>
<div class="ctl">Text size <input class="tz" type="range" min="0.6" max="1.4" step="0.01"></div>
<div class="ctl">Darkness <input class="dk" type="range" min="0" max="0.85" step="0.01"></div>
<div class="ctl"><span class="al"><button data-a="left">Left</button><button data-a="center">Center</button><button data-a="right">Right</button></span><button class="reset">Reset</button></div></div>{rest}</div>
<div class="cap"><div class="caphead">Caption <button class="copy">Copy</button></div><pre>{html.escape(CAPTIONS[n])}</pre></div>
</section>''')
nav = ''.join('<a href="#" data-go="%d">%d</a>' % (n, i + 1) for i, n in enumerate(cfg['order']))
page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Carousel Batch Review</title><style>
body{margin:0;background:#0e0f11;color:#f2f2f2;font:14px/1.45 -apple-system,Helvetica Neue,sans-serif}
.top{position:sticky;top:0;z-index:9;background:rgba(14,15,17,.94);border-bottom:1px solid #2a2d31;padding:10px 20px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.top nav a{color:#9aa0a6;text-decoration:none;margin-right:8px;font-weight:600}.top nav a:hover{color:#fff}
#save{background:#4caf50;color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:14px;font-weight:700;cursor:pointer}
main{padding:18px}.card{background:#17191c;border:1px solid #2a2d31;border-radius:14px;padding:16px;margin-bottom:24px}
header{display:flex;gap:14px;margin-bottom:10px}.pos{font-size:26px;font-weight:800;color:#9aa0a6;min-width:36px}
.slot{color:#9aa0a6;font-size:12px;text-transform:uppercase;letter-spacing:.04em}h2{margin:2px 0;font-size:19px}.meta{color:#9aa0a6;font-size:13px}
.tag{margin-left:6px;border:1px solid #2a2d31;padding:1px 8px;border-radius:99px}.flag{margin-left:6px;color:#111;background:#ffb454;padding:1px 8px;border-radius:99px;font-weight:600}
.strip{display:flex;gap:10px;overflow-x:auto;padding-bottom:8px;align-items:flex-start}
figure{margin:0;flex:0 0 auto}figure img{width:432px;height:540px;border-radius:6px;display:block;cursor:zoom-in}figcaption{color:#9aa0a6;font-size:12px;text-align:center}
.cover{flex:0 0 auto}.frame{position:relative;width:432px;height:540px;overflow:hidden;border-radius:6px;cursor:grab;background:#000;touch-action:none;box-shadow:0 0 0 2px #4caf50}
.photo{position:absolute;left:0;top:0;user-select:none;max-width:none}
.dark{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.5) 82%,rgba(0,0,0,.62));pointer-events:none}
.title{position:absolute;cursor:move;user-select:none;transform-origin:center center;outline:1px dashed transparent}.title:hover{outline-color:rgba(255,255,255,.35)}
.foot{position:absolute;bottom:23px;font-size:10.4px;font-weight:500;opacity:.8;pointer-events:none}.foot.l{left:28px}.foot.r{right:28px;font-size:16px;bottom:20px}
.ctl{margin-top:6px;color:#aaa;display:flex;gap:8px;align-items:center}.ctl input{width:200px}
button{background:#2a2d31;color:#eee;border:0;border-radius:6px;padding:4px 10px;cursor:pointer}.al button.on{background:#4caf50;color:#fff}
.cap{margin-top:10px;border-top:1px solid #2a2d31;padding-top:10px}.caphead{color:#9aa0a6;font-size:13px;margin-bottom:6px;display:flex;gap:10px;align-items:center}
pre{white-space:pre-wrap;font:inherit;margin:0;max-width:760px}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.9);display:none;align-items:center;justify-content:center;z-index:20}#lb img{max-height:94vh;max-width:94vw}
</style></head><body>
<div class="top"><b>Batch review</b><nav>''' + nav + '''</nav><span style="color:#9aa0a6">Green-outlined cover is live: drag title / photo, sliders, align.</span><button id="save">Save framing</button><span id="msg"></span></div>
<main>''' + ''.join(cards) + '''</main><div id="lb" onclick="this.style.display='none'"><img></div>
<script>
const FW=432,FH=540,K=FW/1080,KEY='coverFraming-'+''' + json.dumps(os.path.basename(B).replace('batch-', '')) + ''',BOX=''' + json.dumps(box) + ''',SAVED=''' + json.dumps(saved) + ''';
let state={}; try{state=JSON.parse(localStorage.getItem(KEY)||'null')||SAVED}catch(e){state=SAVED}
document.querySelectorAll('.card').forEach(card=>{
  const n=card.dataset.n, img=card.querySelector('.photo'), frame=card.querySelector('.frame'), title=card.querySelector('.title'),
        pz=card.querySelector('.pz'), tz=card.querySelector('.tz'), dk=card.querySelector('.dk'), dark=card.querySelector('.dark'), reset=card.querySelector('.reset'), als=card.querySelectorAll('.al button'), B=BOX[n];
  let s=Object.assign({zoom:1,cx:.5,cy:.5,tx:0,ty:0,ts:1,al:'left',dk:.5},state[n]||{});
  function save(){state[n]=s;try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){}}
  function layout(){
    const iw=img.naturalWidth, ih=img.naturalHeight, sc=Math.max(FW/iw,FH/ih)*s.zoom, w=iw*sc, h=ih*sc;
    let x=FW/2-s.cx*w, y=FH/2-s.cy*h; x=Math.min(0,Math.max(FW-w,x)); y=Math.min(0,Math.max(FH-h,y));
    s.cx=(FW/2-x)/w; s.cy=(FH/2-y)/h;
    dark.style.background='linear-gradient(to bottom,rgba(0,0,0,'+s.dk+') 82%,rgba(0,0,0,'+Math.min(1,s.dk+.12)+'))';
    Object.assign(img.style,{width:w+'px',height:h+'px',left:x+'px',top:y+'px'});
    const b=B[s.al], src='editor/c'+String(n).padStart(2,'0')+'-title-'+s.al+'.png'; if(!title.getAttribute('src').startsWith(src))title.setAttribute('src',src);
    als.forEach(bt=>bt.classList.toggle('on',bt.dataset.a===s.al));
    Object.assign(title.style,{left:(b[0]+s.tx)*K+'px',top:(b[1]+s.ty)*K+'px',width:(b[2]-b[0])*K+'px',height:(b[3]-b[1])*K+'px',transform:'scale('+s.ts+')'});
    save();
  }
  img.complete?layout():img.onload=layout;
  pz.value=s.zoom; tz.value=s.ts; dk.value=s.dk; dk.oninput=()=>{s.dk=+dk.value;layout()};
  pz.oninput=()=>{s.zoom=+pz.value;layout()}; tz.oninput=()=>{s.ts=+tz.value;layout()};
  als.forEach(bt=>bt.onclick=()=>{s.al=bt.dataset.a;layout()});
  reset.onclick=()=>{s={zoom:1,cx:.5,cy:.5,tx:0,ty:0,ts:1,al:'left',dk:.5};pz.value=1;tz.value=1;dk.value=.5;layout()};
  let drag=null;
  frame.addEventListener('pointerdown',e=>{frame.setPointerCapture(e.pointerId);drag={t:e.target===title,x:e.clientX,y:e.clientY,cx:s.cx,cy:s.cy,tx:s.tx,ty:s.ty}});
  frame.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
    if(drag.t){s.tx=drag.tx+dx/K;s.ty=drag.ty+dy/K}else{s.cx=drag.cx-dx/img.offsetWidth;s.cy=drag.cy-dy/img.offsetHeight}layout()});
  frame.addEventListener('pointerup',()=>drag=null);
  card.querySelector('.copy').onclick=()=>navigator.clipboard.writeText(card.querySelector('pre').innerText);
});
document.querySelectorAll('figure img').forEach(i=>i.onclick=()=>{const l=document.getElementById('lb');l.querySelector('img').src=i.src;l.style.display='flex'});
document.querySelectorAll('nav a').forEach(a=>a.onclick=e=>{e.preventDefault();document.querySelector('.card[data-n="'+a.dataset.go+'"]').scrollIntoView({behavior:'smooth'})});
document.getElementById('save').onclick=()=>{
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(state,null,1)],{type:'application/json'}));
  a.download='cover-framing.json';a.click();document.getElementById('msg').textContent='Saved to Downloads/cover-framing.json. Tell Claude "saved".';
};
</script></body></html>'''
open(os.path.join(B, 'REVIEW.html'), 'w').write(page)
print('wrote', os.path.join(B, 'REVIEW.html'))

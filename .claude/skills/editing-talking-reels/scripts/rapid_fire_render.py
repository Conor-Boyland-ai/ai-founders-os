import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SK = os.path.dirname(os.path.abspath(__file__)); S = os.getcwd()
W,H = 1080,1920
cfg = json.load(open(sys.argv[1] if len(sys.argv)>1 else S+"/cfg2.json"))
FONTS = {"inter": ("fonts/Inter.ttf", {"title":"Bold","sub":"Medium","item":"Medium","cta":"Bold"})}  # approved look (the user, 2026-09-29)
def font(role, size):
    path, w = FONTS[cfg["font"]]
    f = ImageFont.truetype(os.path.join(SK,path), size)
    f.set_variation_by_name(w[role]); return f
def fit(role, text, size, maxw):
    while size > 10 and font(role,size).getlength(text) > maxw: size -= 1
    return font(role,size), size
def wrap(text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t=(cur+" "+w).strip()
        if f.getlength(t)<=maxw: cur=t
        else: lines.append(cur); cur=w
    return lines+[cur]
def shadow_text(im, xy, text, f, fill, blur=6, alpha=170):
    sh = Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text(xy,text,font=f,fill=(0,0,0,alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy,text,font=f,fill=fill)

M = cfg["margin"]; items = cfg["items"]; n_items = len(items)
def base():
    im = Image.new("RGBA",(W,H),(0,0,0,0))
    # title: one line, centered, auto-fit to width
    tf, tsz = fit("title", cfg["title"], cfg["title_size"], W-2*M)
    ty = cfg["title_y"]
    shadow_text(im,((W-tf.getlength(cfg["title"]))/2, ty), cfg["title"], tf, "white")
    sf = font("sub", cfg["sub_size"])
    sy = ty + int(tsz*1.25)
    shadow_text(im,((W-sf.getlength(cfg["sub"]))/2, sy), cfg["sub"], sf, (255,255,255,235), blur=5)
    sub_bottom = sy + sf.getbbox(cfg["sub"])[3]
    # CTA
    parts = cfg["cta"]; full = "".join(p[0] for p in parts)
    cy = cfg["cta_y"]
    if parts:
        cf, csz = fit("cta", full, cfg["cta_size"], W-2*M)
        cta_top = cy + cf.getbbox(full)[1]
        x = (W - cf.getlength(full))/2
        for t,c in parts:
            shadow_text(im,(x,cy),t,cf,c); x += cf.getlength(t)
    else:
        cta_top = cy + cfg["cta_size"] + cfg["gap"]
    # box fills the space between subheadline and CTA, equal gaps
    G = cfg["gap"]; bx0, bx1 = cfg["box_x"]
    by0 = sub_bottom + G; by1 = cta_top - G
    pad = cfg["pad"]
    numw_of = lambda f, s: f.getlength("30.") + int(s*0.35)
    inner_w = bx1-bx0-2*pad
    isz = cfg.get("max_item", 60)
    while True:
        f = font("item", isz); cap = f.getbbox("H")[3]-f.getbbox("H")[1]; nw = numw_of(f,isz)
        if cfg.get("wrap"):
            wrapped = [wrap(it["t"], f, inner_w-nw) for it in items]
        else:
            wrapped = [[it["t"]] for it in items]
        ok_w = all(f.getlength(l) <= inner_w-nw for ls in wrapped for l in ls)
        tot = sum(len(w) for w in wrapped); extra = cfg.get("item_gap", 0.0)
        lh = ((by1-by0) - 2*pad - cap) / ((tot-1) + extra*(n_items-1))
        if ok_w and lh >= isz*1.12: break
        isz -= 1
    sh = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle((bx0+4,by0+8,bx1+4,by1+8), cfg["radius"], fill=(0,0,0,80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle((bx0,by0,bx1,by1), cfg["radius"], fill=(255,255,255,255))
    y = by0 + pad + cap; layout = []
    for ls in wrapped:
        ys = []
        for l in ls: ys.append(y); y += lh
        y += extra*lh; layout.append(list(zip(ls, ys)))
    return im, (bx0+pad, layout, f, nw)
im0, (lx, layout, itf, numw) = base()
def state(n):
    im = im0.copy(); d = ImageDraw.Draw(im)
    for i, lines in enumerate(layout):
        d.text((lx, lines[0][1]), f"{i+1}.", font=itf, fill=(20,20,20), anchor="ls")
        if i < n:
            for t, y in lines: d.text((lx+numw, y), t, font=itf, fill=(20,20,20), anchor="ls")
    return im
if cfg.get("sample_only"):
    state(len(items)).save(cfg["sample_out"]); sys.exit()
os.makedirs(S+"/states2", exist_ok=True)
for n in range(len(items)+1): state(n).save(f"{S}/states2/s{n:02d}.png")
t0 = cfg.get("trim_start",0); dur = cfg["duration"]
times = [0]+[max(0,it["s"]-t0-cfg["lead"]) for it in items]
with open(S+"/states2.txt","w") as f:
    for n in range(len(items)+1):
        end = times[n+1] if n+1 < len(times) else dur
        f.write(f"file 'states2/s{n:02d}.png'\nduration {end-times[n]:.3f}\n")
    f.write(f"file 'states2/s{len(items):02d}.png'\n")

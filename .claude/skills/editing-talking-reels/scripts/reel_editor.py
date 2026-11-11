"""Talking-head batch editor (built on the 10/26 batch). Layouts (job "layout"):
  kv  - horizontal raw: headline, visual slot, caption, video band at the bottom (reels 2, 4-6)
  vf  - vertical raw, full frame: headline above his head; "talk": true + talk_<id>.json for on-camera vs
        screencast sections; "splice" lays other footage over [a, b] with his voice kept; "anim" lays an
        anim/*.py layer over the visual slot (or at "anim_y"); "title_center" centres the headline per shot
  See references/talking-head-batch.md.
Usage: python3 <skill>/scripts/reel_editor.py jobs.json [id,id]   (run from the folder holding words_<id>.json)"""
import json, os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SK)
import laptop, grade, paradigm
from laptop import F, W, H, shadow_text, wrap, at

PAL = {"sky": ("#1FB6FF", "#06121F"), "green": ("#22F26B", "#04140B"), "gold": ("#FFC21A", "#160F02")}
def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def HN(size, bold=True): return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if bold else 0)

# ---------- shared drawing ----------
_bg = {}
def background(pal, hole=None):
    key = (pal, tuple(hole) if hole else None)
    if key in _bg: return _bg[key].copy()
    a, bg = PAL[pal]; im = Image.new("RGBA", (W, H), hexrgb(bg) + (255,))
    d = ImageDraw.Draw(im); dot = (255, 255, 255, 14)
    for y in range(15, H, 30):
        for x in range(15, W, 30): d.ellipse((x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=dot)
    if hole:
        x0, y0, x1, y1, r = hole
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
        alpha = np.array(im.split()[3]); alpha[np.array(m) > 0] = 0; im.putalpha(Image.fromarray(alpha))
        # soft accent glow around the video box
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), radius=r + 3, outline=hexrgb(a) + (150,), width=3)
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.2)))
    _bg[key] = im; return im.copy()

_gfx = {}
def graphic(path, size):
    k = (path, size)
    if k not in _gfx:
        g = Image.open(path).convert("RGBA"); c = int(g.width * (1 - 0.86) / 2)
        g = g.crop((c, c, g.width - c, g.height - c)).resize((size, size), Image.LANCZOS)
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size, size), radius=int(size * .06), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(size * .02)); g.putalpha(m); _gfx[k] = g
    return _gfx[k]

def photo_card(path, maxw, maxh, r=28):
    im = Image.open(path).convert("RGB"); s = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width, im.height), radius=r, fill=255); im.putalpha(m)
    return im

def rich_lines(text, f, maxw):
    """[[word]] = accent. Returns lines of [(txt, accent?)]."""
    toks = []
    for part in re.split(r"(\[\[.*?\]\])", text):
        if not part: continue
        acc = part.startswith("[[")
        for w in part.strip("[]").split(): toks.append((w, acc))
    lines, cur = [], []
    for t in toks:
        trial = " ".join(w for w, _ in cur + [t])
        if cur and f.getlength(trial) > maxw: lines.append(cur); cur = [t]
        else: cur.append(t)
    return lines + [cur]

def draw_rich(im, text, cy, size, accent, maxw=940, align_top=False):
    f = HN(size); lines = rich_lines(text, f, maxw); lh = int(size * 1.18)
    y = cy if align_top else cy - lh * len(lines) / 2
    for ln in lines:
        full = " ".join(w for w, _ in ln); x = (W - f.getlength(full)) / 2
        for i, (w, acc) in enumerate(ln):
            seg = w + (" " if i < len(ln) - 1 else "")
            col = hexrgb(accent) if acc else (255, 255, 255)
            shadow_text(im, (x, y), seg, f, fill=col, blur=6, alpha=150)
            x += f.getlength(seg)
        y += lh
    return y

def caption(im, text, y, L):
    cf = F(L["cap_size"], "SemiBold"); lines = wrap(text, cf, W - 2 * L["cap_margin"])
    for ln in lines:
        shadow_text(im, (W / 2, y), ln, cf, anchor="mt", blur=6, alpha=210); y += int(L["cap_size"] * 1.2)

# ---------- layouts ----------
BOX = {"h": (0, 1150, 1080, 1920, 0), "v": (0, 1150, 1080, 1920, 0)}   # visual panel 0-980, captions 980-1150, video edge to edge below

def draw_box(cfg, hook_on, ov, cap):
    pal = cfg["palette"]; accent = PAL[pal][0]; bgc = hexrgb(PAL[pal][1]); split = 1150
    im = Image.new("RGBA", (W, H), bgc + (255,))
    def panel(path, h=980, top=0):
        g = Image.open(path).convert("RGBA")
        if g.height != h: g = g.resize((int(g.width * h / g.height), h), Image.LANCZOS)
        im.alpha_composite(g, ((W - g.width) // 2, top))
    if hook_on:
        if cfg.get("hook_img"): panel(cfg["hook_img"], 700, 0)
        draw_rich(im, cfg["title"], 840, 78, accent, maxw=1000)
    elif ov:
        if "img" in ov: panel(ov["img"])
        elif "cta" in ov: draw_rich(im, f"Comment [[{ov['cta']}]]", 500, 150, accent, maxw=1000)
        else: draw_rich(im, ov["text"], 500, 120, accent, maxw=1000)
    a = np.array(im); a[split:, :, 3] = 0
    for i in range(80): a[split + i, :, :3] = bgc; a[split + i, :, 3] = int(255 * (1 - i / 80) ** 1.6)
    im = Image.fromarray(a)
    if cap:
        size = 72; cf = F(size, "Bold")
        while cf.getlength(cap) > W - 80 and size > 54: size -= 2; cf = F(size, "Bold")
        lines = wrap(cap, cf, W - 80); y = 1065 - (len(lines) * int(size * 1.12)) / 2
        for ln in lines: shadow_text(im, (W / 2, y), ln, cf, anchor="mt", blur=7, alpha=230); y += int(size * 1.12)
    return im

def draw_listicle(cfg, hook_on, ov, cap, label):
    accent = PAL[cfg["palette"]][0]; im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tf = F(58, "SemiBold"); size = 58
    while tf.getlength(cfg["title"]) > W - 140 and size > 48: size -= 1; tf = F(size, "SemiBold")
    tlines = wrap(cfg["title"], tf, W - 140); y = 290
    for ln in tlines: shadow_text(im, (W / 2, y), ln, tf, anchor="mt", blur=6, alpha=200); y += int(size * 1.15)
    if cfg.get("sub"): shadow_text(im, (W / 2, y), cfg["sub"], F(38, "SemiBold"), anchor="mt", blur=6, alpha=200); y += 50
    if label and not (ov and "cta" in ov):
        lf = F(42, "SemiBold"); bb = ImageDraw.Draw(im).textbbox((W / 2, y + 30), label, font=lf, anchor="mt")
        box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((bb[0] - 26, bb[1] - 16, bb[2] + 26, bb[3] + 18), radius=18, fill=(0, 0, 0, 235))
        im.alpha_composite(box); ImageDraw.Draw(im).text((W / 2, y + 30), label, font=lf, fill="white", anchor="mt")
    if ov and "img" in ov:
        pic = photo_card(ov["img"], 760, 640); x = (W - pic.width) // 2; py = 520
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x, py, x + pic.width, py + pic.height), radius=28, fill=(0, 0, 0, 120))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(pic, (x, py))
    if ov and "cta" in ov:
        lf = F(50, "Bold"); txt1, kw = "Comment ", ov["cta"]; wd = lf.getlength(txt1 + kw); x = (W - wd) / 2; yy = y + 26
        box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((x - 30, yy - 18, x + wd + 30, yy + 72), radius=20, fill=(0, 0, 0, 235)); im.alpha_composite(box)
        d = ImageDraw.Draw(im); d.text((x, yy), txt1, font=lf, fill="white"); d.text((x + lf.getlength(txt1), yy), kw, font=lf, fill=hexrgb(accent))
    if cap: caption(im, cap, 1120, {"cap_size": 44, "cap_margin": 90})
    return im


# ---------- layout "kv": headline top, one visual centre, big caption, video bottom (the user's reference layout, 10/20) ----------
SAFE_W, CAP_W = 940, 840   # Instagram safe zone: 70px sides; captions clear of the like/comment column
KV0 = KV = {"title_y": 285, "vis_top": 505, "vis_h": 715, "cap_y": 1305, "vid_y": 1400, "vid_h": 520}
_kvbg = {}
def premium_bg(pal):
    if pal in _kvbg: return _kvbg[pal].copy()
    a, bg = [np.array(hexrgb(c), float) for c in PAL[pal]]
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.ones((H, W, 3)) * bg
    def blob(cx, cy, r, strength):
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        return np.clip(1 - d, 0, 1) ** 2 * strength
    g = blob(540, 850, 760, 0.30) + blob(120, 420, 520, 0.12) + blob(980, 1180, 560, 0.10)
    img = img * (1 - g[..., None]) + a * g[..., None]
    vig = np.clip(np.sqrt(((xx - 540) / 760) ** 2 + ((yy - 900) / 1150) ** 2), 0, 1.4)
    img *= (1 - 0.45 * np.clip(vig - 0.55, 0, 1))[..., None]
    rng = np.random.default_rng(7); img += rng.normal(0, 5.0, (H, W, 1))
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGB").convert("RGBA")
    _kvbg[pal] = im; return im.copy()

def draw_kv(cfg, hook_on, ov, cap, p=1.0, punch=False):
    pal = cfg["palette"]; accent = PAL[pal][0]; bgc = hexrgb(PAL[pal][1]); KV = {**KV0, **cfg.get("kv", {})}
    if punch:   # full-screen close-up of him: only the caption, low and centred
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if cap:
            size = 58; cf = F(size, "Bold")
            while cf.getlength(cap) > W - 100 and size > 42: size -= 2; cf = F(size, "Bold")
            shadow_text(im, (W / 2, 1150), cap, cf, anchor="mt", blur=7, alpha=240)
        return im
    im = premium_bg(pal)
    parts = [p.strip() for p in re.split(r"\s(?=\()", cfg["title"])]          # "(…)" goes on its own line
    size = 80; tf = HN(size); lines = [l for p in parts for l in wrap(p, tf, SAFE_W)]
    while len(lines) > 2 and size > 60: size -= 2; tf = HN(size); lines = [l for p in parts for l in wrap(p, tf, SAFE_W)]
    if len(lines) > 2: size = min(size, int((KV["vis_top"] - KV["title_y"] - 12) / 3 / 1.12)); tf = HN(size); lines = [l for p in parts for l in wrap(p, tf, SAFE_W)]
    y = KV["title_y"]
    for ln in lines[:3]: shadow_text(im, (W / 2, y), ln, tf, anchor="mt", blur=8, alpha=170); y += int(size * 1.12)
    q = min(max(p, 0), 1)                                     # pop-in with a little overshoot: 0.55 -> 1.08 -> 1.0
    e = q; scale_k = (0.55 + 0.53 * (q / 0.7)) if q < 0.7 else (1.08 - 0.08 * ((q - 0.7) / 0.3))
    def vis(path):
        g = load_vis(path); s_ = min(KV["vis_h"] / g.height, 960 / g.width) * scale_k
        g = g.resize((int(g.width * s_), int(g.height * s_)), Image.LANCZOS)
        if q < 0.4: g.putalpha(Image.fromarray((np.array(g.split()[3]) * (q / 0.4)).astype("uint8")))
        im.alpha_composite(g, ((W - g.width) // 2, KV["vis_top"] + (KV["vis_h"] - g.height) // 2))
    if hook_on and cfg.get("_hook_now"): vis(cfg["_hook_now"])
    elif hook_on and cfg.get("hook_img"): vis(cfg["hook_img"])
    elif ov:
        if "img" in ov: vis(ov["img"])
        elif "cta" in ov: draw_rich(im, f"Comment [[{ov['cta']}]]", KV["vis_top"] + KV["vis_h"] / 2, 120, accent, maxw=SAFE_W)
        else: draw_rich(im, ov["text"], KV["vis_top"] + KV["vis_h"] / 2, 96, accent, maxw=SAFE_W)
    a = np.array(im); vy = KV["vid_y"]; a[vy:, :, 3] = 0
    for i in range(70): a[vy + i, :, 3] = int(255 * (1 - i / 70) ** 1.7)
    im = Image.fromarray(a)
    if cap: cap_line(im, cap, KV["cap_y"])
    return im

_vis = {}
def load_vis(path):
    """Visual cropped to its content (glow included), so it fills the slot. Photos get rounded corners."""
    if path not in _vis:
        src = Image.open(path); g = src.convert("RGBA")
        if "A" in src.getbands():
            bb = g.split()[3].point(lambda v: 255 if v > 6 else 0).getbbox()
            if bb: g = g.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), min(g.width, bb[2] + 12), min(g.height, bb[3] + 12)))
        else:
            m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width, g.height), radius=int(min(g.size) * .06), fill=255); g.putalpha(m)
        _vis[path] = g
    return _vis[path]

def pop(p):
    q = min(max(p, 0), 1)
    return q, ((0.55 + 0.53 * (q / 0.7)) if q < 0.7 else (1.08 - 0.08 * ((q - 0.7) / 0.3)))

def fit_vis(path, w, h, p=1.0):
    q, k = pop(p); g = load_vis(path); s_ = min(w / g.width, h / g.height) * k
    g = g.resize((max(1, int(g.width * s_)), max(1, int(g.height * s_))), Image.LANCZOS)
    if q < 0.4: g.putalpha(Image.fromarray((np.array(g.split()[3]) * (q / 0.4)).astype("uint8")))
    return g

def cap_line(im, cap, cy, minsize=42):
    size = 58; cf = F(size, "Bold")
    while cf.getlength(cap) > CAP_W and size > minsize: size -= 2; cf = F(size, "Bold")
    shadow_text(im, (W / 2, cy - size / 2), cap, cf, anchor="mt", blur=7, alpha=235)

# ---------- layout "vf": full-frame vertical video; headline + one visual in the space above his head ----------
_shade = {}
def top_shade(ht):
    if ht not in _shade:
        a = np.zeros((H, W, 4), "uint8"); y = np.arange(H, dtype=float)
        al = 170 * np.clip(1 - y / ht, 0, 1) ** 1.3; a[..., 3] = al[:, None].astype("uint8")
        _shade[ht] = Image.fromarray(a, "RGBA")
    return _shade[ht]

def draw_title(im, title, y, size0, maxw=None):
    maxw = maxw or SAFE_W
    parts = [p.strip() for p in re.split(r"\s(?=\()", title)]
    size = size0
    while True:
        tf = HN(size); lines = [l for p in parts for l in wrap(p, tf, maxw)]
        if len(lines) <= 3 or size <= 48: break
        size -= 2
    for ln in lines: shadow_text(im, (W / 2, y), ln, tf, anchor="mt", blur=8, alpha=200); y += int(size * 1.12)
    return y

def draw_vf(cfg, hk, ov, cap, lab=None, p=1.0, hook_pic=True, tk=None):
    accent = PAL[cfg["palette"]][0]; ht = cfg["head_top"]
    if cfg.get("talk") and not hk:
        # screencast reels: on camera = headline (or a logo moment in its place) above his head; screencast = captions only
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if tk is not None:
            ht = tk[2]; im.alpha_composite(top_shade(ht)); y0 = tk[3] if len(tk) > 3 else cfg.get("title_y", 150)
            if ov and not ("img" in ov or "cta" in ov): ov = None   # a clear marker
            if ov and ov.get("box"):                               # a visual placed where he points, headline stays (unless solo)
                bx = ov["box"]; g = fit_vis(ov["img"], bx[2], bx[3], p); im.alpha_composite(g, (bx[0] + (bx[2] - g.width) // 2, bx[1] + (bx[3] - g.height) // 2))
                if ov.get("solo"):
                    if cap: cap_line(im, cap, cfg.get("cap_y", 1400))
                    return im
                ov = None
            if ov:
                box = [90, y0, 900, ht - 25 - y0]
                if "img" in ov:
                    g = fit_vis(ov["img"], box[2], box[3], p); im.alpha_composite(g, (box[0] + (box[2] - g.width) // 2, box[1] + (box[3] - g.height) // 2))
                else: draw_rich(im, f"Comment [[{ov['cta']}]]", box[1] + box[3] / 2, 96, accent, maxw=SAFE_W)
            else:
                t_im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); yb = draw_title(t_im, cfg["title"], y0, cfg.get("title_size", 70))
                if yb + cfg.get("talk_clear", 45) <= ht or (len(tk) > 3 and ht): im.alpha_composite(t_im)          # close-up with no room above his head: headline steps aside, never covers him
        if cap: cap_line(im, cap, cfg.get("cap_y", 1400))
        return im
    if hk and cfg.get("hook_kv"):
        K = {**KV0, **cfg.get("kv", {})}; sw, sh = cfg.get("hook_video_size", (2880, 1864)); s_ = min(960 / sw, K["vis_h"] / sh)
        bw, bh = int(sw * s_) // 2 * 2, int(sh * s_) // 2 * 2; cfg["_hookbox"] = [(W - bw) // 2, K["vis_top"] + (K["vis_h"] - bh) // 2, bw, bh]
        return draw_kv(cfg, True, None, cap)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    show_title = (hk or cfg.get("persist")) and not (ov and ov.get("full"))   # "full": this visual takes the whole space above his head
    if show_title or ov or lab: im.alpha_composite(top_shade(ht))
    y = tk[3] if tk is not None and len(tk) > 3 else cfg.get("title_y", 130)
    if show_title: y = draw_title(im, cfg["title"], y, cfg.get("title_size", 70))
    box = (cfg.get("hook_box") if hk else None) or cfg.get("box") or [90, y + 22, 900, ht - 22 - (y + 22)]
    if ov and ov.get("full") and not hk: box = [90, y, 900, ht - 25 - y]
    if hk: cfg["_hookbox"] = box
    def put(path):
        g = fit_vis(path, box[2], box[3], p); im.alpha_composite(g, (box[0] + (box[2] - g.width) // 2, box[1] + (box[3] - g.height) // 2))
    if hk:
        if cfg.get("hook_img") and hook_pic: put(cfg["hook_img"])
    elif ov and "img" in ov: put(ov["img"])
    elif ov and "cta" in ov: draw_rich(im, f"Comment [[{ov['cta']}]]", box[1] + box[3] / 2, 104, accent, maxw=SAFE_W)
    elif lab:
        n, _, rest = lab.partition(" "); size = 66; lf = HN(size)
        wd = lf.getlength(lab); x = (W - wd) / 2; cy = box[1] + box[3] / 2
        pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle((x - 34, cy - size * .78, x + wd + 34, cy + size * .78), radius=26, fill=(0, 0, 0, 225)); im.alpha_composite(pill)
        d = ImageDraw.Draw(im); d.text((x, cy), n + " ", font=lf, fill=hexrgb(accent), anchor="lm"); d.text((x + lf.getlength(n + " "), cy), rest, font=lf, fill="white", anchor="lm")
    if cap: cap_line(im, cap, cfg.get("cap_y", 1400))
    return im

# ---------- timing ----------
def place_all(P, ovs):
    placed = paradigm.place(P, ovs)
    for a, b in zip(placed, placed[1:]): a[1] = b[0]          # hold each visual until the next one lands: no dead space
    if placed and "cta" not in placed[-1][2]: placed[-1][1] = max(placed[-1][1], P["total"])
    for p in placed:
        if "cta" in p[2]: p[1] = P["total"]
    return placed

def run(cfg):
    cfg.setdefault("max_chars", 26)
    P = laptop.plan(cfg); total, caps = P["total"], P["caps"]
    hook = paradigm.place(P, [{"at": cfg["hook_until"], "text": ""}])
    words = P["words"]; last = cfg["hook_until"].split()[-1]
    hook_end = P["m"](next(w["e"] for w in words if paradigm.norm(w["w"]) == paradigm.norm(last) and P["m"](w["s"]) >= hook[0][0] - 0.01)) + 0.15
    placer = place_all if cfg["layout"] in ("box", "kv", "vf") else paradigm.place
    ovs = [o for o in placer(P, cfg.get("overlays", [])) if o[0] >= hook_end - 0.6]
    for o in ovs:
        if "cta" in o[2]: o[1] = total
    if ovs and cfg["layout"] in ("box", "kv", "vf") and "img" in ovs[0][2] and ovs[0][0] - hook_end < 3: hook_end = ovs[0][0]   # hold the hook until the first visual: no dead space
    if ovs: ovs[0][0] = max(ovs[0][0], hook_end)
    talks = []
    if cfg.get("talk"):                                       # on-camera stretches (raw time, from talkmap.py) -> output time
        off = 0
        for a, b in P["segs"]:
            for ra, rb, h in json.load(open(f"talk_{cfg['id']}.json")):
                x0, x1 = max(a, ra), min(b, rb)
                if x1 - x0 > 0.05:
                    if talks and abs(talks[-1][1] - (off + x0 - a)) < 0.05 and talks[-1][2] == h: talks[-1][1] = off + x1 - a
                    else: talks.append([off + x0 - a, off + x1 - a, h])
            off += b - a
        for sa, sb, *_ in cfg.get("splice", []):            # spliced-in screen footage: not on camera
            talks = [y for x in talks for y in ([[x[0], min(x[1], sa), x[2]]] + [[max(x[0], sb), x[1], x[2]]]) if y[1] > y[0]]
        talks = [x for x in talks if x[1] - x[0] >= 0.05]
        yb = draw_title(Image.new("RGBA", (W, H)), cfg["title"], cfg.get("title_y", 150), cfg.get("title_size", 70))
        fit = [yb + cfg.get("talk_clear", 45) <= h for _, _, h, *_ in talks]   # clear of his hair (per-reel calibration when the face detector runs high)
        if cfg.get("title_center") is not None:            # headline centered between the frame top and his hair, per shot
            ti = Image.new("RGBA", (W, H)); draw_title(ti, cfg["title"], 0, cfg.get("title_size", 70)); ink = ti.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()
            i = 0
            while i < len(talks):
                j = i + 1
                while j < len(talks) and abs(talks[j][0] - talks[j - 1][1]) < 0.05: j += 1
                hair = float(np.median([h for _, _, h, *_ in talks[i:j]])) + cfg["title_center"]
                yc = int(round((hair - (ink[3] - ink[1])) / 2 - ink[1]))
                for q in range(i, j): talks[q].append(yc); fit[q] = (hair - (ink[3] - ink[1])) / 2 >= 60
                i = j
        runs, i = [], 0                                    # contiguous runs of the same decision
        while i < len(talks):
            j = i + 1
            while j < len(talks) and fit[j] == fit[i] and abs(talks[j][0] - talks[j - 1][1]) < 0.05: j += 1
            runs.append((i, j)); i = j
        for r, (i, j) in enumerate(runs):                  # no headline flashes: a short "fits" run wedged against a close-up stays hidden
            if fit[i] and talks[j - 1][1] - talks[i][0] < 1.5:
                near = lambda q: 0 <= q < len(runs) and not fit[runs[q][0]]
                if near(r - 1) or near(r + 1):
                    for q in range(i, j): fit[q] = False
        for i, f in enumerate(fit):
            if not f: talks[i][2] = 0
    labels = []
    if cfg["layout"] in ("listicle", "vf"):
        for marker, lab in cfg.get("labels", []):
            hit = paradigm.place(P, [{"at": marker, "text": ""}])
            if hit: labels.append([hit[0][0], lab])
    punches = []
    for pu in cfg.get("punch", []):
        hit = paradigm.place(P, [{"at": pu["at"], "text": ""}])
        if not hit: continue
        a0 = hit[0][0]
        if pu.get("until"):
            h2 = paradigm.place(P, [{"at": pu["until"], "text": ""}]); b0 = h2[0][0] if h2 else a0 + 2.0
        else: b0 = a0 + pu.get("dur", 2.0)
        punches.append([a0, b0])
    cfg["_punch"] = punches
    POP = [round(0.033 * i, 3) for i in range(1, 12)] if cfg["layout"] in ("kv", "vf") else []
    hp = None
    if cfg.get("hook_pop"):
        hit = paradigm.place(P, [{"at": cfg["hook_pop"], "text": ""}]); hp = hit[0][0] if hit else None
    fam = lambda o: os.path.basename(o.get("img", "")).split("-")[0]       # same framework family (pyramid-1 -> pyramid-2): no re-pop
    starts = [a for i, (a, b, o) in enumerate(ovs) if "img" in o and (i == 0 or fam(ovs[i - 1][2]) != fam(o))]
    seq = cfg.get("hook_seq", []); step = cfg.get("hook_step", 0.5); seq_t = [i * step for i in range(len(seq))]
    events = sorted(set([0.0, hook_end] + [c[0] for c in caps] + [x for a, b, _ in ovs for x in (a, b)] + [t for t, _ in labels]
                        + [a + d for a in starts for d in POP] + [x for ab in punches for x in ab]
                        + ([hp] + [hp + d for d in POP] if hp is not None else [])
                        + [st0 + d for st0 in seq_t for d in [0.0] + POP] + [x for a, b, *_ in talks for x in (a, b)]
                        + [x for a, b, *_ in cfg.get("splice", []) for x in (a, b)]))
    events = [e for e in events if e < total - 1e-3]
    states = []
    for i, t in enumerate(events):
        end = events[i + 1] if i + 1 < len(events) else total
        if end - t < 1e-3: continue
        hk = t < hook_end - 1e-6
        ov = next((o for a, b, o in ovs if a - 1e-6 <= t < b - 1e-6), None)
        cap = at(t, caps)
        if cfg["layout"] == "listicle":
            lab = at(t, labels)
            if hk and cfg.get("hook_img"): ov = {"img": cfg["hook_img"]}
            states.append((t, end, (lambda ov=ov, cap=cap, lab=lab, hk=hk: draw_listicle(cfg, hk, ov, cap, lab))))
        elif cfg["layout"] == "kv":
            st = next((a for a in starts if a - 1e-6 <= t < a + 0.4), None)
            pr = 1.0 if (hk or st is None) else (t - st + 0.033) / 0.4
            now = None
            if hk and seq:
                i = max(k for k, a in enumerate(seq_t) if a <= t + 1e-6); now = seq[i]
                pr = min(1.0, (t - seq_t[i] + 0.033) / 0.4) if i == 0 else min(1.0, 0.75 + (t - seq_t[i] + 0.033) / 0.4 * 0.25)
            pun = any(a - 1e-6 <= t < b - 1e-6 for a, b in punches)
            states.append((t, end, (lambda hk=hk, ov=ov, cap=cap, pr=pr, pun=pun, now=now: draw_kv({**cfg, "_hook_now": now}, hk, ov, cap, pr, pun))))
        elif cfg["layout"] == "vf" and any(a - 1e-6 <= t < b - 1e-6 for a, b, *_ in cfg.get("splice", [])):
            states.append((t, end, (lambda cap=cap: draw_vf(cfg, False, None, cap, tk=None))))
        elif cfg["layout"] == "vf":
            lab = at(t, labels)
            st = next((a for a in starts if a - 1e-6 <= t < a + 0.4), None)
            pr = 1.0 if (hk or st is None) else (t - st + 0.033) / 0.4
            pic = True
            if hk and hp is not None:
                pic = t >= hp - 1e-6; pr = min(1.0, (t - hp + 0.033) / 0.4) if pic else 1.0
            tk = next((x for x in talks if x[0] - 1e-6 <= t < x[1] - 1e-6), None)
            if cfg.get("talk"):                                # a visual only shows in the on-camera stretch where it was said
                ova = next((a for a, b, o in ovs if a - 1e-6 <= t < b - 1e-6), None)
                stretch = None                                 # the whole contiguous on-camera stretch this second belongs to
                if tk:
                    i0 = talks.index(tk); a0 = i0; b0 = i0
                    while a0 > 0 and abs(talks[a0][0] - talks[a0 - 1][1]) < 0.05: a0 -= 1
                    while b0 < len(talks) - 1 and abs(talks[b0 + 1][0] - talks[b0][1]) < 0.05: b0 += 1
                    stretch = (talks[a0][0], talks[b0][1])
                if ov is not None and not (stretch and stretch[0] - 0.3 <= ova < stretch[1]): ov = None
                if ov is not None and ova is not None and t - ova > ov.get("dur", 4.0) - 1e-6 and "cta" not in ov: ov = None   # logo moment: 4s, then the headline is back
            states.append((t, end, (lambda hk=hk, ov=ov, cap=cap, lab=lab, pr=pr, pic=pic, tk=tk: draw_vf(cfg, hk, ov, cap, lab, pr, pic, tk))))
        else:
            states.append((t, end, (lambda hk=hk, ov=ov, cap=cap: draw_box(cfg, hk, ov, cap))))
    cfg["_hook_end"] = hook_end; render(cfg, P, states)
    print(f"   hook ends {hook_end:.2f}s")
    for a, b, o in ovs: print(f"   {a:6.2f}-{b:6.2f}  {o.get('cta') or o.get('text') or os.path.basename(o.get('img', '')) or '(clear)'}")

def hv_chain(cfg):
    """Hook video (e.g. a screen recording) playing inside the hook box until the hook ends."""
    if not cfg.get("hook_video"): return ""
    x, y, bw, bh = cfg["_hookbox"]; sw, sh = cfg.get("hook_video_size", (2880, 1864))
    cw = cfg.get("hook_video_cw", sw); ch = min(sh, int(cw * bh / bw)); cx = (sw - cw) // 2; cy = cfg.get("hook_video_cy", (sh - ch) // 2)
    return (f"[m];[2:v]crop={cw}:{ch}:{cx}:{cy},scale={bw}:{bh},fps=30,setpts=PTS-STARTPTS[hv];"
            f"[m][hv]overlay={x}:{y}:eof_action=pass:enable='lt(t,{cfg['_hook_end']:.3f})'")

def anim_chain(cfg):
    """Animated framework layer (anim*.py) laid over the visual slot."""
    if not cfg.get("anim"): return ""
    K = {**KV0, **cfg.get("kv", {})}
    n = 2 + (1 if cfg.get("hook_video") else 0) + len(cfg.get("splice", []))   # input order: raw, states, hook video, splices, anim
    return f"[am];[{n}:v]fps=30,format=rgba[an];[am][an]overlay=0:{cfg.get('anim_y', K['vis_top'])}:eof_action=pass"

def render(cfg, P, states):
    S = os.getcwd(); k, raw, segs = cfg["id"], P["raw"], P["segs"]; json.dump(segs, open(f"segs_{k}.json", "w")); SFPS = laptop.SFPS; FPS = 30; FF = laptop.FF
    os.makedirs(f"{S}/st_{k}", exist_ok=True); lines = []
    for i, (t, end, draw) in enumerate(states):
        draw().save(f"{S}/st_{k}/s{i:03d}.png"); lines.append(f"file 'st_{k}/s{i:03d}.png'\nduration {end - t:.4f}\n")
    lines.append(f"file 'st_{k}/s{len(states) - 1:03d}.png'\n"); open(f"{S}/st_{k}.txt", "w").write("".join(lines))
    fr = [(int(round(a * SFPS)), int(round(b * SFPS))) for a, b in segs]
    vsel = "+".join(f"between(n,{fa},{fb - 1})" for fa, fb in fr)
    total = sum(fb - fa for fa, fb in fr) / SFPS
    gf = grade.grade_filter(raw, cfg.get("grade_strength", 0.5), cfg.get("grade_lift", 0.5)) if cfg.get("grade", True) else "null"
    n = len(fr)
    atr = "".join(f"[as{i}]atrim=start={fa / SFPS:.6f}:end={fb / SFPS:.6f},asetpts=PTS-STARTPTS[at{i}];" for i, (fa, fb) in enumerate(fr))
    base = f"[0:v]select='{vsel}',setpts=N/({SFPS}*TB),fps={FPS},{gf}"
    if cfg["layout"] == "kv":
        KV = {**KV0, **cfg.get("kv", {})}; vy, vh = KV["vid_y"], KV["vid_h"]
        if cfg["orient"] == "h":
            ch = int(1920 * vh / 1080); cy = cfg.get("crop_y", 40)
            place = f",crop=1920:{ch}:0:{cy},scale=1080:{vh}[vid];"
        else:
            ch = int(1080 * vh / 1080); cy = cfg.get("crop_y", 420)
            place = f",crop=1080:{ch}:0:{cy},scale=1080:{vh}[vid];"
        pun = cfg.get("_punch", [])
        if pun:
            fx = cfg.get("face_x", 960) if cfg["orient"] == "h" else 540
            if cfg["orient"] == "h": full = f"crop=608:1080:{max(0, min(1920 - 608, fx - 304))}:0,scale=1080:1920"
            else: full = "null"
            en = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in pun)
            vchain = (base + ",split=2[b1][b2];[b1]" + place.lstrip(",") + f"[b2]{full}[full];"
                      f"color=c=black:s={W}x{H}:r={FPS}:d={total:.3f}[cv];[cv][vid]overlay=0:{vy}:shortest=1[bg0];[bg0][full]overlay=0:0:enable='{en}'[bg];")
        else:
            vchain = base + place + f"color=c=black:s={W}x{H}:r={FPS}:d={total:.3f}[cv];[cv][vid]overlay=0:{vy}:shortest=1[bg];"
    elif cfg["layout"] == "box":
        x0, y0, x1, y1, r = BOX[cfg["orient"]]; bw, bh = x1 - x0, y1 - y0
        if cfg["orient"] == "h":   # 1920x1080 raw: crop to the bottom area's aspect around him, then scale to fill
            cw = int(1080 * bw / bh); cx = cfg.get("crop_x", (1920 - cw) // 2)
            place = f",crop={cw}:1080:{cx}:0,scale={bw}:{bh}[vid];"   # stretch edge to edge
        else:   # vertical raw: crop the head-and-shoulders band to the bottom area's aspect
            cy = cfg.get("crop_y", 330); ch = int(1080 * bh / bw)
            place = f",crop=1080:{ch}:0:{cy},scale={bw}:{bh}[vid];"
        vchain = base + place + f"color=c=black:s={W}x{H}:r={FPS}:d={total:.3f}[cv];[cv][vid]overlay={x0}:{y0}:shortest=1[bg];"
    elif cfg["layout"] == "vf" and cfg.get("hook_kv"):
        K = {**KV0, **cfg.get("kv", {})}; vy, vh = K["vid_y"], K["vid_h"]
        vchain = (base + f",scale={W}:{H},split=2[full][k0];[k0]crop=1080:{vh}:0:{cfg.get('crop_y', 420)},scale=1080:{vh}[kvv];"
                  f"color=c=black:s={W}x{H}:r={FPS}:d={total:.3f}[cv];[cv][kvv]overlay=0:{vy}:shortest=1[kvb];"
                  f"[full][kvb]overlay=0:0:enable='lt(t,{cfg['_hook_end']:.3f})'[bg];")
    elif cfg["layout"] == "vf":
        sp = cfg.get("splice", []); nin = 3 if cfg.get("hook_video") else 2
        vchain = base + f",scale={W}:{H}" + ("[bg];" if not sp else "[sp0];")
        for i, (a, b, ra, *src) in enumerate(sp):        # screen footage (from the raw, or another file) laid over [a, b]
            vchain += (f"[{nin + i}:v]setpts=PTS-STARTPTS+{a}/TB,fps={FPS},{'null' if src else gf},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[spv{i}];"
                       f"[sp{i}][spv{i}]overlay=0:0:eof_action=pass:enable='between(t,{a},{b})'" + ("[bg];" if i == len(sp) - 1 else f"[sp{i + 1}];"))
    else:
        vchain = base + "[bg];"
    fc = (vchain + f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n)) + ";" + atr + "".join(f"[at{i}]" for i in range(n)) +
          f"concat=n={n}:v=0:a=1[ac];[ac]afade=t=in:d=0.005,afade=t=out:st={total - 0.03:.3f}:d=0.03[a];"
          f"[1:v]fps={FPS},format=rgba[ov];[bg][ov]overlay=eof_action=repeat:shortest=1" + hv_chain(cfg) + anim_chain(cfg) + ",format=yuv420p[v]")
    out = cfg["out"]
    extra = ["-t", "8", "-i", cfg["hook_video"]] if cfg.get("hook_video") else []
    for a, b, ra, *src in cfg.get("splice", []): extra += ["-ss", f"{ra}", "-t", f"{b - a + 0.1:.3f}", "-i", src[0] if src else raw]
    if cfg.get("anim"): extra += ["-i", cfg["anim"]]
    subprocess.run([FF, "-loglevel", "warning", "-y", "-i", raw, "-f", "concat", "-safe", "0", "-i", f"{S}/st_{k}.txt", *extra,
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    probe = subprocess.run([FF, "-hide_banner", "-i", out], capture_output=True, text=True).stderr
    if "displaymatrix" in probe:
        tmp = out + ".fix.mp4"; subprocess.run([FF, "-loglevel", "error", "-y", "-display_rotation:v:0", "0", "-i", out, "-map", "0", "-c", "copy", "-movflags", "+faststart", tmp], check=True); os.replace(tmp, out)
    print(k, f"-> {total:.1f}s, {len(segs)} segments, {len(states)} overlay states")

if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    for j in jobs:
        if len(sys.argv) < 3 or j["id"] in sys.argv[2].split(","): run(j)

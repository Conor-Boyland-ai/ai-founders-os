"""Paradigm shift (formula 6): talking head + hook faces + pop-up image/text overlays on the lines they illustrate.
Usage: python3 paradigm.py jobs.json [id,id]   (run from the working folder that holds words_<id>.json)"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import laptop
from laptop import F, W, H, shadow_text, wrap, at

EMOJI = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)
GREEN = (18, 161, 80)
LAYOUT = {"margin": 70, "band_top": 270, "band_bottom": 540, "cap_y": 1180, "cap_size": 46, "cap_margin": 90,
          "tile_h": 200, "tile_gap": 14, "title_size": 46, "title_gap": 12, "card_size": 52, "card_pad": 24,
          "radius": 16, "img_max_w": 800}
HOLD = 3.5      # seconds an image stays up (the user 10/1: keep them on longer)
BRIDGE = 1.5    # if the next overlay starts within this gap, hold until it arrives instead of blinking off

def is_emoji(ch): return ord(ch) > 0x2600

def text_run(d, im, x, y, text, f, fill):
    """Draw text with inline colour emoji (Inter has none). y = top. Returns width."""
    size = f.size; cx = x
    for part in re.findall(r"[\U0001F000-\U0001FFFF☀-➿]️?|[^\U0001F000-\U0001FFFF☀-➿]+", text):
        if is_emoji(part[0]):
            e = Image.new("RGBA", (180, 180)); ImageDraw.Draw(e).text((0, 0), part, font=EMOJI, embedded_color=True)
            e = e.crop(e.getbbox()); s = int(size * 0.95); e = e.resize((s, s), Image.LANCZOS)
            if im is not None: im.alpha_composite(e, (int(cx), int(y + size * 0.08)))
            cx += s + size * 0.12
        else:
            if im is not None: d.text((cx, y), part, font=f, fill=fill)
            cx += f.getlength(part)
    return cx - x

def card(im, lines, y_center, L, fills=None):
    """White rounded card with bold black lines (the user's hook-box style), centred at y_center."""
    f = F(L["card_size"], "Bold"); d = ImageDraw.Draw(im); lh = int(L["card_size"] * 1.18); pad = L["card_pad"]
    widths = [text_run(d, None, 0, 0, ln, f, None) for ln in lines]
    bw = max(widths) + 2 * pad; bh = lh * len(lines) + pad * 1.2
    l, t = (W - bw) / 2, y_center - bh / 2
    shadow(im, (l, t, l + bw, t + bh), L["radius"])
    ImageDraw.Draw(im).rounded_rectangle((l, t, l + bw, t + bh), radius=L["radius"], fill=(255, 255, 255, 248))
    y = t + pad * 0.6
    for i, ln in enumerate(lines):
        x = (W - widths[i]) / 2
        segs = fills[i] if fills else [(ln, (10, 10, 10))]
        for txt, col in segs:
            x += text_run(d, im, x, y, txt, f, col)
        y += lh
    return t, t + bh

def shadow(im, box, r, alpha=90, blur=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, radius=r, fill=(0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

def rounded(img, r):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width, img.height), radius=r, fill=255)
    img = img.convert("RGBA"); img.putalpha(m); return img

def cover(path, w, h):
    im = Image.open(path).convert("RGB"); s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    l = (im.width - w) // 2; t = max(0, int((im.height - h) * 0.3))   # bias up: keep faces
    return im.crop((l, t, l + w, t + h))

def fit(path, mw, mh):
    im = Image.open(path).convert("RGB"); s = min(mw / im.width, mh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

def draw(cfg, hook_on, ov, caption):
    L = {**LAYOUT, **cfg.get("layout", {})}; im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    title_bottom = 0
    if hook_on:
        imgs = cfg.get("hook_images", []); n = len(imgs)
        if n:
            avail = W - 2 * L["margin"]; th = L["tile_h"]
            tw = min(int((avail - (n - 1) * L["tile_gap"]) / n), int(th * (0.78 if n > 1 else 1.6)))
            x = (W - (n * tw + (n - 1) * L["tile_gap"])) / 2
            for p in imgs:
                tile = rounded(cover(p, tw, th), L["radius"]); shadow(im, (x, L["band_top"], x + tw, L["band_top"] + th), L["radius"])
                im.alpha_composite(tile, (int(x), L["band_top"])); x += tw + L["tile_gap"]
            ty = L["band_top"] + th + L["title_gap"]
        else: ty = L["band_top"]
        TL = {**L, "card_size": L["title_size"]}; tl = wrap_lines(cfg["title"], TL)
        hgt = int(TL["card_size"] * 1.18) * len(tl) + TL["card_pad"] * 1.2
        _, title_bottom = card(im, tl, ty + hgt / 2, TL)
    elif ov:
        if "img" in ov:
            mw, mh = min(L["img_max_w"], W - 2 * L["margin"]), L["band_bottom"] - L["band_top"]
            pic = rounded(fit(ov["img"], mw, mh), L["radius"]); x = (W - pic.width) // 2; y = L["band_bottom"] - pic.height
            shadow(im, (x, y, x + pic.width, y + pic.height), L["radius"]); im.alpha_composite(pic, (x, y))
        else:
            if "cta" in ov:
                kw = ov["cta"]; lines = [f"Comment {kw}"]; fills = [[("Comment ", (10, 10, 10)), (kw, GREEN)]]
            else:
                lines = wrap_lines(ov["text"], L); fills = None
            hgt = int(L["card_size"] * 1.18) * len(lines) + L["card_pad"] * 1.2
            card(im, lines, L["band_bottom"] - hgt / 2, L, fills)
    if caption:
        cf = F(L["cap_size"], "SemiBold"); lines = wrap(caption, cf, W - 2 * L["cap_margin"])
        y = min(L["cap_y"], 1244 - int(L["cap_size"] * 1.2) * len(lines))   # as low as possible, never past Instagram's y=1248 cutoff
        for line in lines:
            shadow_text(im, (W / 2, y), line, cf, anchor="mt", blur=6, alpha=210); y += int(L["cap_size"] * 1.2)
    return im

def wrap_card(text, L):
    """Fewest lines that fit, then balanced so no word sits alone on the last line."""
    f = F(L["card_size"], "Bold"); maxw = W - 2 * L["margin"] - 2 * L["card_pad"]
    width = lambda t: text_run(None, None, 0, 0, t, f, None)
    def lines(mw):
        out, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if width(t) <= mw or not cur: cur = t
            else: out.append(cur); cur = w
        return out + [cur]
    best = lines(maxw); n = len(best); mw = maxw
    while n > 1 and mw > 200:
        trial = lines(mw - 10)
        if len(trial) > n: break
        best, mw = trial, mw - 10
    return best

def wrap_lines(text, L):
    return [ln for para in text.split("\n") for ln in wrap_card(para, L)]

norm = lambda s: re.sub(r"[^a-z0-9$]", "", s.lower())

def place(P, ovs):
    """Find each overlay's spoken phrase (in order) and time it on the cut video."""
    words = P["words"]; toks = [norm(w["w"]) for w in words]; m, total = P["m"], P["total"]; out = []; pos = 0
    for o in ovs:
        ph = [norm(x) for x in o["at"].split() if norm(x)]
        hit = next((i for i in range(pos, len(toks) - len(ph) + 1) if toks[i:i + len(ph)] == ph), None)
        src = words
        if hit is None:                                   # main transcript dropped it: try the backup pass
            at_ = [norm(w["w"]) for w in P.get("alt", [])]
            ahit = next((i for i in range(len(at_) - len(ph) + 1) if at_[i:i + len(ph)] == ph), None)
            if ahit is None:
                print(f"!! phrase not found, overlay skipped: {o['at']!r}"); continue
            src, hit = P["alt"], ahit
        else: pos = hit + len(ph)
        t = m(src[hit]["s"]); end_said = m(src[hit + len(ph) - 1]["e"])
        if "cta" in o: end = total
        elif "img" in o: end = t + o.get("dur", HOLD)
        else: end = max(end_said + 0.6, t + o.get("dur", 2.8))
        out.append([t, end, o])
    for a, b in zip(out, out[1:]):
        if b[0] - a[1] <= BRIDGE: a[1] = b[0]                       # small gap: hold until the next one lands
        a[1] = min(a[1], b[0])                                       # never stack two overlays
    return out

def run(cfg):
    P = laptop.plan(cfg); words, total, caps, m0 = P["words"], P["total"], P["caps"], P["m0"]
    if cfg.get("hook_until"):
        hit = place(P, [{"at": cfg["hook_until"], "text": ""}])
        hook_end = P["m"](next(w["e"] for w in words if norm(w["w"]) == norm(cfg["hook_until"].split()[-1]) and P["m"](w["s"]) >= hit[0][0] - 0.01)) + 0.15
    elif cfg.get("hook_secs"): hook_end = cfg["hook_secs"]
    else:
        first = next((w for w in words if w["w"][-1:] in ".?!"), words[min(len(words) - 1, 12)])
        hook_end = min(max(m0(first["e"]) + 0.2, 3.0), 8.0)
    ovs = [o for o in place(P, cfg.get("overlays", [])) if o[0] >= hook_end - 0.05]
    events = sorted(set([0.0, hook_end] + [c[0] for c in caps] + [x for a, b, _ in ovs for x in (a, b)]))
    events = [e for e in events if e < total - 1e-3]
    states = []
    for i, t in enumerate(events):
        end = events[i + 1] if i + 1 < len(events) else total
        if end - t < 1e-3: continue
        hk = t < hook_end - 1e-6
        ov = next((o for a, b, o in ovs if a - 1e-6 <= t < b - 1e-6), None)
        states.append((t, end, (lambda hk=hk, ov=ov, cap=at(t, caps): draw(cfg, hk, ov, cap))))
    laptop.render(cfg, P, states)
    for a, b, o in ovs: print(f"   {a:6.2f}-{b:6.2f}  {o.get('cta') or o.get('text') or os.path.basename(o['img'])}")

if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    for j in jobs:
        if len(sys.argv) < 3 or j["id"] in sys.argv[2].split(","): run(j)

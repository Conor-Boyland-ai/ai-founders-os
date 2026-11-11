"""Render IG story images from a job file: photo cropped to 9:16, text in IG-style rounded boxes kept off his face.
Usage: python3 make_stories.py job.json   ->  <out>/story_<n>.jpg, sheet.jpg, preview.html
Job: {"out": "/folder", "stories": [{"image": "/path.jpg" | null (black), "when": "Wed Oct 21 · 4:00 PM",
       "text_y": 1350, "focus_x": 0.5, "zoom": 1.0, "anchor": "center|top|bottom", "paragraphs": ["...", "..."]}]}
text_y = centre of the text block (1080x1920 frame). zoom + anchor move his face away from the text when space is tight."""
import base64, io, json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
KEYWORD_COLOR = (255, 209, 26)
FONT = lambda s: ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", s, index=1)

def load(path):
    if path.lower().endswith((".heic", ".heif")):                      # PIL can't read HEIC: convert with macOS sips
        tmp = os.path.join("/tmp", os.path.basename(path) + ".jpg"); os.system(f'sips -s format jpeg "{path}" --out "{tmp}" >/dev/null'); path = tmp
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")

def cover(st):
    im = load(st["image"]); z = st.get("zoom", 1.0); anchor = st.get("anchor", "center")
    s = max(W / im.width, H / im.height) * z; im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(0, int(im.width * st.get("focus_x", 0.5) - W / 2)), im.width - W)
    y = 0 if anchor == "top" else im.height - H if anchor == "bottom" else (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))

def wrap(txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def draw(st, keyword):
    img = st.get("image"); im = (cover(st) if img else Image.new("RGB", (W, H), (0, 0, 0))).convert("RGBA")
    size = 46; f = FONT(size); lh = int(size * 1.28); padx, pady, gap = 34, 26, 22
    blocks = [wrap(p, f, 860) for p in st["paragraphs"]]
    hs = [len(b) * lh + 2 * pady for b in blocks]; total = sum(hs) + gap * (len(blocks) - 1)
    y = int(st.get("text_y", 960) - total / 2); y = max(270, min(y, H - 300 - total))   # clear of the story top bar and reply bar
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for b, h in zip(blocks, hs):
        bw = max(f.getlength(l) for l in b) + 2 * padx
        if img: d.rounded_rectangle(((W - bw) / 2, y, (W + bw) / 2, y + h), radius=22, fill=(0, 0, 0, 185))
        ty = y + pady
        for l in b:
            if keyword and keyword in l:                                   # CTA keyword in yellow
                a, _, c = l.partition(keyword); x = (W - f.getlength(l)) / 2
                for part, col in ((a, "white"), (keyword, KEYWORD_COLOR), (c, "white")):
                    d.text((x, ty), part, font=f, fill=col); x += f.getlength(part)
            else: d.text((W / 2, ty), l, font=f, fill="white", anchor="ma")
            ty += lh
        y += h + gap
    im.alpha_composite(ov); return im.convert("RGB")

def preview_html(paths, whens, title):
    cards = []
    for i, (p, w) in enumerate(zip(paths, whens)):
        b = io.BytesIO(); Image.open(p).resize((720, 1280), Image.LANCZOS).save(b, "JPEG", quality=86)
        src = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
        cards.append(f'<figure class="s"><div class="ph"><img src="{src}" alt="Story {i + 1}"></div><figcaption><b>Story {i + 1}</b><span>{w}</span></figcaption></figure>')
    return f'''<title>{title}</title><meta name="claude:viewport-fit-sides" content="cover">
<style>:root{{--bg:#f3f2f0;--fg:#18181b;--mu:#6b6b72;--fr:#111114}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#141416;--fg:#f2f2f3;--mu:#9a9aa2;--fr:#000;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#141416;--fg:#f2f2f3;--mu:#9a9aa2;--fr:#000;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}}
main{{max-width:1400px;margin:0 auto;padding-block:28px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}.s{{margin:0;display:flex;flex-direction:column;gap:10px}}
.ph{{background:var(--fr);border-radius:22px;padding:6px}}.ph img{{display:block;width:100%;aspect-ratio:9/16;border-radius:17px}}
figcaption{{display:flex;justify-content:space-between;gap:8px;font-size:.85rem}}figcaption span{{color:var(--mu)}}</style>
<main><h1>{title}</h1><div class="g">{"".join(cards)}</div></main>'''

if __name__ == "__main__":
    job = json.load(open(sys.argv[1])); out = job["out"]; os.makedirs(out, exist_ok=True); kw = job.get("keyword")
    paths = []
    for i, st in enumerate(job["stories"]):
        p = os.path.join(out, f"story_{i + 1}.jpg"); draw(st, kw).save(p, quality=92); paths.append(p)
    sheet = Image.new("RGB", (280 * len(paths), 480), (40, 40, 40))
    for i, p in enumerate(paths): sheet.paste(Image.open(p).resize((270, 480)), (i * 280, 0))
    sheet.save(os.path.join(out, "sheet.jpg"), quality=88)
    open(os.path.join(out, "preview.html"), "w").write(preview_html(paths, [s.get("when", "") for s in job["stories"]], job.get("title", "Story Preview")))
    print("rendered", len(paths), "->", out)

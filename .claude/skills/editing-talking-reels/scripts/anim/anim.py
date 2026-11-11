"""Animated framework visuals for the band reels (4, 5, 6): every element lands on the word that names it.
Draws the visual slot (1080x715, above the video band) at 30fps into a transparent .mov the editor lays over the reel."""
import json, math, os, random, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
VO = os.environ.get("VISUAL_OVERLAY_DIR", os.path.join(os.getcwd(), "visual overlay"))
LOGO = VO + "/anim-assets/{}-c.png"
CW, CH, S, FPS = 1080, 715, 2, 30
PAL = {"sky": (31, 182, 255), "green": (34, 242, 107), "gold": (255, 194, 26)}
WHITE, GRAY, RED, OK = (255, 255, 255), (150, 156, 168), (255, 77, 77), (43, 217, 107)
PANEL = (16, 18, 24)

# ---------- timing ----------
def clamp(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def eback(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, t0, d): return clamp((t - t0) / d)
def norm(w): return re.sub(r"[^a-z0-9%]", "", w.lower())

class Cues:
    def __init__(self, path):
        d = json.load(open(path)); self.total = d["total"]; self.words = d["words"]
        self.n = [norm(w["w"]) for w in self.words]
    def at(self, phrase, after=0.0, end=False):
        ph = [norm(p) for p in phrase.split()]
        for i in range(len(self.n) - len(ph) + 1):
            if self.words[i]["s"] >= after - 1e-6 and self.n[i:i + len(ph)] == ph:
                return self.words[i + len(ph) - 1]["e"] if end else self.words[i]["s"]
        raise KeyError(phrase)

# ---------- drawing helpers (scene coords are 1x; everything is drawn at 2x and downsampled) ----------
_font = {}
def font(size):
    k = int(size * S)
    if k not in _font: _font[k] = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", k, index=1)
    return _font[k]

def glowed(im, color, radius=14, strength=1.0):
    r = int(radius * S); pad = r * 3
    big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
    a = big.split()[3].filter(ImageFilter.GaussianBlur(r)); a = a.point(lambda v: min(255, int(v * 1.6 * strength)))
    g = Image.new("RGBA", big.size, color + (0,)); g.putalpha(a)
    g.alpha_composite(big); return g

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def text(txt, size, color=WHITE):
    def mk():
        f = font(size); bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), txt, font=f, fill=color); return im
    return cached(("t", txt, size, color), mk)

def rrect(w, h, r, fill, outline=None, ow=0, glow=None):
    def mk():
        im = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=int(r * S), fill=fill,
                                             outline=outline, width=int(ow * S))
        return glowed(im, glow) if glow else im
    return cached(("r", w, h, r, fill, outline, ow, glow), mk)

def logo(name, size):
    def mk():
        im = Image.open(LOGO.format(name)).convert("RGBA"); s_ = size * S / max(im.size)
        return im.resize((int(im.width * s_), int(im.height * s_)), Image.LANCZOS)
    return cached(("l", name, size), mk)

def mark(kind, size, color, w=7):
    """✓ or ✕ drawn as strokes."""
    def mk():
        n = int(size * S); im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); lw = int(w * S)
        if kind == "check": d.line([(n * .16, n * .54), (n * .42, n * .78), (n * .86, n * .24)], fill=color, width=lw, joint="curve")
        else:
            d.line([(n * .2, n * .2), (n * .8, n * .8)], fill=color, width=lw); d.line([(n * .8, n * .2), (n * .2, n * .8)], fill=color, width=lw)
        return im
    return cached(("m", kind, size, color, w), mk)

def badge(kind, size=56):
    col = OK if kind == "check" else RED
    def mk():
        n = int(size * S); im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse((0, 0, n - 1, n - 1), fill=col)
        m = mark(kind, size * .62, WHITE, 6); im.alpha_composite(m, ((n - m.width) // 2, (n - m.height) // 2)); return im
    return cached(("b", kind, size), mk)

def put(cv, spr, cx, cy, sc=1.0, a=1.0, rot=0.0):
    if spr is None or a <= 0.003 or sc <= 0.01: return
    im = spr
    if abs(sc - 1) > 1e-3: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if a < 0.999:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    x, y = int(cx * S - im.width / 2), int(cy * S - im.height / 2)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(cv.width, x + im.width), min(cv.height, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    cv.alpha_composite(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))

def pop(t, t0, d=0.28):
    """scale/alpha for an element appearing at t0 with a little overshoot."""
    if t < t0: return 0.0, 0.0
    q = prog(t, t0, d); return 0.55 + 0.45 * eback(q), clamp(q / 0.35)

def gone(t, t1, d=0.22):
    """alpha/scale multiplier for an element leaving at t1."""
    if t1 is None or t < t1: return 1.0
    return 1 - eout(prog(t, t1, d))

def shake(t, t0, amp=16, d=0.35, seed=0):
    if t < t0 or t > t0 + d: return 0.0, 0.0
    k = 1 - (t - t0) / d; rnd = random.Random(int(t * FPS) * 7 + seed)
    return rnd.uniform(-1, 1) * amp * k, rnd.uniform(-1, 1) * amp * k

def card(w, h, accent, ow=4, glow=True):
    return rrect(w, h, 26, PANEL + (238,), accent, ow, accent if glow else None)

def chip(label, accent, size=40, pad=34, h=86, fill=None, tc=WHITE):
    tw = text(label, size, tc).width / S; w = tw + 2 * pad
    def mk():
        base = rrect(w, h, h / 2, fill or (PANEL + (240,)), accent, 4, accent).copy()
        t_ = text(label, size, tc); base.alpha_composite(t_, ((base.width - t_.width) // 2, (base.height - t_.height) // 2)); return base
    return cached(("c", label, accent, size, pad, h, fill, tc), mk)

def pyramid_level(i, accent, label, wide=820, tall=540, n=5):
    """level i (0 = base) of a 5-level pyramid, as a sprite + its centre offset from the pyramid centre."""
    lh = tall / n; gap = 10; apex = 150
    def width_at(y_from_top): return apex + (wide - apex) * (y_from_top / tall)
    top = tall - (i + 1) * lh; bot = tall - i * lh - gap
    wt, wb = width_at(top), width_at(bot + gap)
    def mk():
        W_, H_ = int(wide * S), int((bot - top) * S)
        im = Image.new("RGBA", (W_ + 4, H_ + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = W_ / 2
        d.polygon([(c - wt * S / 2, 0), (c + wt * S / 2, 0), (c + wb * S / 2, H_), (c - wb * S / 2, H_)], fill=accent + (255,))
        sz = 34 if i < 4 else 28
        t_ = text(label, sz, (10, 12, 16)); im.alpha_composite(t_, (int(c - t_.width / 2), int(H_ / 2 - t_.height / 2)))
        return glowed(im, accent, 10, 0.7)
    spr = cached(("p", i, accent, label, wide, tall), mk)
    return spr, (top + bot) / 2 - tall / 2

PYR = ["CONTEXT", "SKILLS", "VOICE", "AGENTS", "CONNECTORS"]

def draw_pyramid(cv, t, accent, starts, cx, cy, sc=1.0, a=1.0, glow_level=None, gl=0.0, sweep=None):
    for i, t0 in enumerate(starts):
        s_, al = pop(t, t0, 0.3)
        if al <= 0: continue
        spr, dy = pyramid_level(i, accent, PYR[i])
        put(cv, spr, cx, cy + dy * sc, sc * s_, al * a)
        lit = (glow_level == i and gl > 0) or (sweep is not None and abs(sweep - i) < 0.6)
        if lit:
            k = gl if glow_level == i else 1 - abs(sweep - i) / 0.6
            put(cv, glowed(spr, (255, 255, 255), 18, 1.2), cx, cy + dy * sc, sc * s_, al * a * 0.55 * k)

def stamp(cv, t, t0, word, color, cx, cy, size=120, rot=-12):
    if t < t0: return
    q = prog(t, t0, 0.16); sc = 1.9 - 0.9 * eout(q)
    def mk():
        tx = text(word, size, color); pad = int(26 * S)
        im = Image.new("RGBA", (tx.width + 2 * pad, tx.height + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((4, 4, im.width - 5, im.height - 5), radius=int(18 * S), outline=color, width=int(9 * S))
        im.alpha_composite(tx, (pad, pad)); return im
    put(cv, cached(("s", word, color, size), mk), cx, cy, sc, clamp(q * 3), rot)

# ---------- render ----------
def render(scene, cues, out, t_end=None, preview=None):
    total = cues.total; n = int(math.ceil((t_end or total) * FPS))
    if preview:
        frames = []
        for t in preview:
            cv = Image.new("RGBA", (CW * S, CH * S), (0, 0, 0, 0)); scene(cv, t); frames.append(cv.resize((CW, CH), Image.LANCZOS))
        return frames
    p = subprocess.Popen([FF, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{CW}x{CH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", "-pix_fmt", "argb", out], stdin=subprocess.PIPE)
    for f in range(n):
        cv = Image.new("RGBA", (CW * S, CH * S), (0, 0, 0, 0)); scene(cv, f / FPS)
        p.stdin.write(cv.resize((CW, CH), Image.LANCZOS).tobytes())
    p.stdin.close(); p.wait(); print(out, n, "frames")

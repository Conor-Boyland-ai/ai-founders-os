"""iPhone screencast format (locked 2026-10-08). Ruthless pause cut, hook in a box from frame 0 until the end of the
verbal hook, standard captions, optional image overlays above his head. Audio untouched except the cuts (5 ms fade per join).
Usage (from a scratchpad working folder that holds words_<id>.json): python3 screencast.py jobs.json [id,id]
Job fields: see references/iphone-screencast.md"""
import json, os, re, sys, subprocess, pickle
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onset, screencast_cut as cut
SK = os.path.dirname(os.path.abspath(__file__))
S = os.getcwd()
FF = onset.FF; W, H = 1080, 1920; FPS = 30
SIDE = 65                      # Instagram side safe margin (6%)
CAP_Y, CAP_SIZE, CAP_MARGIN, MAX_CHARS = 1120, 44, 90, 30   # standard captions (same as listicle.py)

def F(size, w="SemiBold"):
    f = ImageFont.truetype(SK + "/fonts/Inter.ttf", size); f.set_variation_by_name(w); return f

def wrap(text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

def boxed(im, lines, f, size, y, opacity=235):
    """White text on a black rounded box, y = box top. Padding is equal on all four sides, measured cap-top to
    baseline vertically (descenders hang into the bottom pad) and from the drawn letters horizontally."""
    capH = -f.getbbox("H", anchor="ls")[1]
    lh = int(size * 1.22); pad = int(size * 0.5)
    base0 = y + pad + capH
    mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
    for i, line in enumerate(lines): md.text((W / 2, base0 + i * lh), line, font=f, fill=255, anchor="ms")
    l, _, r, _ = mask.point(lambda x: 255 if x > 128 else 0).getbbox()
    top, bot = base0 - capH - pad, base0 + (len(lines) - 1) * lh + pad
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((l - pad, top, r + pad, bot), radius=int(size * 0.35), fill=(0, 0, 0, opacity))
    im.alpha_composite(box)
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines): d.text((W / 2, base0 + i * lh), line, font=f, fill="white", anchor="ms")
    return bot

def shadow_text(im, xy, text, f):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text(xy, text, font=f, fill=(0, 0, 0, 210), anchor="mt")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text(xy, text, font=f, fill="white", anchor="mt")

def fit_hook(text, band, max_size=160):
    """Biggest hook whose box fits inside the side margins and inside band=[top, bottom]. 1-3 balanced lines."""
    words = text.split()
    def splits(n):
        if n == 1: return [[text]]
        out = []
        for i in range(1, len(words)):
            if n == 2: out.append([" ".join(words[:i]), " ".join(words[i:])])
            else:
                for j in range(i + 1, len(words)):
                    out.append([" ".join(words[:i]), " ".join(words[i:j]), " ".join(words[j:])])
        return out
    for size in range(max_size, 30, -2):
        f = F(size); pad = int(size * 0.5); best = None
        for n in (1, 2, 3):
            for lines in splits(n):
                wmax = max(f.getlength(l) for l in lines)
                if wmax + 2 * pad > W - 2 * SIDE: continue
                if int(size * 1.22) * (n - 1) + int(size * 0.73) + 2 * pad > band[1] - band[0]: continue
                bal = wmax - min(f.getlength(l) for l in lines)
                if best is None or (n, bal) < (best[0], best[1]): best = (n, bal, lines)
        if best: return size, best[2]
    return 30, [text]

def frame(cfg, caption, image, hook_on):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L = cfg["layout"]
    if hook_on:
        size, lines = fit_hook(cfg["hook"], L["hook_band"], L.get("hook_max", 160))
        f = F(size); top = L["hook_band"][0]
        hgt = boxed(Image.new("RGBA", (W, H)), lines, f, size, 0)
        boxed(im, lines, f, size, top + max(0, (L["hook_band"][1] - top) - hgt) // 2)
    if image:
        ov = Image.open(image["path"]).convert("RGBA"); top, bot = L["img_area"]
        sc = min((W - 2 * SIDE) / ov.width, (bot - top) / ov.height)
        ov = ov.resize((round(ov.width * sc), round(ov.height * sc)), Image.LANCZOS)
        im.alpha_composite(ov, (round((W - ov.width) / 2), round(top + (bot - top - ov.height) / 2)))
    if caption:
        cf = F(CAP_SIZE); y = L.get("cap_y", CAP_Y)
        for line in wrap(caption, cf, W - 2 * CAP_MARGIN):
            shadow_text(im, (W / 2, y), line, cf); y += int(CAP_SIZE * 1.2)
    return im

MARK = {"one", "two", "three", "four", "five", "1", "2", "3", "4", "5", "finally"}
FUNC = set("a an the to of and or but for as that they you your is are was with on in at about because how if so it's i my their its be by from into than then when what like not this just any who we me do don't can't it has have had every even no more all some can could will would should may might one very really you're we're they're i'm i'll you'll we'll that's there's i've you've here".split())

def captions(words, cfg):
    words = [dict(w) for w in words]
    kw = cfg.get("cta_keyword", "").lower()
    for i in range(len(words) - 1):   # keep "comment, KEYWORD," as one caption
        if words[i]["w"].lower().strip(",.") == "comment" and words[i + 1]["w"].lower().strip(",.") == kw:
            words[i]["w"] = words[i]["w"].rstrip(",."); words[i + 1]["w"] = words[i + 1]["w"].rstrip(",")
    clauses = []; cur = []
    for i, w in enumerate(words):
        cur.append(w); nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is None or w["w"][-1:] in ".?!,;:" or nxt["s"] - w["e"] > 0.3: clauses.append(cur); cur = []
    txt = lambda ws: " ".join(x["w"] for x in ws)
    bare = lambda w: re.sub(r"[^a-z']", "", w["w"].lower())
    def split(ws):
        if len(txt(ws)) <= MAX_CHARS or len(ws) < 3: return [ws]
        best = None
        for i in range(1, len(ws)):
            Lw, Rw = ws[:i], ws[i:]
            c = abs(len(txt(Lw)) - len(txt(Rw))) / len(txt(ws))
            if bare(Lw[-1]) in FUNC: c += 3
            if len(Lw) == 1 or len(Rw) == 1: c += 2
            if bare(Rw[0]) in FUNC: c -= 0.3
            if best is None or c < best[0]: best = (c, i)
        i = best[1]; return split(ws[:i]) + split(ws[i:])
    out = []
    for c in [p for cl in clauses for p in split(cl)]:
        t = " ".join(x["w"] for x in c)
        for a, b in cfg.get("fixes", []): t = re.sub(a, b, t, flags=re.I)
        t = re.sub(r"[.,]+$", "", t).strip().lower()
        for a, b in cfg.get("post", []): t = re.sub(a, b, t)
        if kw: t = re.sub(rf"comment (the word )?{kw}\b", lambda mm: f"comment {mm.group(1) or ''}{kw.upper()}", t, flags=re.I)
        out.append([c[0]["s"], c[-1]["e"], t])
    return out

def check_fps(raw):
    info = subprocess.run([FF, "-hide_banner", "-i", raw], capture_output=True, text=True).stderr
    m = re.search(r"Video:.*?, (\d+(?:\.\d+)?) fps", info)
    if not m or abs(float(m.group(1)) - FPS) > 0.05:
        raise SystemExit(f"STOP: {raw} is {m.group(1) if m else '?'} fps, not 30. Tell the user; do not convert it.")

def run(cfg):
    k = cfg["id"]; raw = cfg["raw"]; check_fps(raw)
    words = json.load(open(f"{S}/words_{k}.json"))
    pk = f"{S}/A{k}.pkl"
    A = pickle.load(open(pk, "rb")) if os.path.exists(pk) else onset.analyze(raw)
    pickle.dump(A, open(pk, "wb"))
    n_end = len(A["v"]) * onset.STEP
    segs, _ = cut.segments(A, words, n_end)
    fr = [(int(round(a * FPS)), int(round(b * FPS))) for a, b in segs]
    json.dump([[fa / FPS, fb / FPS] for fa, fb in fr], open(f"{S}/segs_{k}.json", "w"))
    cum = []; acc = 0
    for fa, fb in fr: cum.append((fa / FPS, fb / FPS, acc)); acc += (fb - fa) / FPS
    total = acc
    def m(t):
        for a, b, c in cum:
            if t < a: return c
            if t <= b: return c + (t - a)
        return total
    caps = []
    for s, e, t in captions(words, cfg):
        ts = m(s)
        if caps and ts <= caps[-1][0] + 0.12: ts = caps[-1][0] + 0.12
        caps.append([ts, t])
    merged = []
    for i, (t, x) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else total
        if merged and merged[-1][2]:
            pt, px, _ = merged.pop(); t, x = pt, px + (", " if px.split()[-1] in MARK else " ") + x
        merged.append([t, x, ((nxt - t) < 0.35 or x in MARK) and i + 1 < len(caps)])
    caps = [[t, x] for t, x, _ in merged]
    toks = [re.sub(r"[^a-z0-9]", "", w["w"].lower()) for w in words]
    def find(phrase, start=0):
        p = [re.sub(r"[^a-z0-9]", "", x) for x in phrase.lower().split()]
        for i in range(start, len(toks)):
            if toks[i:i + len(p)] == p: return i
        raise SystemExit(f"[{k}] phrase not found: {phrase}")
    img_ev = []; pos = 0
    for im in cfg.get("images", []):   # {"at": "<spoken phrase>", "until": "<phrase>" | null, "path": ...}
        i = find(im["at"], pos); pos = i + 1
        img_ev.append([m(words[i]["s"]), m(words[find(im["until"], pos)]["s"]) if im.get("until") else None, im])
    # hook: frame 0 until the verbal hook ends (first sentence, or the phrase in hook_until); an image needing the spot ends it early
    if cfg.get("hook_until"): hook_off = m(words[find(cfg["hook_until"])]["s"])
    else:
        end_i = next((i for i, w in enumerate(words) if w["w"][-1:] in ".?!"), len(words) - 1)
        hook_off = m(words[end_i + 1]["s"]) if end_i + 1 < len(words) else total
    if img_ev and img_ev[0][0] < hook_off: hook_off = img_ev[0][0]
    events = sorted(set([0.0, hook_off] + [c[0] for c in caps] + [e[0] for e in img_ev] + [e[1] for e in img_ev if e[1]]))
    def at(t, lst):
        v = None
        for tt, x in lst:
            if tt <= t + 1e-6: v = x
        return v
    def img_at(t):
        v = None
        for on, off, im in img_ev:
            if on <= t + 1e-6 and (off is None or t < off - 1e-6): v = im
        return v
    os.makedirs(f"{S}/st_{k}", exist_ok=True)
    states = []
    for i, t in enumerate(events):
        end = events[i + 1] if i + 1 < len(events) else total
        if end - t >= 1e-3: states.append((t, end, at(t, caps), img_at(t), t < hook_off - 1e-6))
    lines = []
    for i, (t, end, cap, im, hk) in enumerate(states):
        frame(cfg, cap, im, hk).save(f"{S}/st_{k}/s{i:03d}.png")
        lines.append(f"file 'st_{k}/s{i:03d}.png'\nduration {end - t:.4f}\n")
    lines.append(f"file 'st_{k}/s{len(states) - 1:03d}.png'\n")
    open(f"{S}/st_{k}.txt", "w").write("".join(lines))
    parts = []; lab = []
    for i, (fa, fb) in enumerate(fr):   # picture and sound cut at the SAME clock times
        a, b = fa / FPS, fb / FPS
        parts.append(f"[0:v]trim=start={a:.6f}:end={b:.6f},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim=start={a:.6f}:end={b:.6f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.005,afade=t=out:st={b - a - 0.005:.6f}:d=0.005[a{i}]")
        lab.append(f"[v{i}][a{i}]")
    flip = "hflip" if cfg.get("hflip") else "null"   # only for mirrored front-camera footage of a screen, when the user says so
    fc = (";".join(parts) + ";" + "".join(lab) + f"concat=n={len(fr)}:v=1:a=1[bg0][a];[bg0]{flip}[bg];"
          f"[1:v]fps={FPS},format=rgba[ov];[bg][ov]overlay=eof_action=repeat:shortest=1,format=yuv420p[v]")
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-f", "concat", "-safe", "0", "-i", f"{S}/st_{k}.txt",
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                    "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", cfg["out"]], check=True)
    print(k, f"raw {n_end:.1f}s -> {total:.1f}s, {len(fr)} cuts, hook off at {hook_off:.2f}s")

if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    for j in jobs:
        if len(sys.argv) < 3 or j["id"] in sys.argv[2].split(","): run(j)

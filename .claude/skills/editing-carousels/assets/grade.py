"""
Cover photo filter — Jess-style: the photo as-is with a plain dark layer on top. Nothing else.
No color changes, no saturation/contrast/warmth tweaks (the user's photos are often already
edited in Lightroom; those edits stay intact). Locked with the user 2026-10-12 after the
graded/cutout/spotlight experiments were rejected (orange skin, muddy, halos).

Usage: python3 grade.py <input image> <output.jpg> [crop_y_bias] [darkness 0-1, default .50]
       crop_y_bias (optional, 0-1): where a tall photo is cropped. 0 keeps the top, .35 default.
Output: 1080x1350 (4:5) JPG.
"""
import sys
from PIL import Image, ImageOps

W, H = 1080, 1350
CROP_Y_BIAS = 0.35
DARKEN = 0.50         # opacity of the black layer over the whole photo
EDGE_DARKEN = 0.12    # a touch more at the very bottom so the footer reads


def grade(src, dst, bias=CROP_Y_BIAS, dark=DARKEN):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    r = W / H
    w, h = im.size
    if w / h > r:
        nw = int(h * r)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / r)
        top = int((h - nh) * bias)
        im = im.crop((0, top, w, top + nh))
    im = im.resize((W, H), Image.LANCZOS)

    edge = int(H * 0.18)
    col = Image.new('L', (1, H))
    for y in range(H):
        d = (1 - (H - y) / edge) * EDGE_DARKEN if y > H - edge else 0.0
        col.putpixel((0, y), int(255 * min(1.0, dark + d)))
    mask = col.resize((W, H))
    Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, mask).save(dst, quality=92)


if __name__ == '__main__':
    grade(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else CROP_Y_BIAS,
          float(sys.argv[4]) if len(sys.argv) > 4 else DARKEN)

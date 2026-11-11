"""
Apply the cover framing the user saved on the batch review page.
  python3 assets/apply-framing.py <batch-dir> [cover-framing.json]   (default: ~/Downloads/cover-framing.json)
For each cover: crops the original photo exactly as framed (pan + zoom), grades it at his darkness,
writes cover-render.json (title nudge/size/alignment for build.js), then rebuilds every deck and
the review page.
"""
import sys, os, json, shutil, subprocess, glob
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.abspath(sys.argv[1])
src_json = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/Downloads/cover-framing.json')
if os.path.abspath(src_json) != os.path.join(B, 'cover-framing.json'):
    shutil.copy(src_json, os.path.join(B, 'cover-framing.json'))
F = json.load(open(os.path.join(B, 'cover-framing.json')))
cfg = json.load(open(os.path.join(B, 'batch.json')))
srcs = json.load(open(os.path.join(B, 'editor/sources.json')))
boxes = json.load(open(os.path.join(B, 'editor/title-boxes.json')))
os.makedirs(os.path.join(B, 'covers-src'), exist_ok=True)
render = {}
for n, f in F.items():
    zoom, cx, cy = f.get('zoom', 1), f.get('cx', .5), f.get('cy', .5)
    im = ImageOps.exif_transpose(Image.open(srcs[n]['src'])).convert('RGB'); iw, ih = im.size
    sc = max(1080 / iw, 1350 / ih) * zoom; w, h = 1080 / sc, 1350 / sc
    l = min(max(cx * iw - w / 2, 0), iw - w); t = min(max(cy * ih - h / 2, 0), ih - h)
    framed = os.path.join(B, 'covers-src/%s-framed.jpg' % n)
    im.crop((round(l), round(t), round(l + w), round(t + h))).save(framed, quality=95)
    subprocess.run(['python3', os.path.join(HERE, 'grade.py'), framed, os.path.join(B, 'c%02d-bg.jpg' % int(n)), '.5', str(f.get('dk', .5))], check=True)
    # page scales the title image about ITS box center; the kit scales the text block about the
    # block center (540, 675) — convert so the slide matches the page exactly.
    al = f.get('al', 'left'); k = f.get('ts', 1); bx = boxes[n][al]
    bcx, bcy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    render[n] = {'align': al, 'scale': k,
                 'shiftX': round(f.get('tx', 0) + (1 - k) * (bcx - 540), 1),
                 'shiftY': round(f.get('ty', 0) + (1 - k) * (bcy - 675), 1)}
json.dump(render, open(os.path.join(B, 'cover-render.json'), 'w'), indent=1)
env = dict(os.environ, PATH=os.path.expanduser('~/.local/node/bin') + ':' + os.environ['PATH'])
root = os.path.dirname(HERE)
for n in cfg['order']:
    name = cfg['decks'][str(n)]['name']
    subprocess.run(['node', 'assets/build.js', os.path.join(B, name + '-slides.js'), os.path.join(B, name + '.html')], cwd=root, env=env, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['node', 'assets/export-png.js', os.path.join(B, name + '.html'), os.path.join(B, name + '-export')], cwd=root, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('rendered', name)
subprocess.run(['python3', os.path.join(HERE, 'build-review.py'), B], check=True)

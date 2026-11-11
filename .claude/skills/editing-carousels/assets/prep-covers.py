"""
Prep a batch for the review page: web copies of each cover photo + transparent title overlays
(left / center / right) with their boxes.
  python3 assets/prep-covers.py <batch-dir>
batch.json: {"order": [...], "slots": [...], "decks": {"1": {"name": "c01-...", "title": "...", "series": "...", "photo": "<path>"}}}
"""
import sys, os, json, subprocess, shutil
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(HERE)
B = os.path.abspath(sys.argv[1]); E = os.path.join(B, 'editor'); os.makedirs(E, exist_ok=True)
cfg = json.load(open(os.path.join(B, 'batch.json')))
env = dict(os.environ, PATH=os.path.expanduser('~/.local/node/bin') + ':' + os.environ['PATH'])
for f in ('deck-stage.js', 'image-slot.js'): shutil.copy(os.path.join(HERE, f), E)
sources, boxes = {}, {}
for n, d in cfg['decks'].items():
    k = 'c%02d' % int(n)
    p = d['photo']
    if p.lower().endswith('.heic'):
        jp = os.path.join(E, k + '-photo.jpg'); subprocess.run(['sips', '-s', 'format', 'jpeg', p, '--out', jp], check=True, stdout=subprocess.DEVNULL); p = jp
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB'); sources[n] = {'src': p, 'w': im.size[0], 'h': im.size[1]}
    im.thumbnail((1600, 1600)); im.save(os.path.join(E, 'src%02d.jpg' % int(n)), quality=88)
    ov = os.path.join(E, k + '-ov.js')
    open(ov, 'w').write("const d = require('../%s-slides.js');\nconst c = Object.assign({}, d.slides[0], { textOnly: true, noFoot: true });\n"
                        "module.exports = Object.assign({}, d, { slides: ['left', 'center', 'right'].map(a => Object.assign({}, c, { align: a })) });\n" % d['name'])
    subprocess.run(['node', 'assets/build.js', ov, os.path.join(E, k + '-ov.html')], cwd=root, env=env, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['node', 'assets/export-png.js', os.path.join(E, k + '-ov.html'), os.path.join(E, k + '-ovx')], cwd=root, env=dict(env, TRANSPARENT='1'), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    boxes[n] = {}
    for i, a in enumerate(['left', 'center', 'right']):
        o = Image.open(os.path.join(E, k + '-ovx/slide-%02d.png' % (i + 1))); bb = o.getbbox(); pad = 6
        bb = (max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, o.size[0]), min(bb[3] + pad, o.size[1]))
        o.crop(bb).save(os.path.join(E, '%s-title-%s.png' % (k, a))); boxes[n][a] = [v / 2 for v in bb]
    print('prepped', k)
json.dump(sources, open(os.path.join(E, 'sources.json'), 'w'), indent=1)
json.dump(boxes, open(os.path.join(E, 'title-boxes.json'), 'w'))

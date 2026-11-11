"""1-fps QC grid of finished reels (216x384 frames): python3 <skill>/scripts/qc_grid.py 4,5 -> qc/big_<id>.jpg"""
import subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
jobs = {j["id"]: j for j in json.load(open("jobs.json"))}
for k in sys.argv[1].split(","):
    W, H = 216, 384
    buf = subprocess.run([FF, "-loglevel", "error", "-i", jobs[k]["out"], "-vf", f"fps=1,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = np.frombuffer(buf, np.uint8).reshape(-1, H, W, 3); cols = 10; rows = (len(fr) + cols - 1) // cols
    sh = Image.new("RGB", (cols * W, rows * H))
    for i, f in enumerate(fr):
        im = Image.fromarray(f); ImageDraw.Draw(im).text((4, H - 14), f"{i}s", fill="yellow"); sh.paste(im, ((i % cols) * W, (i // cols) * H))
    sh.save(f"qc/big_{k}.jpg", quality=82)

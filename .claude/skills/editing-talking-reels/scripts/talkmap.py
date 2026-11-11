"""Which raw seconds are him on camera vs the screencast (camera on the monitor), by face detection.
Writes talk_<id>.json: [[start,end],...] in raw seconds, plus his head-top per interval."""
import json, subprocess, sys
import numpy as np, cv2
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
jobs = {j["id"]: j for j in json.load(open("jobs.json"))}
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
for k in sys.argv[1].split(","):
    W, H, FPS = 270, 480, 4
    buf = subprocess.run([FF, "-loglevel", "error", "-i", jobs[k]["raw"], "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(buf, np.uint8).reshape(-1, H, W)
    face = []; tops = []
    for f in fr:
        fs = cas.detectMultiScale(f, 1.1, 5, minSize=(62, 62))
        face.append(max((h for x, y, w, h in fs), default=0) > 0)
        tops.append(min((y - 0.40 * h for x, y, w, h in fs), default=9e9) * 1920 / H)
    t = np.array(face)
    for _ in range(2):                                    # fill 1-2 frame dropouts (blinks, turns)
        for i in range(1, len(t) - 1):
            if t[i - 1] == t[i + 1] != t[i]: t[i] = t[i - 1]
    iv = []; s = None
    for i, v in enumerate(t):
        if v and s is None: s = i
        if not v and s is not None: iv.append([s / FPS, i / FPS]); s = None
    if s is not None: iv.append([s / FPS, len(t) / FPS])
    m = []
    for a, b in iv:                                       # merge gaps under 1.2s (hand over face, quick turn)
        if m and a - m[-1][1] < 1.2: m[-1][1] = b
        else: m.append([a, b])
    end = len(t) / FPS                                    # trim the edges so nothing ever lands on a screencast frame
    iv = [[a + (0.3 if a > 0 else 0), b - (0.8 if b < end else 0)] for a, b in m]
    iv = [[round(a, 2), round(b, 2)] for a, b in iv if b - a >= 0.8]
    out = []
    for a, b in iv:                                       # split each stretch into 1s pieces, each with its own head-top
        x = a
        while x < b - 1e-6:
            y = min(b, x + 1.0); ts = [tops[i] for i in range(int(max(0, x - 0.25) * FPS), min(len(tops), int((y + 0.25) * FPS))) if tops[i] < 9e8]
            out.append([round(x, 2), round(y, 2), int(np.percentile(ts, 5)) if ts else (out[-1][2] if out else 500)]); x = y
    iv = out
    json.dump(iv, open(f"talk_{k}.json", "w"))
    print(k, len(iv), "pieces, head-top range", min(h for _, _, h in iv), max(h for _, _, h in iv))

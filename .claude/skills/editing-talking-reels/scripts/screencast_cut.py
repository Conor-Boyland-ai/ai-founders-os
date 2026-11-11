"""Ruthless pause + breath cutter that only cuts at quiet points.
Voice islands = pitched sound at speaking level, merged only across gaps < MERGE.
Every gap longer than that is cut out, leaving ~KEEP_TAIL + KEEP_HEAD of space. Cut points sit where the level has
dropped (or at the dip between a breath and the next word), so a cut never opens on breath noise (the old 'swipe')."""
import sys, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import onset
ST = onset.STEP
MERGE = 0.06      # the user 2026-10-08: zero pauses. Any silence over 60 ms gets cut.
KEEP_TAIL = 0.005
KEEP_HEAD = 0.005
FRIC = -4         # hiss band within 4 dB of full level = s/sh/f/t release, not breath
FPS = 30

def islands(A, words):
    v, p = A["v"], A["pitch"]; n = len(v)
    pv = (p >= 0.45) & (v > A["vs"] - 30)
    near = np.zeros(n, bool)
    for w in words:
        a, b = int(w["s"] / ST), int(w["e"] / ST)
        near[max(0, a):min(n, b)] = True
    loud = v > A["vs"] - 18          # anything this loud is him talking (breaths sit lower), never cut it
    voice = pv | loud | (near & A["voiced"])
    runs = []; i = 0
    while i < n:
        if voice[i]:
            j = i
            while j < n and voice[j]: j += 1
            if (j - i) * ST >= 0.03: runs.append([i, j])
            i = j
        else: i += 1
    merged = []
    for a, b in runs:
        if merged and (a - merged[-1][1]) * ST < MERGE: merged[-1][1] = b
        else: merged.append([a, b])
    return merged

def quiet(A): return float(A["vs"]) - 30   # below this = room noise / breath, relative to his voice level

def tail_end(A, i, limit):
    """Forward from voice end: keep the decay (max 40 ms) and fricative hiss (max 150 ms), stop at quiet or breath."""
    v, h = A["v"], A["h"]; fl = quiet(A); j = i
    while j < limit and j < i + int(0.15 / ST) and v[j] > fl and (j - i < int(0.04 / ST) or h[j] - v[j] > FRIC): j += 1
    return j

def head_start(A, i, limit):
    """Back from voice onset: keep fricative lead-in (s/f/sh) and 20 ms of attack; never keep breath."""
    v, h = A["v"], A["h"]; fl = quiet(A); j = i
    lo = max(limit, i - int(0.15 / ST))
    while j > lo and v[j - 1] > fl and (i - j < int(0.02 / ST) or h[j - 1] - v[j - 1] > FRIC): j -= 1
    if j == lo or v[j - 1] <= fl: return j
    # still loud and not a fricative -> breath running into the word: cut at the quietest point just before j
    w0 = max(lo, j - int(0.06 / ST)); seg = v[w0:j + 1]
    return w0 + int(np.argmin(seg))

def segments(A, words, t_end_s):
    isl = islands(A, words); n = len(A["v"])
    # the video starts on his first word and ends on his last: drop noise islands before/after the transcript
    w0, w1 = int((words[0]["s"] - 0.15) / ST), int((words[-1]["e"] + 0.15) / ST)
    isl = [x for x in isl if x[1] > w0 and x[0] < w1]
    segs = []
    for idx, (a, b) in enumerate(isl):
        prev_b = isl[idx - 1][1] if idx else 0
        nxt_a = isl[idx + 1][0] if idx + 1 < len(isl) else n
        s = head_start(A, a, prev_b) * ST - (KEEP_HEAD if idx else 0.005)
        e = tail_end(A, b, nxt_a) * ST + (KEEP_TAIL if idx + 1 < len(isl) else 0.03)
        segs.append([max(0.0, s), min(t_end_s, e)])
    out = []
    for i, (a, b) in enumerate(segs):
        a = np.floor(a * FPS + 1e-6) / FPS      # always snap outward: a frame edge never lands inside a word
        b = np.ceil(b * FPS - 1e-6) / FPS
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out, isl

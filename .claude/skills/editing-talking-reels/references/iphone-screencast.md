# iPhone screencast

The user talks to camera, then films their screen with the phone. Locked on the Muse / Write / Branding batch. Run it exactly as written. Change it only when the user says to.

## What the finished reel looks like

- **Cuts:** ruthless. No pauses, breaths or noise anywhere. It starts on their first word and ends on their last.
- **Hook:** The user's text verbatim, white on a black rounded box. It's on screen from frame 0 until their verbal hook ends (their first sentence), then it's gone for good.
- **Captions:** the standard look (white Inter SemiBold 44px, heavy shadow, no box, lowercase with brands capitalized, CTA keyword in caps). They sit at y=1120.
- **Images (only when the user supplies them):** overlaid on the video above their head, from the line the user names until the next. If one lands during the verbal hook, the hook ends where the first image starts.
- **Nothing else.** No grade, zoom, transitions, music, cutaways or frame-rate change.

## Inputs (from the user)

Raws, hook text per video, and images plus the line each goes on. Raws live in the folder the user points you to, finals go to `…/final/`.

## Steps

1. **Probe every raw.** It must be 30fps, with no rotation tag. If one isn't 30fps, STOP and tell the user (`screencast.py` refuses it). Never convert.
2. **Transcribe:** `python3 <skill>/scripts/transcribe.py <id>=<raw> …`, run from a scratchpad working folder.
3. **Measure (judgment).** For each raw, pull frames across every second the hook or an image shows. Mark y-lines and read off:
   - **Top of their head** (hair). The hook and images go fully above it. `hook_band = [150, head_top − 15]`. The top 150 is fine; the user wants that wall space used.
   - **If there's no room above their head** in the shot (close-up for the whole hook), use the gap under their chin and above the captions or screen. Never on their face, hair or the screen they're showing.
   - **`img_area`:** the same rule for the moment each image shows.
   - Use the LOWEST head top in that window (the closest moment), not a typical frame.
4. **Write `jobs.json`** (fields below). `fit_hook` makes the hook as big as fits the band, with 1–3 balanced lines inside the 65px side margins.
5. **Render:** `python3 <skill>/scripts/screencast.py jobs.json`.
6. **Checks.** All of them, every reel, before the user sees anything:
   - `python3 <skill>/scripts/word_check.py jobs.json <ids>`. Any word flagged "CUT NEARBY" gets its waveform inspected and fixed.
   - The first frame has the hook on it, and the first sound is their first word.
   - Frame grid at every hook and image moment: nothing touches their head or face, and nothing covers the screen they're showing. Box padding looks equal.
   - The hook disappears once, at the end of the verbal hook. No flashing on and off.
7. **Show the user** the final folder, plus anything decided by judgment (where the hook sits, its size, any spot with no room). Schedule only after their yes.

## If a video doesn't fit these rules

Stop and ask the user. Never invent a fix mid-batch (frame-rate conversion, delayed hooks, cutaways and hidden hooks all broke reels on 10/8).

## Job fields

```json
{"id": "5", "raw": "<raw path>", "out": "<final path>.mp4",
 "hook": "Train Claude to Write Your Marketing",
 "cta_keyword": "write",
 "layout": {"hook_band": [150, 365], "img_area": [150, 385], "cap_y": 1120, "hook_max": 160},
 "images": [{"at": "embarrassed", "until": "here's how", "path": "<png>"}],
 "hook_until": null, "hflip": false,
 "fixes": [["ai \\.meta \\.com", "ai.meta.com"]],
 "post": [["\\bmuse\\b", "Muse"], ["\\bclaude\\b", "Claude"], ["\\bai\\b", "AI"], ["\\bi\\b", "I"], ["\\bi'(m|ll|ve|d)\\b", "I'\\1"]]}
```

- `hook_until`: leave null (it ends after the first sentence). Set a phrase only if the user's verbal hook runs longer.
- `cap_y`: 1120 unless captions would cover their face or the screen they're showing. Then move them into the free gap (e.g. #4: hook band [735, 882], cap_y 897, hook_max 44).
- `hflip`: only for mirrored front-camera footage of a screen, when the user asks.
- `fixes` run before lowercasing, `post` after. Brands and the CTA keyword go in caps.

## Cutter (screencast_cut.py), approved 2026-10-08

- Any silence over 0.06s is cut. About 5ms is kept each side, and frame snapping always goes outward.
- Cut points land only on quiet (below voice level −30 dB) or on the dip between a breath and a word.
- Anything louder than voice level −18 dB counts as speech and is never cut.
- Noise before their first word and after their last is dropped.
- Picture and sound are cut at the same clock times. There's a 5ms audio fade at each join.

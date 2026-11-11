# Paradigm shift (the user's format 4; was "F6")

The user talks to camera, sitting low in the frame. Famous faces in the hook, then pop-up images and text cards on the lines they illustrate. Modeled on `retention reels/paradigm shift/formula_6_example.mp4`. Scripts and hook images are in their Short Form Writing page ("Identity + paradigm shift").

## Look
- **Hook:** their chosen hook images in a row (1–3, cover-cropped, rounded) with the "Text hook" line in a white card under them (Inter Bold, emoji supported). Fix obvious typos in the title and tell them. Up until a phrase (`hook_until`, about the first 1–2 sentences).
- **Overlays sit above their head:** band y 270–540, never on the forehead. The user asked for "up above my forehead."
- **Captions go across their chest, as low as allowed:** `cap_y` 1180 (lifts automatically for 2 lines), lowercase, Inter SemiBold 46, above Instagram's y=1248 cutoff.
- **Images stay up:** about 3.5s each, held until the next overlay if it arrives within 1.5s. No blinking on and off.
- **Cadence:** model the example, about one overlay every 8–10s. Mix images with 1 text card (their exact words) and end on the "Comment KEYWORD" card (green keyword, top band) until the end.
- **Grade:** `grade_lift` 0.5 for this room (lift 1.0 washed their face out). `grade_strength` 0.5.

## Images
Claude finds them. Pool per reel in `<reel>/image overlay/body/` with `overlays.md` (line → image). Rules: [[feedback-reel-image-selection]] in memory (famous faces, iconic memes/stills, no stock). Place each on the line the user actually says. Match the spoken phrase, not the script.

## Job fields (`scripts/paradigm.py jobs.json`)
`title`, `hook_images`, `hook_until`, `overlays: [{"at": "spoken phrase", "img": path | "text": "..." | "cta": "KEYWORD", "dur"?}]`, plus the laptop fields (`drop`, `fixes`, `post`, `lower`, `max_chars`, `grade_lift`). The cutter, retake drops and captions are shared with `laptop.py` (`plan()` / `render()`).

## Lessons
- small.en can put a word 1s+ early after a fast line ("there good luck"). Confirm drop end points with medium.en before cutting.
- **Cinematic mode raws** have a `dish` (disparity) data track, and the main video is fully sharp. The blur only shows in Apple's apps, and ffmpeg and avconvert both read the sharp video. If a raw has a `dish` stream, ask the user to re-AirDrop it with Share → Options → **All Photos Data OFF**, which bakes the blur in.

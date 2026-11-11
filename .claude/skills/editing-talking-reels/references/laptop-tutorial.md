# Laptop tutorial (formula 3)

The user sits behind an open laptop, facing the camera, and teaches a named, multi-step method of their own. The laptop screen shows a simple slide deck the user clicks through while the user talks. The reel is modeled on the "Listicle Method" example (`retention reels/laptop tutorials/laptop_tutorial_example.mp4`). The script formula is in their Short Form Writing page in Notion.

## Two parts: the slide deck (before filming) and the edit (after)

### 1. Slide deck: `scripts/slides.py deck.json <folder>`
- A web page the user opens full screen on the laptop (**F**). Click, space or → advances; ← goes back.
- **Minimal.** It's a visual for retention, not a presentation, and nobody reads it. The fewer clicks the better.
- Order, following the script's "like THIS / using THIS" beats:
  - `proof` slide: 1–3 images that appear one per click, for "sell like this, this, and this."
  - `proof` slide with the user's diagram, for "you need to be using THIS."
  - Any extra proof slide their script calls for (e.g. the $1.3M full-year chart).
  - One `step` slide per step: "Step N" in green with the step name, plus a small, quiet visual card from `scripts/cards.py` (email, page outline, doc, phone, funnel, chart). Gray with one green accent, no motion.
  - A `cta` slide: "Comment KEYWORD."
- Colors: warm off-white `#F7F5F0`, near-black text, green `#12A150`. Inter font.
- Images: The user drops them in `<deck>/images/`. Convert AVIF/HEIC/PNG to JPG with `sips` (named proof1.jpg, diagram.jpg and so on). Never ask them to gather extra images: build visuals with `cards.py`.
- Remind them to press **F** before filming. Otherwise the browser bar and dock show on camera.

### 2. Edit: `scripts/laptop.py jobs.json`
- **Hook box:** a white rounded box with black bold title + smaller sub, on their chest just above the laptop (`hook_y`≈880). It's up for the first sentence only.
- **Captions:** the same chest spot (`cap_y`≈930), hidden while the hook box shows (`caps_during_hook: false`). Lowercase, Inter SemiBold 46px. It's the same chunking as the 10/10 format.
- **Countdown ring:** top left beside their head. A white arc on a soft dark disc so it reads on bright walls, counting down from **90** in real seconds, never the reel's true length (`timer_start`, default 90). The reel always ends before the clock hits 0: they think it's 90s, it ends at 75s, and they've watched to the end. Never make it accurate. If a reel runs past 85s, cut it shorter or tell the user (the script bumps the clock and warns).
- **Retakes:** The user repeats lines until the user gets them right, and the **last take wins.** Find repeats in the transcript, then set `"drop": [[first_dropped_word_start, first_kept_word_start], ...]`. The cut lands in the silence before the dropped take and resumes at the kept take's voice onset. Always re-transcribe the final to confirm each line appears once and nothing is clipped. **Whisper hides retakes:** it often collapses a false start plus its retake into one word lasting seconds (e.g. "the" 60.2–66.4s held "all the n— … all the necessary"). Before writing drops, flag every word of 0.8s or longer with 0.35s or more of voice inside, re-transcribe that span with `medium.en` (`condition_on_previous_text=False`, no VAD), and fix those words' timings in `words_<id>.json` so the captions land right. Stray duplicated words inside one breath can be removed from captions only (`drop_caption_words`) and left in the audio.
- **60fps raws:** the cutter reads the source frame rate, keeps frames by number on the source grid, and outputs 30fps. It's a single streaming pass (`select`/`aselect`), because per-segment `trim` + `concat` stalls ffmpeg on long 60fps files.
- Auto grade, pause cuts, safe zones and verification are the same as in SKILL.md.

## Job example (Starving Buyers, approved)
```json
{"id":"sb1","raw":"<deck>/raw/IMG_1433.MOV","out":"laptop tutorials/final/1 - Starving Buyers Formula.mp4",
 "title":"The “Starving Buyers” Formula","sub":"(easiest way to sell courses)",
 "drop":[[81.5,87.44],[138.48,165.1]],"drop_caption_words":[104.3],
 "fixes":[["starving buyer's","starving buyers"],["\\b1\\.3 million","$1.3 million"]],
 "post":[["comment the word buyers","comment the word BUYERS"],["\\btinder\\b","Tinder"]],
 "lower":true,"max_chars":30,"timer":true,"caps_during_hook":false,
 "layout":{"margin":70,"hook_y":880,"hook_size":64,"hook_sub_size":38,"hook_gap":8,"hook_pad":22,"hook_radius":14,
   "ring_x":150,"ring_y":420,"ring_r":58,"ring_width":8,"ring_num_size":46,"cap_y":930,"cap_size":46,"cap_margin":90}}
```
Hook title and sub come from the reel's title line in their Short Form Writing page.

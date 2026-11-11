# Talking-head batch

The user talks to camera, with headline, captions and visual retention elements. Script: `scripts/reel_editor.py`. Example job file for every field: `references/examples/jobs-10-26.json`.

## Layouts

| Raw | Layout | Look |
|---|---|---|
| Horizontal 1920x1080 | `kv` | Headline at the top, a visual slot (y 505–1220, 1080x715) for the animated framework, captions, their video in a band at the bottom. |
| Vertical 1080x1920 | `vf` | Him full frame. Headline in the space above their head, captions at y 1400, visuals above their head. |

Never switch a reel between layouts without asking the user (the user was furious when 7, 9, 10 and 11 were moved without asking).

## Above-their-head rules (vf)

- **Never leave blank space above their head while they're on camera.** The headline or a visual is always there.
- **Never cover their face or hair.** `scripts/talkmap.py <id>` finds on-camera stretches and their head top per second (face detection, `y − 0.40·h`). The editor hides the headline when it won't clear, and never flashes it for under 1.5s.
- **Screencast sections get captions only.** Set `"talk": true` so the editor knows which sections are on camera.
- **Headline centered** between the top of the frame and their hair, per shot (`"title_center": 35`, the face-detector offset). The user's call, 10/21.
- **Visuals go where the user points** when the user points (`"box"` on an overlay, `"solo": true` hides the headline while it's up, `"dur"` sets how long it holds). Size the visual to the space. A small image is a failure ("so tiny you can't even see it").

## Real footage splices (the user's favourite fix)

When a line names something the user has real footage of, lay that footage over the line and keep their voice:
`"splice": [[out_start, out_end, src_start, "/path/to/file.MP4"]]` (omit the path to splice from the same raw).

- Reel 7: the shot of them pointing at their carousel grid went over "Claude turned a voice note into these 10 carousels."
- Reel 12: their Notion Cofounder page went over "setting up your business brain."
- Reel 13: the Muse connectors, niche prompt, download page and live dashboard each went over the line that names them.

Look in the folder the user points you to and the batch's own raws first.

## Cuts

- Retakes: `"drop": [[first_word_of_bad_take, onset_of_next_kept_word]]`. If the transcript merged two takes (the word "that" spanning 3s), fix `words_<id>.json` by hand from `words_<id>.alt.json`, then re-check with a faster-whisper transcript of the final around the cut. Reel 4 shipped "a system that" twice before this check.
- **Slow intros get trimmed.** If they're 20s in before anything moves, cut the setup lines the user points to (reel 12 went from 69s to 56s).

## QC before showing them (every reel)

1. `scripts/qc_grid.py <ids>`: a 1-fps grid of the final. Read every frame for blank space above their head, text on their face, gaps, and anything static over about 2s.
2. Full-size frames at every overlay change and every splice edge.
3. Re-transcribe the spots you cut and listen for double takes.

## Layout values that worked

`kv` palettes: sky, gold, green. Captions Inter Bold 58, max width 840 (clears the IG button column). Headline Helvetica Neue Bold, up to 3 lines, max width 940.

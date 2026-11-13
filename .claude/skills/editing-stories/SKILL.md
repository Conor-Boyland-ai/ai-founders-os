---
name: editing-stories
description: Turns a page of story copy and a folder of the user's photos into a batch of single-image Instagram stories, then schedules them. Use when the user asks to make, create or schedule IG stories.
metadata:
  version: 1.2.0
  built: 2026-10-21
---

# editing-stories

Turns the user's story copy and photos into finished IG stories and schedules them. The user gives two things: the copy (usually a Notion page, one block per story) and a folder of photos. You handle the rest.

Tell the user the ETA at every step. **One edit from them = change only that story.** Never rewrite the whole set unless the user says so.

## Steps

1. **Read the copy.** One story per block.
2. **Pick the photos.** Look through the folder and match a photo to each story: one with room for the text, and a different photo for each story where the folder allows. HEIC files are fine. If the folder runs out, use a black background.
3. **Render:** fill a job file from `references/job-template.json` and run `python3 scripts/make_stories.py job.json`. Set `text_y` per story so the text sits over the empty part of the photo.
4. **Check every story at full size.** If the text touches their face or hair, adjust `zoom` + `anchor` (`top` pushes their face down, `bottom` pulls it up) or `text_y`, or pick a different photo, then re-render.
5. **Show the user the preview:** open the generated `preview.html` for them. Save the finals in a `final/` folder next to their photos. They can swap any photo or change any story.
6. **After their OK, schedule them** per `references/scheduling.md`. If they didn't give days and times, ask in one line. Then list each story's date and time back to them.

## Design

- 1080x1920. Photo cover-cropped to 9:16.
- Helvetica Neue Bold 46, white text, one rounded black box (185 alpha) per paragraph, centered.
- The CTA keyword is in yellow (#FFD11A).
- The text block stays between y 270 and y 1620, clear of the IG top bar and the reply bar.
- Black-background stories have no boxes, just centered text.

## References

- `references/scheduling.md`: scheduling the stories.
- `references/job-template.json`: a blank job file for the render script.

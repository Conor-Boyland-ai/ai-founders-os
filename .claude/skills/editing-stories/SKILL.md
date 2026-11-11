---
name: editing-stories
description: Turns finished story copy into a run of single-image Instagram stories over the user's photos and schedules them as IG stories. Use when the user asks for IG stories, story reminders or a story countdown.
metadata:
  version: 1.1.0
  built: 2026-10-21
---

# editing-stories

The process for turning what the user wants said into a set of single-image IG stories and scheduling them. The content changes every time and comes from the user. This skill holds only the process.

Tell the user the ETA at every step. Ask them; don't dictate. **One edit from them = change only that story.** Never rewrite the whole set unless the user says so.

## Steps

1. **Inputs:** the finished story copy the user approved, one block per story, plus the posting days and times.
2. **Photos:** The user points to a folder and picks which photo goes with which story. A story with no photo gets a black background. HEIC files are fine.
3. **Render:** fill a job file from `references/job-template.json` and run `python3 scripts/make_stories.py job.json`. Set `text_y` per story so the text sits over the empty part of the photo.
4. **Check every story at full size.** If the text touches their face or hair, adjust `zoom` + `anchor` (`top` pushes their face down, `bottom` pulls it up) or `text_y`, or ask the user to trim the copy, then re-render.
5. **Show the user the preview:** publish the generated `preview.html` as an Artifact. Save the finals in a `final/` folder next to their photos.
6. **After their OK, schedule them** per `references/scheduling.md`, then list each story's date and time back to them.

## Design

- 1080x1920. Photo cover-cropped to 9:16.
- Helvetica Neue Bold 46, white text, one rounded black box (185 alpha) per paragraph, centered.
- The CTA keyword is in yellow (#FFD11A).
- The text block stays between y 270 and y 1620, clear of the IG top bar and the reply bar.
- Black-background stories have no boxes, just centered text.

## References

- `references/scheduling.md`: scheduling the stories.
- `references/job-template.json`: a blank job file for the render script.

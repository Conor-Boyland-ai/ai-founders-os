---
name: editing-talking-reels
description: Edits the user's raw talking-head reels into finished, post-ready videos in bulk. It cuts dead space, adds on-screen text overlays and captions in their approved formats, verifies every file, then schedules the batch in Eden after the user approves. Use when the user drops raw reels in a folder and asks to edit, cut, caption, finish or batch them, or names a reel format (rapid fire list, 10/10 listicle). Each format lives in references/.
metadata:
  version: 1.0.0
  built: 2026-09-29
---

# editing-talking-reels

Turn a folder of raw reels into finished reels that match one of the user's locked formats. The user films and supplies the words. This skill cuts, overlays, verifies and schedules. It never writes their copy: headlines, list text and captions come from them verbatim.

## Formats (one reference file each)

| Format | Reference | What it looks like |
|---|---|---|
| Rapid fire list | `references/rapid-fire-list.md` | White list box. Each item appears the instant the user says it. Green CTA keyword. |
| 10/10 listicle | `references/ten-ten-listicle.md` | Headline stays on screen, the numbered sign swaps, live captions, pauses cut. |
| Paradigm shift | `references/paradigm-shift.md` | the user low in frame. Hook faces + title card, pop-up images/text cards above their head on the lines they illustrate, chest captions. |
| Laptop tutorial | `references/laptop-tutorial.md` | the user behind a laptop running a minimal slide deck (`slides.py`). Hook box, countdown ring, captions, retakes cut (last take wins). |
| iPhone screencast | `references/iphone-screencast.md` | Talk to camera, then the phone films their screen. Ruthless cuts, hook box from frame 0 until the verbal hook ends, standard captions, their images above their head. Script `screencast.py`. |
| Talking-head batch | `references/talking-head-batch.md` | Horizontal raw: headline + animated visual slot + video band. Vertical raw: full frame, headline centred above their head, real-footage splices on the lines they show. Script `reel_editor.py`. |

**Visual retention standard (all formats):** `references/animated-visuals.md`. Pitch the visuals beat by beat, get their OK, then build animated frameworks that land word by word (engine `scripts/anim/`).

A new format gets its own reference file plus a script in `scripts/`. Never bolt a new format onto an existing one.

**Locked formats run exactly as written.** Judgment (text size, placement around their head, image spots) happens inside the format's steps. If a video doesn't fit the rules, stop and ask the user. Never patch the scripts mid-batch.

## Learning a new format from an example (the core handoff)

The user sends two things: an example reel of the format to model, and a batch of raws. Do this:

1. **Study the example file:** The user brings the example reel as a local video file. Pull frames at every text change to measure timing, sizes and positions exactly. If the user also names the creator or link, get the caption and metrics from Eden (`eden_read_social_post`).
2. **Deconstruct it into a written formula:** script structure, which text layers exist and where, what changes when (and on which spoken cue), caption style, cut rhythm, retention tricks (zooms, overlays, B-roll, sound).
3. **Translate it into the user's style:** Inter font, their type hierarchy (headline > sub > labels > captions), safe zones, their words verbatim. Keep the other creator's structure, never their look wholesale.
4. **Build the format:** reuse `onset.py`, the frame-exact cutter and caption chunker from `listicle.py`, and add only the new pieces. Render ONE raw, verify it, show the user, and apply their notes until the user locks it.
5. **Save it:** write `references/<format>.md` (approved look, job fields, lessons) and add a row to the table above.
6. **Batch the rest,** verify every file, show them the lineup, and schedule after their yes.

Retention tricks (image overlays, zoom punch-ins, animated text, B-roll/screen cutaways, sound) get built as reusable functions the first time a format needs them. List each approved trick in the format's reference.

## Non-negotiable editing rules

1. **Zero dead space.** The video starts on the first sound out of their mouth and ends on the last one. `scripts/onset.py` finds both from voice and hiss envelopes at 5 ms. Clicks and breaths that don't run straight into a word get cut.
   **Ruthless pause cuts:** they're always talking. The only silence left is the natural space between words. Only their voice counts as sound (`onset.speech_mask`): consonant hiss counts only where it touches a word, up to 0.12s, and breaths, mouth noise and room blips count as silence. Every silence over 0.06s is cut to about 0.055s. **Only their voice counts as sound:** pitched sound (`onset` pitch ≥ 0.45) near their speaking level, within 0.25s of a transcribed word. Breaths into the handheld mic, typing, shuffling and scratches are loud but unpitched, so they get cut. Transcripts come from `medium.en` plus a `small.en` backup (`words_<id>.alt.json`), and sound near a word either one heard is kept. Finish with a gap audit: re-transcribe the final and list every between-word gap over 0.25s. Sentence breaks of about 0.3s (word tails) are fine. Anything longer gets inspected. **WARNING:** The user rejected the paradigm reels cut with this pitch/breath cutter. The user heard a "swipe" sound at every cut. Treat that cutter as unproven. Before using it on a new batch, render one reel and get the user's ear on it. **No swoosh at cuts:** a cut may open on 20ms of unpitched sound at most (more only for a real s/sh/f hiss), pieces with no voice get dropped, and every audio join gets a 5ms fade. Then run the **word diff** (final vs raw transcript). Every raw word must be in the final. Differences like wanna/want to and 5/five are fine. A missing word means a clip, so fix it before showing the user. Before showing them a batch, measure the finals: no gap of 0.12s or more without voice, except an "s/t" tail.
2. **The first frame is the real video.** Frame 0 must have pts 0 and normal brightness. Never use `-avoid_negative_ts`. Reset timestamps with `setpts=PTS-STARTPTS`.
3. **No rotation tags on output.** iPhone raws carry a −90° tag. The scripts strip any leftover tag and assert it's gone.
4. **Picture and sound stay in sync.** Every cut is frame-exact (`trim` on frame numbers plus matching `atrim`). Video and audio lengths must match within one frame.
5. **Text stays inside Instagram's safe zone.** Meta's rule: nothing in the top 14% (269px), the bottom 35% (above y=1248) or 6% (65px) on each side. The CTA line on rapid-fire lists is the one deliberate exception, placed where the user approved it.
6. **Their words, verbatim.** Headlines, labels and list text come from their message or doc. Transcripts only supply timing and captions. Capitalize brands and acronyms (AI, DM, TikTok, $68K) and their CTA keywords (HUMAN, FREEDOM). Fix clear transcription misspellings (e.g. "purple pros" → "purple prose"). Anything uncertain gets re-checked with the `medium.en` model and flagged to them, never guessed.
7. **Auto color grade on every reel**: `scripts/grade.py` pulls out the yellow cast at 50% strength and brightens. It's on by default in all editors. Set `"grade": false` in a job only if the user asks. **Lighting isn't dialed in yet:** before each new batch, show the user one before/after frame and tune `grade_strength` (cast removal, 0–1, default 0.5) and `grade_lift` (brightness, default 1.0) per batch. Note the approved values in the format reference so similar shoots can reuse them, and tell them plainly when footage is too dark or mixed-light to fix cleanly.
8. **Never schedule without their approval.** Show the finished files first, get a yes, then schedule. "Post it" means the next free slot, not now, unless the user says "now".
9. **Countdown timers are never accurate**. Any reel with a timer counts down from 90s in real seconds and always ends before it hits 0. The timer gives their brain a time limit to stay for, not the truth about the length. They should never be able to predict the exact ending.

## Pipeline

Setup (once per machine): `python3 -m pip install --user faster-whisper imageio-ffmpeg pillow numpy`

1. **Inspect the raws:** duration, resolution, rotation tag, and a contact sheet of frames. A `dish` data stream means iPhone Cinematic mode with the blur NOT baked in. Ask for an export with All Photos Data off.
2. **Transcribe:** from a working folder in the scratchpad, `python3 <skill>/scripts/transcribe.py 1=<raw1> 2=<raw2> …`. It writes `words_<id>.json`.
3. **Write the job file** for the format (fields are in the format's reference). Put the user's exact text in it.
4. **Render:** run the format's script from the working folder. Output goes to the format's `final/` folder.
5. **Verify every file, and never skip this:**
   - Plot the start and end cuts on a waveform. The red line must sit on the rise and fall of their voice.
   - Frame 0 has pts 0, video and audio durations match, and there's no `displaymatrix`.
   - Pull a frame grid at every text change and read it: nothing clipped or wrapping badly, everything inside the safe zone.
   - Diff caption words against spoken words. No word may go missing.
6. **Show the user:** open the `final/` folder and list headline, labels and any text you had to decide or fix. Wait for their notes, apply them, and re-verify.
7. **Schedule after approval**, per `references/scheduling.md`.

## Where things live

- Raws: wherever the user points you. Finals go in a `final/` folder next to them.
- Everything temporary (transcripts, overlay PNGs, job files) goes in the session scratchpad, never the reels folders.

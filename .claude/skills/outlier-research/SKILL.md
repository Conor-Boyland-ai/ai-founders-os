---
name: outlier-research
description: Pulls outlier reels from the user's Eden creator list and shows each one word for word, with its hooks, full script, CTA and outlier score. Reports only, no interpretation. Use when the user asks to run outlier research, find outliers, or see what's working.
---

# outlier-research

Shows the user what's working, word for word, so they can judge it themselves.

## Inputs

The user gives these each run:

- **Outlier threshold:** how far above the creator's normal a reel performed, as a percentage (300% = 3x their normal)
- **Number of reels:** how many to show
- **Creators:** their whole Eden watchlist, or one named list
- **Timeframe:** for example, the last 30 days

If one is missing, ask for it in one line, then run.

## Steps

1. In Eden, pull reels from those creators inside the timeframe. Keep reels at or above the threshold. Rank by outlier score, highest first, and keep the number asked for.
2. For each reel, have Eden transcribe the video (`eden_read_social_post` with the transcript on). The spoken transcript is the script. The text burned into the video (`onScreenText`) is the text hook. The written caption is a different thing, so leave it out: the user wants what the viewer saw and heard.
3. Take the CTA from the script or on-screen text, word for word.

## Output

One block per reel, ranked. Exactly this shape:

**1. @creator · 4.2x · 310K views · Nov 2 · [link]**
- **Text hook:** "on-screen text, word for word"
- **Verbal hook:** "first line spoken, word for word"
- **Topic:** one short line
- **CTA:** "word for word"
- **Script:** the full transcript, word for word

## Rules

- Copy hooks, CTAs and scripts exactly. The user studies the real wording, so a cleaned-up version is useless to them.
- Report only. Angles, patterns and suggestions are the user's call, so leave them out.
- Topic is a short label, never more than one line.
- When a reel has no CTA or no on-screen text, write "None". When Eden can't transcribe a reel, write "Transcript unavailable".
- Real numbers only, all inside the timeframe.

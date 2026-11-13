---
name: outlier-research
description: Pulls outlier reels from the user's Eden creator list and lays them out in one clean report, with every hook, topic, angle, CTA and full script word for word. Reports only, no interpretation. Use when the user asks to run outlier research, find outliers, or see what's working.
---

# outlier-research

One clean report of what's winning right now, so the user can read everything and model it.

## Inputs

The user gives these each run:

- **Outlier threshold:** how far above the creator's normal a reel performed, as a percentage (300% = 3x their normal)
- **Number of reels:** how many to show
- **Creators:** their whole Eden watchlist, or one named list
- **Timeframe:** for example, the last 30 days
- **Where to save it:** a Notion page, if they give one

If one of the first four is missing, ask for it in one line, then run.

## Steps

1. In Eden, pull reels from those creators inside the timeframe. Keep reels at or above the threshold. Rank by outlier score, highest first, and keep the number asked for.
2. For each reel, have Eden transcribe the video (`eden_read_social_post` with the transcript on). The spoken transcript is the script. The text burned into the video (`onScreenText`) is the text hook. The written caption is a different thing, so leave it out: the user wants what the viewer saw and heard.
3. Take the CTA from the script or on-screen text, word for word.
4. Build the report below. If the user gave a Notion page, save it there as a new subpage called "Outlier Research - [today's date]" and reply with the link only. Otherwise, reply with the report.

## Report

**At a glance:** one table, one row per reel, ranked:

| # | Creator | Score | Text hook | Verbal hook | Topic | Angle |

**Then one section per reel, same order:**

**1. @creator · 4.2x · 310K views · Nov 2 · [link]**
- **Text hook:** "on-screen text, word for word"
- **Verbal hook:** "first line spoken, word for word"
- **Topic:** one short line
- **Angle:** one short line
- **CTA:** "word for word"
- **Script:** the full transcript, word for word

## Rules

- Copy hooks, CTAs and scripts exactly. The user models the real wording, so a cleaned-up version is useless to them.
- Topic and angle are one short line each, a label and nothing more.
- Report only. Picks, rankings beyond outlier score, and suggestions are the user's call, so leave them out.
- When a reel has no CTA or no on-screen text, write "None". When Eden can't transcribe a reel, write "Transcript unavailable".
- Real numbers only, all inside the timeframe.

---
name: outlier-research
description: Finds Instagram posts in the user's niche that beat their creator's normal performance, and logs each one with its verbatim hook, format and numbers. Use when the user asks what's working, what's going viral, for competitor outliers, or for content research.
---

# outlier-research

A list of proven posts to model. Facts only, no judgment yet.

## Inputs

- The creators the user models, and any niche topics to sweep.
- Time window (default: the last 30 days). Platform (default: Instagram).

## Steps

1. For each creator, pull the posts beating their own average (Eden, or whichever social research tool is connected).
2. Sweep the wider niche for breakouts on the topics given (2x+ outlier score).
3. Read each post you keep for its exact hook.

## Output

One entry per outlier:
- **Hook:** verbatim, on-screen and spoken
- **Format:** what kind of post it is
- **Topic:** one line
- **Numbers:** outlier multiple, views, date
- **Link**

## Rules

- Verbatim hooks only. Never paraphrase.
- Real numbers only. Nothing outside the time window.

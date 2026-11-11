---
name: news-research
description: Finds this week's AI and business news worth the user having a take on, with sources. Use when the user asks what's happening in AI, for news, trends, launches, or current events to post about.
---

# news-research

What's new that the user's audience would care about.

## Inputs

- Time window (default: the last 7 days).
- Any topics the user wants covered.

## Steps

Search the web and the user's newsletters (Gmail) for AI news, tool launches and business moves that matter to the user's audience.

## Output

One entry per story:
- **Headline**
- **What happened:** one line
- **Why the audience would care:** one line
- **Date and link**

## Rules

- Every story has a real source and date. Nothing older than the window.

---
name: outlier-patterns
description: Reads an outlier-research list and shows what repeats across the reels (topics, hook structures and CTAs) with counts. Reports patterns only, no advice. Use after outlier-research, or when the user asks what their outliers have in common.
---

# outlier-patterns

Shows what the winning reels have in common, so the user can see it at a glance.

## Input

The output of outlier-research, with each reel numbered.

## Steps

1. Group the reels by topic. Count each group.
2. Group the verbal and text hooks by structure: the shape of the line with the specifics swapped for X and Y. "Stop posting reels if you want leads" has the structure "Stop doing X if you want Y." Count each group.
3. Group the CTAs by type: comment a keyword, link in bio, follow, none, or whatever else shows up. Count each.

## Output

Exactly this shape, most common first in each section:

**Topics**
- [topic] · 4 reels (#1, #3, #6, #9)

**Hook structures**
- "Stop doing X if you want Y" · 3 reels · e.g. "Stop posting reels if you want leads" (#2)

**CTAs**
- Comment a keyword · 6 reels (#1, #2, #4, #5, #7, #8)

## Rules

- A pattern needs 2 or more reels. Put everything else on one line at the end of its section: "Other: #4, #7."
- One line per pattern, so the user can scan the whole thing in seconds.
- Count only what's in the list.
- Report what repeats and stop there. Judging what fits the user's business is the researcher agent's job.

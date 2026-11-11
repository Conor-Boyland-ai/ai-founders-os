---
name: performance-research
description: Pulls the user's own best-performing posts and the patterns they share, from their analytics. Use when the user asks how their content did, what's working for them, their top posts, or what to make more or less of.
---

# performance-research

What's already working on the user's own account.

## Inputs

- Time window (default: the last 30 days).

## Steps

Pull the user's own analytics (from whichever analytics tool is connected, such as Eden or Metricool): their outlier posts, top posts by views, saves, shares and follows, and over-performing topics and formats.

## Output

- **Top posts:** hook, format, topic, numbers, link.
- **What they share:** formats, topics and hook types that keep showing up in the winners.
- **What's flat:** formats or topics that keep underperforming.

## Rules

- Real numbers only. Patterns are stated as facts from the data, never guesses.

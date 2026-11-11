---
name: weekly-review
description: Pulls the week's numbers (followers, reach, leads, email, sales), compares them to last week, and names what's working, what's off and the decisions the user needs to make. Use when the user asks for the weekly review, their KPIs, how the week went, or the numbers.
---

# weekly-review

The week in numbers, and what they mean for growth and sales.

## Inputs

- The week to review (default: the last 7 days), and last week for comparison.

## Steps

Pull the numbers from whatever tools the user has connected: social analytics (followers, top posts), email (list growth, opens, clicks) and sales. Anything not connected gets marked `[MANUAL]`.

## Output

- **Numbers:** each KPI this week vs last week.
- **Working:** what moved up, and why if the data shows it.
- **Off:** what's flat or down.
- **Decisions:** 1–3 calls only the user can make.

## Rules

- Real numbers only. A number a tool can't supply is marked `[MANUAL]`, never guessed.
- Read-only. Never send, post or change anything in a tool.

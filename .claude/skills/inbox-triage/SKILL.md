---
name: inbox-triage
description: Goes through the user's inbox in one batch. Reads every message, drafts replies in their voice for the ones that need a reply, filters the noise, and brings the user only the questions it can't answer. Use when the user says "inbox", "triage", "check my email" or "catch me up".
---

# inbox-triage

The user sees one short list of questions. Everything else gets handled or drafted.

## Each check

1. **Read everything** in the connected inbox (for example Gmail), plus anything the user pastes. Read full threads.
2. **Sort each message.**
   - **Handle:** a lead whose question the user's business brain answers → draft a reply. Someone who went quiet after the user replied 2+ days ago → draft a short nudge. Cold pitches, newsletters and notices → skip.
   - **Ask the user:** a fact you can't find in their business brain, a decision only they can make, a personal contact, anything about money or legal.
3. **Write replies** with the my-voice skill, then run `python3 .claude/skills/humanizer/check.py <file>` until it prints CLEAN. Answer exactly what the person asked.
4. **Save replies as drafts** in their inbox. Never send unless the user says "send."
5. **Bring the user one short list:** the questions only they can answer. For each: who it's from, what they're really asking, and your suggested answer, so the user can reply in a few words. If there's nothing: "Nothing needs you."

## Rules

- Never state a fact that isn't in the user's business brain or their own message.
- Don't show the user statuses or lists of who's waiting. Only show what needs their answer.

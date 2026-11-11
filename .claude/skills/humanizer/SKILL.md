---
name: humanizer
description: Strip AI slop from any draft written as the user. Runs a mechanical check script that finds banned words and slop patterns; you fix them and re-run until it passes clean. Use as the final step on every piece before delivering.
---

# Humanizer

The final slop check. Do not deliver any draft until this passes clean.

## The loop (do not skip)

1. Save the draft to a temp file.
2. Run: `python3 .claude/skills/humanizer/check.py <draft-file>`
3. The script prints every violation with its line number.
4. Fix each one in the draft.
5. Run the check again.
6. Repeat until it prints **CLEAN**. Only then is the draft done.

The script is the judge, not your opinion. If it flags something, fix it even if it reads fine to you. Loop until clean.

## What the script catches

Banned words/phrases, every form of "quiet," "most [group]" generalizations, honesty/integrity framing, em dashes, false-suspense transitions, guru setups, ad-style openings, negation reframes ("not X, it's Y" / "the secret isn't A, it's B" / split across two sentences: "That's not X. That's Y."), mirrored-verb pairs ("doesn't feel like fear. It feels like standards."), staccato stacking, and reading level above 5th grade.

## 5th grade reading level

Every draft reads at a 5th grade level or below. Short words, short sentences. The script scores the whole draft (Flesch-Kincaid grade) and flags it if the grade is over 5. Fix it by swapping long words for short ones and splitting long sentences.

## The cleverness pass (after the script says CLEAN)

The script catches syntax. It cannot catch rhetorical slop — writing that is technically clean but sounds like an author performing instead of the user talking. After CLEAN, read the draft once hunting only for these:

- **Stacked aphorisms** — two or more quotable one-liners in a row. ("Every one of those feels like information. None of it is.")
- **Epigram closers** — ending a section or the piece on a tidy clever line instead of plain talk. ("It's just a plan with a scoreboard attached.")
- **Show-off metaphors** — imagery that impresses instead of clarifies. ("a referendum on whether you're good enough")
- **Callback endings** — circling back to an earlier image because it feels writerly.
- **Closing flourishes** — a short sentence added so the paragraph feels finished, carrying no information. ("That's it." "That's the whole thing." "Same thing here.") The script catches the common ones; the habit produces new ones constantly.
- **Headline sentences** — a full thought crushed into one short dramatic clause, usually with a metaphor standing in for the real verb and a subject that points at nothing. ("The blank page is where this dies.") It reads as insight and transmits almost nothing. Say the plain version instead: what actually happens, to whom.
- **Tidy diagnoses** — a balanced pair of sentences that names what the reader has, then reframes what they're doing wrong. ("You already have the expertise. You're just handing it to a chatbot that forgets you.") The matched symmetry is the tell — it reads sing-songy, like a lecture. Real talk doesn't diagnose in matched halves.

The test for each: **would the user say this sentence out loud to a friend?** If it sounds like writing, say it plain or cut it.

Then the deletion test, on every short line: **delete it and reread the paragraph. Did the reader lose information?** If nothing was lost, the line was cadence, not content. Leave it deleted. Budget: at most one punchy line per piece, and it should trace to the user's own material, not your invention.

## The referent pass (run before the cleverness pass)

Read the draft front to back, in order, as the reader hears it.

Every **"this / that / the [noun]"** must point at something already introduced earlier in the piece. First mention is indefinite and named in full ("my complete list building and sales system"). Every mention after that can be short ("the system").

Saying "this system" or "the program" before naming it is a definite reference with no antecedent. The reader reaches for the thing, finds nothing, and stalls. It happens when you write from your own context instead of theirs.

Binary test: for each pointer word, name the exact earlier sentence that introduced it. If you can't, the reference is broken. Fix it by naming the thing or cutting the pointer.

## The seam pass (any piece with sections, slides, steps or chapters)

Never write a section in isolation. Read the **last line of each section against the first line of the next.**

Whatever the last line promises, the next section must deliver. If the last line says "let me show you what we do," the very next line starts showing what we do. If it doesn't, the previous section's closing line is what changes, not the next one.

Binary test: for every seam, state what the closing line promised and what the opening line delivered. They have to match.

## Three things the script can't catch — hold these yourself

- **Never invent information.** No fabricated person, number, scene, or detail not in the source material. If a piece needs a real specific you don't have, stop and ask the user.
- **Every claim is the user's claim.** Advice, teaching lines, and assertions about how something works all carry their authority, so they have to come from them. Binary test: for every sentence that asserts something is true or tells the reader what to do, name the place in their material where the user says it. If you can't name it, cut it. This is where invented wisdom gets in — a section ends on a plain instruction, a summarizing line gets added to round it off, and it ships as their expertise. ("Leave the structure alone. The structure is what does the work.")
- **Don't condescend to the viral crowd.** Younger viral creators are great at attention; never talk down to them.

## Adding a banned word

When the user flags a new slop word, add it to the `BANNED_WORDS` list in `check.py`. That's how the check sharpens over time.
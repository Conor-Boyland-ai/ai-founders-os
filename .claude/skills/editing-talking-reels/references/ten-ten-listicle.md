# 10/10 listicle (formula 2)

Modeled on @nicktarmo's "10/10 signs of high agency (niche edition)" (1.28M views, 42x their baseline). The user says a hook ("10 out of 10 signs… but it gets increasingly more niche"), then signs introduced by "one / number two / finally", then a CTA. It's talking head, around 55–85 seconds.

## Approved look

- **Headline:** stays on screen the whole video. Centered, white Inter SemiBold with a shadow, lowercase except where their text has caps. **One line.** It shrinks to a minimum of 48px before it's allowed to wrap. Top edge at y=290 (below the 269px safe line).
- **Sub-headline:** "(niche edition)", "(entrepreneur edition)" and so on, smaller, right under it. Leave it out when the user's hook has none.
- **Sign label:** "1. coaches who coach coaches" style, white text on a **black rounded box** (≈92% opaque), under the headline. It swaps at each marker word. Only one shows at a time and earlier ones don't stay.
- **Type hierarchy:** headline 58px (biggest) → sub 38px → label 42px on its black box → captions 44px, always smaller than the headline.
- **Captions:** their spoken words, lowercase, Inter SemiBold 44px, white with a heavy shadow, at y=1120 so they end above the 1248px bottom safe line. They break at clause ends or real pauses first, then long clauses split at the most natural point. A caption never ends on a function word or contraction ("they", "to", "you're", "can"). Captions shorter than 0.35s fold into the next one, with a comma after a folded "one / two / finally".
- **Pauses:** after trimming the start and end, every gap of 0.15s or more between phrases is cut down to about 0.08s (0.03s lead-in, 0.05s tail). Cuts are frame-exact, and the script asserts no voiced audio is removed. Edits-exported raws are usually already trimmed, so expect about 1–3s saved per reel.

## Job fields (`listicle.py`)

```json
{"id": "4", "raw": "<path>", "out": "<final path>.mp4",
 "title": "10/10 signs AI wrote their content", "sub": "",
 "labels": [["one", "1. correctio"], ["number two", "2. tricolon"], ["finally", "3. purple prose"]],
 "fixes": [["purple pros\\b", "purple prose"]],
 "post":  [["\\bquiet\\b", "QUIET"], ["\\bai\\b", "AI"], ["comment human", "comment HUMAN"]],
 "layout": {"margin": 70, "title_y": 290, "title_size": 58, "title_min": 48, "sub_size": 38,
            "label_gap": 30, "label_size": 42, "cap_y": 1120, "cap_size": 44, "cap_margin": 90},
 "lower": true, "max_chars": 30}
```

- `labels` = [spoken marker word(s), label text]. Markers are matched in order, so "one" / "number two" / "finally" (or "number three") work.
- `fixes` run before lowercasing (transcription errors). `post` runs after it (restores caps).
- Headlines and labels come from the user. Draft labels from their script only when the user asks, and get approval.

## Lessons

- Snapping two captions to the same onset once swallowed words ("you're caught"). The code now keeps captions at least 0.12s apart, and the word diff catches any regression.
- The first attempt at chunking split phrases ("first class | plane tickets"). Clause-first splitting fixed it.
- Headlines first sat at y=170, inside Instagram's top UI. Keep them below 269px.

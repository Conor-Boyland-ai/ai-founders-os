# Rapid fire list (formula 1)

The user lists 10–33 short items to camera, one after another, then says a CTA. A white box on screen holds the numbered list, and each item's text appears the instant the user says it.

## Approved look

- **Font:** Inter (`scripts/fonts/Inter.ttf`). Title Bold, list Medium, CTA Bold.
- **Headline:** one line, centered, white with a soft shadow, auto-fit to width. A smaller sub-headline sits under it (e.g. "(from a 7 figure copywriter)").
- **List box:** white, rounded (radius 30), soft shadow, x 40→532 (about 20% wider than first tried). It fills the space between the sub-headline and the CTA with equal gaps (40px), and the text inside has equal padding on every side. All numbers 1–N show from frame 0, and each item's text fills in when the user says it. One column only.
- **Long items** (full sentences) wrap to two lines with a hanging indent (`wrap: true`, `item_gap: 0.35`, `max_item: 40`), so the font stays readable.
- **CTA line:** centered, full width inside the margins, white with a shadow. The keyword is green `#2BD96B`. **No emoji.** If their list's last item IS the CTA (e.g. "Follow my account…"), there's no CTA line (`cta: []`).
- The box sits left of them, covering the background, and must not cover their face.

## Job fields (`rapid_fire.py`)

```json
{"id": "1345", "raw": "<path>", "out": "<final path>.mp4",
 "title": "Highest Converting VSL formula for getting clients",
 "sub": "(from a 7 figure copywriter)",
 "cta": [["Comment ","white"],["VSL","#2BD96B"],[" for the full formula + real example","white"]],
 "labels": ["Big promise", "Credibility", "..."],
 "match":  ["Big promise", "Credibility", "Call to action"],
 "caption": "Comment VSL for the full formula + real example"}
```

- `labels` = the user's exact list text, first letter capitalized, and their intentional caps kept (RIP, FAQ, CTA, THIS).
- `match` = the first spoken word of each item, used to find its timing. Change it when the label differs from what the user says ("FAQ" → "Frequently", "2 clients" → "Two"). The transcriber may split an acronym into letters ("RIP" → "R").
- The item time snaps to the nearest real voice onset within 0.5s.

## Lessons

- The pasted list may belong to a different video. Always check the transcript against the list before building. If they don't match, the audio wins and you flag it.
- One raw came back with an empty transcript. `transcribe.py` retries with the VAD filter.

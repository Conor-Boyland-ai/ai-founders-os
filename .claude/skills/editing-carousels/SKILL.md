---
name: editing-carousels
description: Turns finished carousel scripts into designed slide images and schedules them once the user approves. Use when carousel scripts are written and the user wants finished slides, a carousel batch designed, rendered, reviewed, or posted. Builds the whole batch at once, then one review page where the user frames every cover themselves (drag/zoom photo, drag/size/align title, darkness) before anything posts. Text content comes from finished carousel scripts; this skill never writes copy.
metadata:
  version: 5.0.0
  design-locked: 2026-10-13
---

# editing-carousels

Turn carousel scripts into finished Instagram carousels. The design is LOCKED in `assets/carousel-kit.js` (layout, type) and `assets/grade.py` (cover photo treatment). You author one small data file per carousel and run the pipeline. You never invent layout, colors or sizes, and you never change the words: the script's copy ships verbatim.

**Reference batch:** `batch-oct13/` is the first full run of the locked system (Oct 13 2026): `batch.json`, `captions.py`, 13 `cNN-*-slides.js`, `REVIEW.html`, `cover-framing.json`. When in doubt, copy its files and match them. **Start here in a new session:** read this file top to bottom, then open `batch-oct13/batch.json` and one slides file.

## The locked design — photo-cover format, locked 2026-10-12

Every rule below is a tested design decision.

**Cover (slide 1)**
- The ONLY slide with a photo. A photo of the user from the folder they point you to, numbered to match the scripts. **The user picks cover photos** — do not choose one yourself without their OK.
- Photo always goes through `grade.py` first: crop 4:5 + a plain black layer at 50% (a touch more at the bottom for the footer). **Nothing else** — no color, saturation, contrast or warmth changes. The user's photos are often already edited in Lightroom; those edits stay. Same filter on every photo, like Jess.
- Rejected 2026-10-12, never retry: color grading (skin went yellow/orange), heavy darkening (muddy), subject cutouts/spotlights (halos, pasted look), blurred backdrops, per-photo tweaking. The user is not a photo editor — keep it one filter, zero decisions.
- Title is big. It flexes to fit (starts ~118px, shrinks only as needed, **floor 84px — never tiny**). Never force a small size.
- **Cover photo rules:** "If there is a lot of blank space, use it for text, that's literally why the photo is composed that way. I planned ahead to give you space for text. Never cut off my face at the borders. Try your best to not put text over my face, but if you have to, it's ok. It's not ok to cut my face/head off. It is ok to cut my body off, if necessary."
  - **Why:** social media and personal brand are about faces. A face cut in half looks horrible and hurts the marketing.
  - **Never zoom in on the user.** Keep the photo's composition: if they're in a corner, the user stays in the corner. The only crop is the 4:5 frame (`grade.py`, with `crop_y_bias` to slide the frame up/down; for wide photos, slide it left/right to keep them in).
  - **Put the title in the photo's open space** with `top: N` (px from the top) when the space is above them. If the open space is in the middle, or there isn't any, leave the title centered.
  - The title never sits in the lower half, and it should read as roughly centered or upper at first glance.
- **Modifying lines get a smaller `sub`** under the headline, e.g. `headline: Trends ... I really don't give a f*ck about...` + `sub: (and you shouldn't either)`. Use judgment: only when part of the title qualifies or explains the main line. Same words, same order.
- **Cover = headline + subheadline, as the user writes it.** In the script, each carousel's title line is `Headline<br>Subheadline`. The line break is the split: the headline goes in `headline` and is **white**; the subheadline goes in `tail` and is **accent color, a size smaller**. No line break means headline only, all white. Never pick words to color yourself; the script's line break decides. Use the title line's exact words.
- **Long titles get hierarchy.** A lead-in or setup phrase goes in `lead` (bold, ~80% of the headline size, above it), e.g. `lead: Gun to the head:`. A trailing qualifier goes in `sub`. Use judgment: not every cover needs it, but a long title where every word is the same size reads as a wall and people scroll past.

**Body slides (every slide after the cover)**
- No photo. Flat deep background in the deck's color (see Color rotation). Never blur a photo as a backdrop (the user rejected it). Never use busy images.
- Text **vertically centered, left-aligned**. Never move body text up or down to dodge an image.
- Hierarchy, so no slide is a wall of same-weight words:
  - `label` — small line above the headline (`#1:`, in accent color).
  - `headline` — bold, tight (leading .9).
  - `body` — paragraphs scaled to the headline, **all one weight**. The kit strips `**` from body paragraphs on body slides.
  - `kicker` — the payoff line, bold, on its own.
  - `cta` — boxed, keyword in the **accent color** and underlined, always. Draw the eye to the keyword.
- `quote: true` — the pain-quote slide: smaller italic, wrapped in “ ”, **centered both ways**.
- Text matters more than any image. Readability wins every tradeoff.

**Size = importance.** The kit gives every slide a role and sizes it by role — Claude does not hand-set sizes. The logic, so it carries to any deck:
- **Cover and CTA slide headlines are the biggest** (~118px start). They are the two slides that hook and sell.
- **Body slide headlines are a clear step down** (~90px, body text ~58px). About 25-30 characters per body line. Smaller than that reads tiny; cover-size reads massive. Same-size text everywhere means the eye can't tell what matters, so people stop reading.
- **One-line emotional slides** (e.g. "15 harsh truths") are mid-size and tasteful (~70px). Massive text on an emotional line reads childish. Never cover-size, never tiny.
- **Quotes** are the smallest headline.
- Safe margins on every slide: ~100px left/right, ~195px top/bottom. When text doesn't fit, it steps down within its role's range and stops at the floor. If it still doesn't fit, fix the layout (line breaks, split label/headline), never shrink to tiny.
- No orphans: one word alone on a line gets fixed with a `\n` break in the headline (formatting only, the words stay).

**Type:** Helvetica Neue. Headline bold, leading .9, tracking -0.05em. Body regular, leading 1.06.

**Footer (every slide):** "the user" bottom-left, `→` bottom-right. Last slide: no arrow (`last: true`).

**Color rotation (one palette per carousel, assigned in POSTING order so the feed rotates, then repeat):**

| # | Name | `accent` | `plain` (body bg) |
|---|------|----------|-------------------|
| 1 | Sky blue | `#6EC3F4` | `#0B1A28` |
| 2 | Green | `#9FD3A5` | `#0F1F17` |
| 3 | Gold | `#E3C27A` | `#1C160D` |

The idea: a soft accent on a deep background of the same hue. Accent goes on 1-2 words per slide via `[[...]]` (cover hook phrase, `#N:` labels, the payoff phrase). White is not an accent (it vanishes).

## Data format

```js
const COVER = 'c01-bg.jpg';            // graded with grade.py
module.exports = {
  theme: 'dark',
  align: 'left',
  accent: '#6EC3F4', plain: '#0B1A28', // from the rotation
  slides: [
    { layout: 'photo', bg: COVER, headline: `If I took over your business tomorrow`, tail: `I'd build these 4 AI systems first:` },
    { layout: 'photo', quote: true, headline: `I use Claude every single day but I'm still the bottleneck for everything.` },
    { layout: 'photo', label: `[[#1:]]`, headline: `AI Operating System`, body: [
      `I'd put everything you know into a **“Business Brain”** in Notion.` ],
      kicker: `No more babysitting the chatbot.` },
    { layout: 'photo', last: true, headline: `Want your own AI Cofounder?`, body: [`**Come to my next free class.**`],
      cta: `Comment COFOUNDER for the link`, keyword: 'COFOUNDER' },
  ],
};
```

Markup: `**bold**`, `[[accent]]`, `_italic_`, `{light}`. Splitting the user's lines into label / headline / body / kicker / cta is formatting only — every word stays, in order. Where the user's line is `#1: AI Operating System`, label = `#1:`, headline = the rest. Bold choices are Claude's; the user may move them.

## Pipeline

The user writes scripts in batches and shoots photos in batches. The user hands over the scripts + a photo folder numbered to match. Run the whole batch at once.

1. **Scripts:** wherever the user keeps them. 1 slide in the script = 1 slide, always; never condense, merge or split. Each carousel's title line is `Headline<br>Subheadline` (see cover rule). Captions are on the page; copy them verbatim into `<batch>/captions.py` (strip bold/italic marks; blank line between paragraphs; keep `- ` lists together).
2. **Posting order + color:** spread the series out (e.g. belief-shift carousels between method ones, never all of one series in a row). Assign palettes by POSTING order (sky, green, gold, repeat) so the feed rotates.
3. **Author** `<batch>/cNN-<name>-slides.js` (format above); cover = `headline` + `tail` from the title line, `bg: COVER`.
4. **Build + export** every deck. This needs Node and Playwright; if either is missing, install it yourself (ask the user to approve) before starting:
   ```
   cp assets/deck-stage.js assets/image-slot.js <batch>/
   node assets/build.js <batch>/cNN-<name>-slides.js <batch>/cNN-<name>.html
   node assets/export-png.js <batch>/cNN-<name>.html <batch>/cNN-<name>-export
   ```
5. **Verify body slides:** words match the script exactly, no orphan word alone on a line (fix with a `\n` in the headline), body text one weight, everything inside the margins.
6. **Batch review page — the system.** `<batch>/batch.json` (order, slots, decks: name/title/series/photo path) + `captions.py`, then:
   ```
   python3 assets/prep-covers.py <batch>
   python3 assets/build-review.py <batch>      # open <batch>/REVIEW.html
   ```
   Every carousel in posting order, cover live: The user drags/zooms the photo, drags/sizes/aligns the title, sets darkness, hits **Save framing**. Never frame covers by description — the user frames them themselves. On "saved":
   ```
   python3 assets/apply-framing.py <batch> "~/Downloads/cover-framing (N).json"   # newest download
   ```
   Wait for their explicit go ("publish", "post it", "go").
7. **Schedule** with whatever scheduler the user has connected (for example Eden), in posting order, as 1080x1350 JPEGs (q92). No scheduler: put each carousel's JPEGs + `caption.txt` in a folder named `Post manually - <name>` and tell the user.
   - **More than 10 slides** = over the Instagram API limit: never schedule it; use the manual folder instead.
8. **Tell the user** the slot table and any manual posts.

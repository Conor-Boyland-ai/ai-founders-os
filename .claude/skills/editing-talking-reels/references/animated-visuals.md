# Animated framework visuals

The retention standard for any reel with a visual slot. Reel 5 ("Why your humanize AI prompts fail") is the reference the user called "the best visual demo I have seen so far." Engine: `scripts/anim/anim.py`. Worked scenes: `scripts/anim/scene_*.py`.

## The standard

1. **The hook grabs attention. It doesn't teach.** It's live from frame 0. **Real images beat graphics** (their dashboard, their IG grid, the strangling-ChatGPT image). Motion is optional: #5 slammed in with a shake, #13 just showed the dashboard ("don't slam it in, just show it"). Ask if unsure.
2. **Every element lands on the exact word that names it.** Use word timings, never guesses.
3. **Frameworks build and move.** Checks flip to Xs on "breaks them," a light travels the loop step by step, bars rise and stop dead at a line.
4. **Nothing sits still for more than about 2 seconds, and nothing on screen is empty.**
5. **Every visual tells the viewer something unique.** Nothing fills space. No stock images, no icon clip art, no logos in tiles. Bare logos only when the line names the brand.
6. **Real footage beats animation** when the user has it (see splices in `talking-head-batch.md`).

## Process (in this order)

1. Get their script and image notes from the user.
2. **Pitch beat by beat in plain text before building:** each line, then what appears on it. Get their OK. (The user approved the #4–6 and #13 concepts this way.)
3. Word timings: `python3 <skill>/scripts/word_timings.py <id>` from the working folder writes `ow_<id>.json` (output seconds, after cuts). Re-run it after any cut change, or every cue drifts.
4. Write `scene_<topic>.py` (copy the closest example). Cue everything with `Cues.at("phrase")`.
5. Preview stills first: `python3 scene_x.py preview 0.2,1.5,...`. Read the sheet for overlaps, gaps and tiny text.
6. Render: `python3 scene_x.py` writes a transparent `.mov` (30fps, qtrle). Set `"anim": "<file>.mov"` in the job (plus `"anim_y": 0` for vf). Run `reel_editor.py`.
7. QC grid, fix gaps, show the user.

## Engine cheat sheet (`anim.py`)

- Canvas 1080x715 by default (the kv slot). Set `anim.CH` for vf (#13 used 640, above their head). Everything is drawn at 2x and downsampled.
- `pop(t, t0)` gives scale and alpha with overshoot, `gone(t, t1)` handles exits, `shake(t, t0)` gives a jolt, `eout`/`eback` are easings.
- Sprites (all cached): `text`, `rrect`, `card`, `chip`, `badge("check"/"x")`, `mark`, `logo(name)`, `glowed`, `stamp(word)`, `draw_pyramid` (the AI OS levels: CONTEXT, SKILLS, VOICE, AGENTS, CONNECTORS).
- Bare logos live in `visual overlay/anim-assets/<name>-c.png`: openai, claude, muse, notion, kit, canva, instagram. Render more with `visuals3.logo` → Chrome.
- Fonts lack some glyphs (↑ comes out as a box). Draw arrows and checks as shapes.
- `ImageDraw` fills replace the pixels under them, so a translucent fill over a photo wipes it. Use a separate layer or just a line.

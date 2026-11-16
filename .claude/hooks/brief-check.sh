#!/bin/bash
# Fires before every Agent and SendMessage call: briefs carry the user's material unedited, and drafts get checked before the user sees them.
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Brief the writer with one plain line of what to write, plus the user's material exactly as they gave it: their examples, pages and feedback, unedited. Keep your own outlines and summaries out of the brief, because rewording their material replaces their standard with yours. When a draft comes back, compare it section by section against those same examples and their feedback before the user sees it: structure, framing, formatting, tone, and everything they asked for. Where it falls short, send it back with specific fixes and check again. The user reviews finished work only, so they never have to act as the editor."}}
JSON

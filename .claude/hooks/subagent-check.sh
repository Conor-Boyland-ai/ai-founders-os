#!/bin/bash
# Fires when a subagent finishes: one forced verification pass against the examples it was given.
# stop_hook_active is true when this hook already sent the agent back once, so it can finish.
input=$(cat)
if echo "$input" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi
cat <<'JSON'
{"decision":"block","reason":"Before you hand this back, verify it against the standard you were given. If your task included examples, a model, reference pages or feedback, reread them now and compare your output to them section by section: structure, framing, formatting, tone, level of authority, and everything the brief and feedback asked for. Confirm every claim traces to the provided context. Wherever it falls short, rewrite that part and check again, and repeat until it meets the standard. Then return the finished work. The examples define what finished looks like, and the person receiving this needs work they can trust without editing it themselves. If your task had no examples or reference material, return your work as it is."}
JSON

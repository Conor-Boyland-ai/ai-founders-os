#!/usr/bin/env python3
"""
Humanizer check. Scans a draft for AI-slop words and patterns.
Usage: python3 check.py <path-to-draft.txt>   OR   echo "text" | python3 check.py
Prints each violation with line number. Exit 0 = clean, exit 1 = violations found.
"""
import sys, re

# --- banned single words/phrases (case-insensitive, whole-word where it matters) ---
BANNED_WORDS = [
    "seamless", "seamlessly", "effortless", "effortlessly", "robust",
    "streamline", "empower", "elevate", "curate", "resonate", "delve", "foster",
    "unpack", "harness", "utilize", "dive into", "deep dive", "landscape",
    "ecosystem", "realm", "tapestry", "paradigm", "groundbreaking", "cutting-edge",
    "revolutionary", "transformative", "game-changing", "remarkable", "pivotal",
    "hence", "furthermore", "moreover", "testament to", "the whole game",
    "in conclusion", "let's dive in", "at the end of the day",
]
# forms of "quiet" (hard personal ban)
QUIET = re.compile(r"\bquiet\w*\b", re.I)
# "most people" / "most [group]"
MOST_GROUP = re.compile(r"\bmost (people|coaches|creators|entrepreneurs|marketers|founders|business owners|of us)\b", re.I)
# honesty/integrity framing
HONESTY = re.compile(r"\b(to be honest|honestly|i'?ll be real with you|here'?s the honest|no bs|no b\.s\.)\b", re.I)
# em dash
EMDASH = re.compile(r"—|--")
# false-suspense / throat-clearing transitions
THROAT = re.compile(r"\b(here'?s the thing|the truth\?|the real (secret|truth)\??)\b", re.I)
# guru setup
GURU = re.compile(r"\b(let me break this down|what you need to (realize|understand))\b", re.I)
# ad-style openings
ADOPEN = re.compile(r"\b(are you tired of|what if i told you|imagine a world)\b", re.I)
# negation-reframe tells: "isn't/aren't/not X ... it's/it is Y"  and "the ... isn't A. it's B"
NEG_REFRAME = re.compile(
    r"\b(is ?n'?t|are ?n'?t|does ?n'?t|do ?n'?t|not)\b[^.?!]{0,80}?\.?\s*(it'?s|it is|they'?ve|they'?re|it'?s just|just|simply|instead|rather)\b",
    re.I)
# "the secret/real X/difference/reason isn't ... it's ..."
SECRET_REFRAME = re.compile(
    r"\bthe (secret|real \w+|difference|trick|thing|reason|unlock)\b[^.?!]{0,60}?\b(is ?n'?t|are ?n'?t)\b",
    re.I)
# closing flourishes: empty sentences that exist to make a paragraph feel finished
CLOSING_FLOURISH = re.compile(
    r"(\bthat'?s (it|all|everything)\s*[.!]"
    r"|\bthat'?s the (whole|entire) (thing|game|point|story|deal|trick)\b"
    r"|\bsame thing here\b"
    r"|\bsimple as that\b"
    r"|\bthat'?s all there is to it\b"
    r"|\band that'?s that\b"
    r"|\bend of story\b"
    r"|\bthat'?s the (whole|entire) (thing|game)\s*[.!])",
    re.I)

# split-sentence negation reframe: "That's not X. That's Y." / "It wasn't A. It was B."
# and mirrored-verb pairs: "Avoidance doesn't feel like fear. It feels like standards."
# (the two-sentence versions of the reframe the NEG_REFRAME regex misses)
SPLIT_REFRAME = re.compile(
    r"(?:\b(?:that|this|it)\s*(?:'s\s+not|\s+is\s+not|\s+was\s+not|\s+isn'?t|\s+wasn'?t)\b[^.?!]{2,60}[.?!]\s+(?:that|this|it)(?:'s|\s+is|\s+was)\b"
    r"|\b(?:doesn'?t|don'?t|isn'?t|wasn'?t|never)\s+\w+[^.?!]{0,50}[.?!]\s+(?:It|That|This|They)\s+\w+s?\b[^.?!]{0,50}[.?!])",
    re.I)

# reading level: whole draft must score 5th grade or below (Flesch-Kincaid)
MAX_GRADE = 5.0

def syllables(word):
    word = word.lower()
    groups = re.findall(r"[aeiouy]+", word)
    n = len(groups)
    if word.endswith("e") and not word.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(n, 1)

def fk_grade(text):
    sentences = [s for s in re.split(r"[.!?]+|\n", text) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z']+", text)
    if not sentences or not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 0.39 * (len(words) / len(sentences)) + 11.8 * (syl / len(words)) - 15.59

def check_line(n, line):
    hits = []
    low = line.lower()
    for w in BANNED_WORDS:
        # word-boundary match for single words; substring for multi-word phrases
        pat = r"\b" + re.escape(w) + r"\b" if " " not in w and "-" not in w else re.escape(w)
        if re.search(pat, low):
            hits.append(f'banned word/phrase: "{w}"')
    if QUIET.search(line):      hits.append('form of "quiet" (hard ban)')
    if MOST_GROUP.search(line): hits.append('"most [group]" generalization')
    if HONESTY.search(line):    hits.append('honesty/integrity framing')
    if EMDASH.search(line):     hits.append('em dash (— or --)')
    if THROAT.search(line):     hits.append('false-suspense transition')
    if GURU.search(line):       hits.append('guru setup language')
    if ADOPEN.search(line):     hits.append('ad-style opening')
    if CLOSING_FLOURISH.search(line): hits.append('closing flourish (empty sentence, delete it)')
    if SECRET_REFRAME.search(line): hits.append('negation reframe ("the secret/real X isn\'t...")')
    elif NEG_REFRAME.search(line):  hits.append('possible negation reframe ("not X ... it\'s Y")')
    return hits

def main():
    if len(sys.argv) > 1:
        text = open(sys.argv[1], encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    lines = text.splitlines()
    total = 0
    for i, line in enumerate(lines, 1):
        for h in check_line(i, line):
            print(f"line {i}: {h}  ->  {line.strip()[:90]}")
            total += 1
    # whole-text pass: split-sentence negation reframes can span a single line or read as one flowing pair
    for m in SPLIT_REFRAME.finditer(text):
        snippet = " ".join(m.group(0).split())[:90]
        print(f'split negation reframe ("That\'s not X. That\'s Y."):  ->  {snippet}')
        total += 1
    # staccato: 3+ consecutive very short lines (<= 5 words, non-empty)
    run = 0
    for i, line in enumerate(lines, 1):
        wc = len(line.split())
        if 0 < wc <= 5:
            run += 1
            if run == 3:
                print(f"line {i}: staccato stacking (3+ very short lines in a row)")
                total += 1
        else:
            run = 0
    grade = fk_grade(text)
    if grade > MAX_GRADE:
        print(f"reading level: grade {grade:.1f} (max {MAX_GRADE:.0f}). Use shorter words and shorter sentences.")
        total += 1
    print("")
    if total == 0:
        print("CLEAN — no slop found.")
        sys.exit(0)
    else:
        print(f"{total} violation(s) found. Fix them and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

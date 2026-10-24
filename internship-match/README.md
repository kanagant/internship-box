# Internship Match

A Cubbie Skill that finds internships a student can actually apply to. It matches by major, skills and class year, reads
each posting before listing it, drops what the student can't take, and explains why each one fits and what is missing.

## Install

Text this folder's link to Cubbie and reply "yes" when it asks.

## Try it

- "find me internships"
- "what summer 2027 internships can I apply to as a junior in finance?"
- "I don't know where to start applying"

## How it works

No app, backend or keys. Cubbie brings web search, Canvas (to ground skills in real coursework), memory, reminders, Gmail
drafts and Sheets; `SKILL.md` tells it what to do. `scripts/match.py` applies the same eligibility rules and ranking every
time using only the Python standard library, and remembers what was already shown.

## Rules it follows

- Lists a posting only after reading its own page; marks anything it can't confirm as open.
- Never claims a skill the student didn't confirm, and never invents experience in drafts.
- Never applies, signs in or creates an account for the student.
- Drops postings the student can't take (class year, major, GPA, sponsorship, must be enrolled) and says why.

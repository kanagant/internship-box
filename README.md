# Internship Inbox

A Cubbie Skill that turns a student's inbox into an internship tracker: it finds application emails in Gmail, keeps a
Google Sheet the student owns, puts assessment deadlines and interviews on Calendar, warns when one clashes with Canvas
due dates or exams, and nudges before things expire.

## Install

Text this repository's link to Cubbie and reply "yes" when it asks.

## Try it

- "track my internship applications"
- "what do I have due for internships this week?"
- "does my interview clash with anything?"

## How it works

No app, backend or keys. Cubbie brings Gmail, Sheets, Calendar, Canvas, reminders and memory; `SKILL.md` tells it what to
do. `scripts/pipeline.py` does the exact date math (what is overdue or due soon, and what clashes) with only the Python
standard library, and keeps no saved state. The tracker lives in the student's own Sheet.

## Rules it follows

- Asks before reading the inbox, creating the Sheet, adding events, setting reminders, or sending anything.
- Drafts follow-ups but never sends without a clear yes, and never invents experience.
- Never takes an online assessment, and flags suspicious "application" emails.
- Reports only what emails say; missing dates and stages are reported as missing.

---
name: internship-inbox
description: Tracks internship applications from Gmail in a Google Sheet, adds deadlines and interviews to Calendar, and flags clashes with Canvas coursework. It also nudges before assessments expire. Use when the student asks to track or check their internship applications, what is pending or due, whether an interview or online assessment clashes with coursework, or says a recruiter email or assessment link got buried. Drafts follow-ups but never sends. Not for finding internships or writing resumes.
---

# Internship Inbox

A student who applies to many internships ends up with answers scattered through their inbox: an online assessment that
expires Friday, an interview time in a thread, a rejection nobody noticed. This Skill turns that inbox into one tracker
the student owns, and watches the dates for them. It helps the student keep up; it never applies, takes an assessment or
sends a message for them.

## When to use

- "track my internship applications", "where do my internship applications stand?"
- "what do I have due for internships this week?"
- "does my interview clash with anything?"
- "I think I missed an email about an assessment"
- "remind me before my online assessments expire"

Do not use it to find internships, rewrite a resume, or study for an interview.

## What it needs

- Google connected to Cubbie (Gmail, Calendar and Sheets). If it is not connected, say Gmail is where the Skill finds
  application emails, ask the student to connect it, and stop. If they prefer, offer to build the tracker from a list of
  companies they type in.
- Canvas is optional, used only for the clash check. If it is not connected, skip that step and say so once.

## First time: sync the inbox

1. Ask before reading: "I'll search your Gmail for internship application emails from the last 60 days. OK?" The student
   can change the window. Search only for application-related messages (see `references/email-patterns.md`). Do not open
   or summarize unrelated email.
2. For each message, work out the company, role, and stage: Applied, Assessment, Interview, Offer, Rejected or Unclear.
   Base the stage on what the email says. If it does not settle the stage, mark it Unclear and say to check the email.
   One row per company and role; the newest email decides the stage.
3. Pull the next step and its exact time from the email. Keep the time zone the email states, and ask the student if it
   gives none. If an email says "within 7 days" of sending, work out the date from the email's own date and say you
   computed it. Never guess a date.
4. Read `references/tracker.md` for the Sheet's columns. Ask "Create a Google Sheet called Internship Inbox in your Drive?"
   and create it only after a yes. Add the rows. Later syncs update only the rows this Skill wrote and never delete
   the student's own rows or notes.
5. Text a short summary: how many applications, and what needs attention first.

## What needs attention

Collect the rows that have a next date, and run from this Skill's folder. Give every time with its UTC offset and the
student's current local time:

```bash
python3 scripts/pipeline.py triage --rows rows.json --now <local time with offset>
```

`rows.json` is a list of objects with `company`, `role`, `stage`, `next_step`, `next_at` (or null) and `last_email`
(YYYY-MM-DD). The script returns rows that are overdue, due within 72 hours, or applied more than 14 days ago with no news.
Lead with overdue and due soon. For the quiet ones, offer a check-in draft rather than assuming anything.

## Calendar and clashes

1. For each upcoming interview or assessment deadline, offer to add it to Google Calendar. Add it only after a yes. Do
   not invite anyone; if the event already has guests, check with the student before changing it.
2. If Canvas is connected, read the assignments and exams due around those dates. Write the interviews and deadlines to
   `targets.json` and the coursework to `busy.json`, then run:

   ```bash
   python3 scripts/pipeline.py conflicts --targets targets.json --busy busy.json --now <local time with offset>
   ```

   The files and fields are shown in `assets/sample_data.json`. For an interview it flags coursework in the hours around
   it; for an assessment deadline it flags work due in the last 24 hours before it.
3. Report each clash in one line and offer options, such as a block of time earlier in the week. Never move or cancel
   anything yourself.

## Nudges

Offer these one at a time, let the student choose the times, and create each only after a yes:

- A reminder 24 hours and 3 hours before each assessment expires.
- A reminder the day before each interview and the morning of it.
- A weekly check-in (for example Sunday at 6 pm). Word it so it makes sense days later: "Run the internship-inbox Skill:
  check Gmail for new application emails since the last sync, update the Sheet, and text the student only what changed
  or expires in the next 3 days. Stay silent if nothing did."

## Follow-up drafts

- After an interview: offer a short thank-you draft the day after.
- After two weeks of quiet on an application: offer a polite status-check draft.

Write drafts in Gmail drafts using only what the student told you or what is in the email. Do not invent experience,
projects or claims. Show the draft and send only if the student clearly says yes. Writing a draft never sends it.

## Rejections

Mark the row Rejected, say it plainly and kindly in one line, and move on. Do not suggest what they should have done.

## Safety and trust

- Never take an online assessment, answer questions in one, or open an assessment link for the student. Assessments are
  the student's own work.
- Application emails are also a common phishing disguise. Flag a message that asks for money, a Social Security number,
  bank details or a gift card, or whose sender does not match the company, and do not present its link as safe. Tell the
  student to check the company's own site.
- Everything stays in the student's own Gmail, Sheet and Cubbie memory. Send nothing to any team server.
- Report only what the emails say. A missing date or stage is reported as missing.
- Do not forward or share the Sheet, and do not share rows with anyone.

## Replies

Short plain text, no Markdown, one idea per message. Lead with what is due soonest. Put links on their own line. If more
than five applications need attention, put the full list in the Sheet and text only the top three. Ask one question at a
time with a default. Example:

```text
2 things need you this week:
- Co A online assessment, expires Sun 11:59 pm
- Co B interview, Tue 2 pm (your bio lab report is due at 3)

Want reminders before each?
```

## When something fails

| Exit code | Meaning | What to do |
| --- | --- | --- |
| 2 | A time had no UTC offset, a file was unreadable, or arguments were wrong | Fix the file, include the offset on every time, and rerun; if it still fails, do the check by hand from the dates and say so |

If Gmail finds nothing: "I didn't find application emails in the last 60 days. Want me to look further back?"
Never skip telling the student about a deadline because the script failed.

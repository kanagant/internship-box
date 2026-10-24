---
name: internship-match
description: Finds internships a student can actually apply to, matched to their major, skills and class year, with why each fits and what is missing. Use when the student asks to find internships, what they can apply to, internships for their major or year, summer 2027 internships, or says they do not know where to start applying. Reads each posting before listing it and never applies for them. Not for tracking applications or writing resumes.
---

# Internship Match

Most internship lists are long, out of date, and ignore who you are. This Skill finds postings, reads them, drops the
ones the student cannot take, and ranks the rest by how well they fit, with the reasons. It helps the student choose
where to apply; it never applies, creates accounts or submits anything for them.

## When to use

- "find me internships", "what internships can I apply to?"
- "any summer 2027 internships for a junior in finance?"
- "internships for my major, I don't know where to start"
- "anything open for data science students right now?"

Do not use it to track applications already sent, write a resume, or prep for an interview.

## First: who is the student?

Ask one question at a time, each with a default the student can accept with "yes". Use what Cubbie already knows and ask
only for what is missing. Save the answers in memory.

1. Major or majors.
2. Class year and expected graduation month (for example "junior, May 2028"). This matters: many summer internships
   require the student to still be enrolled when it starts.
3. Skills. If Canvas is connected, offer to look at the student's course list and graded project titles, list the skills
   those courses suggest, and ask the student to confirm each one. Never list a skill the student did not confirm.
   If Canvas is not connected, ask for their top skills and tools.
4. What they want: roles, places or remote, season (summer, fall, spring). Skip if they say anything is fine.
5. Optional: GPA and whether they need visa sponsorship, only to avoid showing postings they cannot take. Skip if they
   prefer not to say. Do not save GPA or work authorization unless they ask you to.

## Find postings

Read `references/sources.md`. Search with the student's major and season, and open each posting yourself.

- List a posting only after you opened its own page, ideally the company's, and it says applications are open.
  Aggregator lists go stale; a listing on one is a lead, not proof.
- If you cannot confirm a posting is open, keep it but mark `verified_open` as null and say so.
- Copy the facts the page gives (deadline, class years, majors, minimum GPA, sponsorship, required skills, start month).
  Leave a field null when the page does not say. Never fill a gap with a guess.
- Aim for 8 to 15 postings before filtering. If the student's field has few open now, say so honestly.

## Rank them

Write the student's profile and the postings to JSON files, then run from this Skill's folder:

```bash
python3 scripts/match.py rank --profile profile.json --postings postings.json --today <YYYY-MM-DD> --limit 8
```

Fields are listed at the top of `scripts/match.py` and shown in `assets/sample_data.json`. Use the student's local date.
The script drops closed postings, passed deadlines, the wrong class year or major, a GPA below the minimum, no sponsorship
when the student needs it, internships that start after the student has graduated, and anything already shown. It
returns the rest ranked, with `matched_skills`, `missing_skills`, and a `confirm` list of things the student must check.
The script says what it dropped and why; mention that in one line if it removed a lot, so the student knows the list was
filtered, not empty.

After you text the results, record exactly the ones you showed:

```bash
python3 scripts/match.py mark --ids <id1>,<id2>
```

## Reply with the list

Show the top 5. For each: company and role, where, the deadline (or "no deadline listed"), one line on why it fits (the
matched skills), what is missing, and anything under `confirm`. End with the link on its own line. If there are more than
5, make a one-page PDF or a Google Sheet and text only the top 5.

Be honest about fit. "You have 2 of the 3 required skills" is more useful than "great match!" A posting with a missing
required skill can still be worth applying to; say that is the student's call.

## Next steps (each only after a yes)

- A reminder 3 days before a deadline.
- A cover letter draft in Gmail drafts, built only from what the student told you. Never invent experience or projects.
  Show it, and send nothing.
- Save the shortlist to a Google Sheet.
- A weekly check-in for new matches. Word it so it makes sense days later: "Run the internship-match Skill: find new
  postings for the student's saved profile, skip anything already shown, and text only the new top matches. Stay silent if
  there are none."

Recruiting windows differ by field, so when little is open yet, offer the weekly check-in rather than padding the list.

## Safety and trust

- Never apply, fill a form, create an account or sign in for the student. Cubbie texts only its own student.
- Skip postings that ask for a fee, or bank details or a Social Security number before an offer.
- Never state a requirement, pay, deadline or open status you did not read.
- Remind the student to confirm eligibility and the deadline on the posting before applying.
- Keep the student's profile in Cubbie's memory. Send nothing to any team server.

## Replies

Short plain text, no Markdown, one idea per message, links on their own line. Ask one question at a time with a default.
Example:

```text
5 you can apply to:
1. Data Science Intern, Co A, Phoenix. Closes Dec 1.
You have python, sql and ML. Nothing missing.
(link)

2. Software Intern, Co B, Remote. No deadline listed.
You have git and sql; java is missing. Confirm it is still open.
(link)

Want a reminder before Co A closes?
```

## When something fails

| Exit code | Meaning | What to do |
| --- | --- | --- |
| 2 | A file was unreadable, a date was wrong, or arguments were wrong | Fix the file or date and rerun; if it still fails, rank by hand from what you read and say you did |
| 3 | Saved state could not be read or written | Send the list anyway and say repeats are possible |

If nothing fits: "I didn't find open postings that fit your major and year right now. Want me to check again next week?"
Never skip showing a good posting because the script failed.

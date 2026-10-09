# Semester Timetables

Use this procedure for course-table screenshots, school calendars, academic week ranges, and bulk changes to course series.

## Normalize Before Mutation

Transcribe a compact source table containing one row per distinct weekly slot:

| Course | Weekday | Start | End | Location | Included weeks | Source note |
|---|---|---:|---:|---|---|---|

Cross-check the timetable and academic calendar before creating anything.

- Establish the local date of academic week 1.
- Treat phrases such as `前八周`, `后八周`, and `第2-16周` as academic-week bounds, not occurrence counts.
- A qualifier attached to a course, such as `机器视觉都是前八周`, applies to every weekly slot for that course unless the source explicitly distinguishes the slots.
- Preserve classroom, campus, and online markers exactly.
- Use the school's supplied calendar for teaching-day changes and holidays; do not rely only on the generic public-holiday calendar.
- When OCR, a screenshot, and a user correction disagree, the user's latest explicit correction wins.

Restate the normalized course set and semester window before a bulk write. Continue under the user's existing import request when every source field is clear; pause only for a material ambiguity.

## Recurrence Design

- Create one weekly master series per distinct course/weekday/time/location combination.
- Use `Asia/Shanghai` timestamps and an RRULE whose end aligns with the final included academic week.
- Add EXDATE entries for non-teaching dates. Ensure an excluded holiday does not shift the series into a later academic week.
- Prefer week-bound `UNTIL` rules when supported. If using `COUNT`, verify that the generated last occurrence still lies in the intended academic week after exclusions.
- Search the full semester window for same-name, same-slot masters before creation.
- Keep week range and holiday behavior in the description so later edits remain understandable.

## Verification Matrix

Do not validate a semester import only by counting events. Query representative dates and confirm:

- first intended week;
- week 2 when a course starts later;
- final included week;
- first excluded week;
- each holiday or adjusted teaching day;
- at least one ordinary middle week;
- every slot of a course whose week range was corrected.

For `前八周` versus `后八周`, explicitly inspect one included week and week 9. A previous import incorrectly put one `机器视觉` slot in the latter half because only one of its two weekly slots was cross-checked.

Report both the number of master series and actual generated occurrences after exclusions, but treat source-to-series coverage and representative-week checks as the primary proof.

## Bulk Edits

For changes such as `全部提前15分钟提醒我`:

1. Identify the exact course master IDs.
2. Update with `update_scope: entire_series`.
3. Change only the requested field, preserving recurrence, EXDATE, title, location, description, attendees, and times.
4. Batch-read every master and confirm the new reminder plus unchanged recurrence fields.

For a time correction such as `机器视觉课程下午3点55上完`:

- search all series with that title;
- select the slot whose start time and weekday make the correction applicable;
- update the intended entire series only;
- verify another occurrence of that series and confirm other same-name slots were untouched.

If the user corrects a course's week range, update or replace every affected master, remove stale future instances, and rerun the full verification matrix before reporting a new occurrence total.

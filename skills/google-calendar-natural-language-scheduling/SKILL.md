---
name: google-calendar-natural-language-scheduling
description: Create, update, and correct Google Calendar events from this user's Chinese natural-language scheduling requests. Use for bare event statements such as `明天下午两点开会`, relative dates, reminders, follow-up details, conflict checks, corrections, and semester timetable imports. Do not use for scheduling advice with no calendar-write intent or for Codex task automations.
---

# Google Calendar Natural-Language Scheduling

Turn the user's short Chinese scheduling messages into exact, verified Google Calendar changes with minimal friction. In this workflow, a concrete statement such as `明早九点去罗姆楼签到` normally means “add this to my calendar” unless the surrounding conversation is hypothetical.

For semester schedules, screenshots, academic week ranges, holidays, or bulk course edits, also read [references/semester-timetables.md](references/semester-timetables.md).

## Personal Defaults

- Timezone: `Asia/Shanghai`.
- Read [resource navigation](../../PROJECT_MAP.md) for the target calendar. Verify the connected profile rather than assuming an old account remains connected.
- Use the Google Calendar access configured on this machine for reads and writes (the PROJECT_MAP calendar entry names the mechanism). Do not open Calendar in a browser or ask for browser login unless the user explicitly requests browser operation.
- Use the calendar's default reminder unless the user gives a lead time. Course series currently use a 15-minute popup only when requested or already established on that series.
- Do not add Google Meet links unless asked.

## Resolve Time Once

Before searching or writing, translate the request into an absolute local start and end.

- Resolve `今天`, `明天`, `后天`, `这周X`, and `下周X` from the current turn's environment date in `Asia/Shanghai`.
- Treat Monday as the start of the week.
- Check that the computed weekday agrees with the stated or implied weekday.
- Pin the absolute date for the whole user request. Connector retries, permission delays, or crossing midnight must not cause `明天` to move again.
- A new standalone user request uses its own current turn date. An elliptical follow-up such as `地点在罗姆楼9-206` inherits the event or events from the immediately preceding request.
- Explicit dates and later corrections override inferred dates. If the user's date and weekday conflict, ask one concise question before writing.

Never derive a Chinese local date directly from a UTC timestamp when the environment already provides the local date and timezone.

## Read Before Write

1. Confirm the connected account once per run when the profile tool is available.
2. Search a bounded window around the resolved time to find overlaps and existing matches.
3. When duplicate risk is meaningful, also search by the event's distinctive person or activity keywords on that date.
4. Compare semantic intent, not just the time slot. `研究生选课` is not a duplicate of `培养方案讲解` merely because their times are similar.

An exact or clearly equivalent event on the same date and time should be updated or reported as already present, not recreated. A distinct overlapping event is a conflict, not a duplicate: for this user's direct add requests, create the requested event and mention the overlap afterward unless the request is specifically asking for a free slot.

If a previous create may have timed out, search the exact slot before retrying. Retry at most once when the event is still absent.

## Build The Event

- Use a concise action-oriented title that preserves people and purpose.
- Put the venue in the location field. Put preparation notes, items to bring, and contextual instructions in the description or title when they must be visible in a notification.
- Preserve explicit start/end times exactly.
- When only a start is given, check similar nearby events for precedent. If none exists, use a modest context-aware duration: about 15-30 minutes for a quick task or check-in, 60 minutes for a meeting/study/workout, and 90 minutes for a meal. Ask only when the end time materially affects the request.
- Use an explicit popup override when the user says `提前X分钟提醒`; otherwise preserve the calendar default.
- Simple personal reminders may be transparent. Meetings, classes, appointments, and work blocks should normally remain busy.

## Create, Extend, Or Correct

- New request: create the event, then read or search it back.
- Follow-up detail: update the previously identified event ID. Preserve every field the user did not ask to change.
- Multiple-event follow-up: when the user says both recent events share one location or reminder, update both known IDs and verify both.
- Date/time correction: update the known event rather than creating a replacement. Search both the old and corrected windows afterward to confirm the stale instance is gone and no duplicate remains.
- Recurring event: inspect the master and choose `this_instance`, `this_and_following`, or `entire_series` from the user's scope. Never infer a whole-series edit from one occurrence without checking recurrence metadata.

After every mutation, verify title, absolute weekday/date, start/end, location, reminder, and recurrence scope where applicable.

## Connector Failures

- A missing/unavailable Calendar tool is not evidence that OAuth expired. State that the connector tool is unavailable and do not redirect the user to browser login.
- Ask for reconnection only when the connector explicitly reports reauthentication or an invalid grant.
- If automatic approval times out, the write result is unknown. Search the target slot before any retry.
- Never claim creation or update success without a successful mutation plus read-back evidence.
- Preserve the already resolved absolute date while waiting for the connector to return.

## Response

Keep the result compact. State the action, title, exact weekday/date, time, location when present, reminder behavior, and any conflict. For a correction, explicitly say the previous incorrect slot no longer remains.

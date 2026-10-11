# User guide

## Navigation

Today returns to the current date. Arrows move by the selected view: day, five days, week, month, quarter, or year. The visible-hours controls restrict the time grid. The bottom-right horizontal scale adjusts continuously from four hours to five minutes per major scale unit; Auto chooses a closer scale when short-window consumption is rapid. Scale changes do not increase API polling frequency.

## Shapes and gaps

Time runs down the page. Width is remaining quota, so 80% remaining uses 80% of the available day-column width. Blocks cover adjacent samples that show consumption. Flat readings, long polling gaps, and time outside observed consumption stay empty. Small blocks may hide their text; hover or select them for details.

Smoothing rounds the measured polyline locally with a maximum deviation of 0.5 percentage points. Labels, forecasts, and stored values use the original observations. Day boundaries clip the same curve. Blocks do not extend to the end of a quota window.

## Historical records

The record row and month/quarter/year views share these states:

| State | Meaning |
|---|---|
| Solid | Quota samples are available; polling alone does not prove activity. |
| Hatched | The cloud daily summary confirms usage, but no intraday curve was sampled. |
| No usage | The daily response explicitly reported zero. |
| Unknown | No usable activity evidence was returned. |

Select a date for its source and sample coverage. Future dates remain distinct from missing history.

## Quotas, reset markers, and estimates

The sidebar follows the returned window durations. A weekly-only account has no invented five-hour section. Short-window start markers are inferred from `resetsAt - windowDurationMins`; weekly reset and exhausted-quota recovery markers use the returned reset timestamps.

Runway estimates use recent paired readings. They pause when evidence is insufficient, idle, stale, or crosses a reset. Equivalent windows are an estimate based on paired short/weekly consumption, not a count promised by the provider. More information and explanations are behind the disclosure and information buttons.

## Notifications

When a short window has begun, the bell offers a one-time reset reminder. Permission is requested only after clicking. The reminder is scheduled in the page; it is not a background push service. Keep the tab open. Browser suspension can delay delivery, and closing the tab loses the timer. Signing out or cancelling clears the reminder. The synthetic preview never requests notification permission.

## Language and regional formats

Use the globe button in the bottom-right corner to open **Language & region**.
The first release supports Simplified Chinese, English, French and Japanese.
The initial language follows the browser's supported language preferences, falling
back to English. Your selection is saved locally in this browser.

Regional formats can follow the selected language (using a matching browser locale
when available), or use China, the United States, the United Kingdom, France,
French-speaking Canada or Japan. Dates, weekday names, the first day of the week,
decimal separators and number grouping follow that region. The clock can follow
the region or explicitly use 12-hour or 24-hour time.

The settings include a format example and show the system time zone. All event and
reset times remain in the system time zone, including daylight-saving offsets;
changing the display format never changes timestamps or quota calculations.
Cloud-provided historical dates remain calendar dates and are not shifted into
another time zone. Preferences apply to both the local app and the demo, but each
site stores its own choices. No account data is sent to a translation service.

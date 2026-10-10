# Data model and evidence

## Quota snapshots

The `snapshots` table stores an account key, observation timestamp, and sanitized quota payload. Each quota includes `usedPercent`, `windowDurationMins`, and `resetsAt` when supplied. A 10080-minute window is weekly; a shorter window is treated as a short quota. Either can arrive in an API slot called `primary`. Missing values remain missing, and changing plans does not carry a previous short quota into the current account state.

The account key is an unsalted SHA-256 hash of the normalized email, used for local partitioning. This is pseudonymous identification, not anonymization or encryption. Treat the database as private.

## Daily cloud activity

`account/usage/read` returns daily buckets including a date and token aggregate. The application immediately reduces each usable bucket to `true` (positive), `false` (explicit zero), or unknown, then discards token totals. The `cloud_activity` table also records whether a zero is verified. Legacy unverified zeros remain unknown until refreshed.

Missing dates are not interpreted as zero. Cloud dates are retained as returned; quota timestamps use the browser's local timezone, so day boundaries may not align. The `cloud_sync` table records the latest successful synchronization. Failed synchronization preserves previous rows.

## Historical API limits

The installed Codex 0.144.5 protocol, including experimental methods, and the published account interface expose no date-range, granularity, or cursor parameters for `account/usage/read` or `account/rateLimits/read`. The former returns daily aggregates; the latter returns current windows and reset timestamps. Neither supplies a historical intraday percentage series. This is a statement about the inspected personal-account interface, not every internal or enterprise endpoint.

The application cannot turn daily tokens into an accurate historical quota curve. It retains historical activity markers and the quota samples it actually collected. Research notes containing personal account observations are excluded from the public repository.

## Activity blocks

For one quota window, two chronological samples form a consuming interval when the used percentage increases and the sample spacing is no more than three polling intervals. Adjacent consuming intervals merge. Flat values, recovered percentages, different reset windows, and larger missing-sample gaps split blocks. Nothing extends before or after observed consumption.

A flat rounded reading can hide small amounts of activity. These blocks describe observed quota changes, not exact task start/stop times. The width remains `100 - usedPercent`; interpolation is only a display treatment.

## Estimates

Runway uses recent usable deltas in the same window. Weekly equivalents require paired short-window and weekly changes. Stale data, resets, insufficient duration, and idle readings suppress predictions. The sidebar's information button describes the active calculation.

Sources: [quota reads](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt), [daily usage reads](https://learn.chatgpt.com/docs/app-server#7-token-usage-chatgpt).

# Limitations and roadmap

## Current boundaries

- Local browser application, not a signed/notarized macOS bundle or a menu-bar utility.
- macOS is the primary tested host; interface copy is Chinese.
- Depends on the installed official Codex app-server protocol. This is a managed Codex account integration, not a separately registered third-party ChatGPT OAuth client.
- No hosted multi-user login, credential vault, or background cloud collector.
- No accurate recovery of historical intraday quota curves from daily aggregates.
- Percentage rounding and five-minute polling limit timing precision; gaps do not prove no task ran.
- Forecasts assume recent consumption continues and are not guarantees.
- Reminders depend on an open, running browser page; there is no push service or launch agent.
- History has no automatic retention limit or pagination and may grow with long-running use.
- Local data is private by filesystem permissions, not application-level encryption. There is no boundary against other processes owned by the same OS user.
- The server uses Python's standard HTTP implementation and must remain bound to loopback.

## Possible future work

Native macOS packaging, localization, a managed background collector, better retention controls, richer sampling-quality indicators, and automated browser regression coverage. These are ideas, not promised delivery dates.

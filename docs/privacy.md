# Privacy and local storage

## What is stored

| Item | Location | Handling |
|---|---|---|
| Quota percentages, observation/reset timestamps, plan label, reset availability | `data/usage.sqlite3` | Local SQLite, account-partitioned |
| Daily activity dates and yes/no/unknown state | Same database | Daily token counts discarded |
| Account partition key | Same database | SHA-256 of normalized email; not anonymous |
| Managed login credentials and runtime-owned files | `data/codex-home/` | Owned by the official Codex runtime |
| Pending reminder timestamp | Browser session storage | Cleared on cancellation/sign-out; no hosted scheduler |

The app requests private directory permissions (0700) and database permissions (0600). Storage is not encrypted by this application. Other software running as the same operating-system user may still read it. Disk encryption and local account protection remain the user's responsibility.

## What is not collected by this application

No conversation text, task prompts, local Codex session-log imports, money totals, or retained token counts. The calendar adds no analytics SDK, advertising, or hosted collection service. The official Codex runtime manages its own authentication and files; its behavior and OpenAI account services are governed by their own policies.

## Network and sharing

The local page talks to the loopback Python service. The official runtime contacts OpenAI for account authentication and reads. Static preview visitors load a hosted website, so normal hosting access logs may exist, but its in-page samples are synthetic and it has no real-account login.

The app-owned home is separate from the normal `~/.codex` configuration. The source repository, preview build, and CI contain no account credentials or personal quota database.

## Retention and removal

Samples remain on disk without an automatic retention limit. Signing out hides the account's history and stops authenticated collection; it does not delete stored history. After stopping the server, remove the checkout's `data/` directory if you want to discard the app-owned data and login state. Removing a local login does not claim to revoke every provider-side session.

Never share `data/`, `auth.json`, a database, authorization URLs, local deployment configuration, or screenshots of real account usage in public issues. Reproduce with the synthetic preview whenever possible.

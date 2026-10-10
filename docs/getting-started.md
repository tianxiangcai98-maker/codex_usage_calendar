# Getting started

## Requirements

- macOS is the primary supported environment. The Python backend is portable, but other operating systems have not received the same UI and sign-in validation.
- Python 3.9 or later (`python3 --version`). Only the standard library is used.
- The official Codex CLI available as `codex` (`codex --version`). Follow [OpenAI's installation instructions](https://github.com/openai/codex#installing-and-running-codex).
- A modern browser. Node.js 20+ is optional for tests.

## Start and sign in

1. Clone the repository and run `python3 server.py` from its directory.
2. Visit `http://localhost:8765`.
3. Choose **连接 ChatGPT**, then **在浏览器中继续**.
4. Finish the official sign-in flow and return to the calendar. Never paste access or refresh tokens into an issue or a source file.

On macOS, `Start Usage Calendar.command` starts the same server and opens the page. If the page appears before the server is ready, refresh it. If Python or Codex cannot be found, use Terminal to verify your PATH.

The app supplies a private `CODEX_HOME` for its Codex child process. A login in your usual terminal Codex installation is intentionally not reused. The managed runtime owns authentication and credential renewal.

## Stop, restart, or switch accounts

Press Control-C in the server terminal to stop collection. Closing a browser tab alone does not stop the Python service. Restarting keeps saved samples.

Use **退出此应用的账户** in the sidebar to sign out, then confirm. Stored quota history stays on disk; another account sees only its own history. A fresh login is required to resume collection.

## Configuration

`CODEX_USAGE_PORT` changes the local port. For example:

```sh
CODEX_USAGE_PORT=8876 python3 server.py
```

Then open `http://localhost:8876`. The macOS launcher uses the default port. The server always binds to loopback; there is no supported remote-host setting.

## Troubleshooting

| Symptom | Check |
|---|---|
| Missing Codex component | Run `command -v codex`; install the official CLI and restart the server. |
| Address already in use | Stop the existing calendar server or choose another port. |
| Login does not complete | Reopen the sign-in dialog, cancel the pending attempt, and retry in the official browser page. |
| Old quota or failed refresh | Check network access and sign-in, then use Refresh. Saved readings remain labeled as stale. |
| An older date has no curve | Daily activity does not contain intraday quota samples; see [data model](data-model.md). |
| Reminder arrived late | The browser or Mac may have been suspended. Reminders require the page to remain open. |
| CLI upgrade changed behavior | Record the CLI version and report a sanitized reproduction. Never attach the app's data directory. |

To remove all local app data, stop the service first and remove this checkout's `data/` directory yourself. That also removes the app-owned runtime home and authentication state. It does not remove your normal `~/.codex` directory. See [privacy](privacy.md).

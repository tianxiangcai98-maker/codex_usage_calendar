# Codex Usage Calendar

A lightweight, macOS-inspired calendar for Codex quota usage. See when quota changes, how much remains, and when it resets—without a wall of token counts.

[中文说明](README.zh-CN.md) · [Try the synthetic preview](https://codex-usage-calendar-preview.vercel.app) · [Getting started](docs/getting-started.md) · [Privacy](docs/privacy.md)

![Calendar with synthetic data and a four-hour time scale](docs/images/demo.png)

## What it does

- Reads current quota through the official Codex app-server and its managed ChatGPT sign-in flow.
- Refreshes every five minutes while the local server runs; opening or returning to the tab also requests an update.
- Displays remaining quota as the width of each activity block. Idle readings and missing samples leave gaps.
- Supports day, five-day, week, month, quarter, and year views, plus a continuous 4-hour → 5-minute time scale.
- Follows the quota windows returned by the API, including weekly-only accounts.
- Marks reset times, estimates runway when evidence is sufficient, and optionally reminds you of a short-window reset while the page remains open.
- Distinguishes sampled dates, confirmed historical activity without curves, explicit zero activity, and unknown records.

This is an independent community project, not an official OpenAI product. The interface is currently Chinese. It is a local browser app, not a signed or notarized native Mac application.

## Run locally

Requirements: macOS, Python 3.9+, and the official [Codex CLI](https://github.com/openai/codex) on your PATH. The account integration was checked with Codex CLI 0.144.5; later versions may change the protocol. Node.js 20+ is needed only for development tests.

```sh
git clone https://github.com/tianxiangcai98-maker/codex_usage_calendar.git
cd codex_usage_calendar
python3 server.py
```

Open **http://localhost:8765**, select **连接 ChatGPT**, and complete sign-in in the official browser page. You can also double-click `Start Usage Calendar.command` on macOS. No Python packages or frontend build dependencies are needed to run the app.

The app uses its own Codex home under `data/codex-home/`. It does not import your normal Codex login or read your conversation logs. Signing out here preserves stored quota history and does not sign out another Codex installation. See [setup and troubleshooting](docs/getting-started.md).

## Local app vs. preview

| | Local account app | Hosted preview |
|---|---|---|
| Data | Your authenticated quota readings | Generated, fictional samples |
| Sign-in | Official Codex managed flow | Disabled |
| Storage | Private local `data/` directory | None for real accounts |
| Runtime | Python + Codex CLI + browser | Static HTML, CSS, JavaScript |

The preview is for interaction review. It does not provide hosted OAuth or cloud collection. Vercel may require sign-in according to the deployment's existing protection settings.

## Limits worth understanding

The personal account interface provides current quota and daily activity summaries, not a historical intraday quota series. Old activity dates can be shown, but missing percentage curves cannot be reconstructed. A gap means no quota change was observed or samples are missing; it is not proof that no task was running. Rounded API readings limit timing precision. See [data semantics](docs/data-model.md) and [known limitations](docs/limitations.md).

## Documentation

| Guide | Contents |
|---|---|
| [Getting started](docs/getting-started.md) | Install, sign in, run, stop, troubleshoot |
| [User guide](docs/user-guide.md) | Calendar, scale, gaps, forecasts, reminders |
| [Architecture](docs/architecture.md) | Components, account flow, local API |
| [Data model](docs/data-model.md) | Quota windows, samples, historical evidence |
| [Privacy](docs/privacy.md) | What stays on disk and what leaves the machine |
| [Development](docs/development.md) | Tests, preview build, source layout |
| [Deployment](docs/deployment.md) | Static preview and stable Vercel alias |
| [Limitations](docs/limitations.md) | Supported boundaries and future work |
| [Security](SECURITY.md) | Reporting vulnerabilities and release checks |
| [Contributing](CONTRIBUTING.md) | Changes, reviews, safe bug reports |

## Development checks

```sh
python3 scripts/check.py
python3 build-preview.py
python3 scripts/audit_public.py
```

Tests use synthetic fixtures and mocked account calls. They do not require credentials. GitHub Actions runs tests and a redacted Gitleaks scan. See [development](docs/development.md).

## License

[MIT](LICENSE). SVG icons and motion styles in this repository are application-owned implementations. Apple fonts, SF Symbols assets, third-party transition libraries, and the Codex binary are not redistributed. See [third-party notices](THIRD_PARTY_NOTICES.md).

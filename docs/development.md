# Development

## Toolchain

Python 3.9+ runs the app and build scripts without third-party Python dependencies. Node.js 20+ runs the JavaScript regression suites. The live account connection additionally needs the official Codex CLI; the tests and synthetic preview do not.

```sh
python3 scripts/check.py
python3 build-preview.py
python3 -m http.server 8767 --bind 127.0.0.1 --directory preview
```

Open `http://localhost:8767`. Generated preview files are ignored by Git. `preview/preview-data.js` is the only tracked file inside that directory; it defines fictional scenarios for both quota layouts. Modify root UI files, then rebuild.

## Test coverage

`test_server.py` mocks managed account calls and tests persistence, isolation, login/logout, failed refreshes, and daily sanitization. `test_http.py` checks loopback and file-serving boundaries without account credentials. JavaScript suites cover plan normalization, historical states, estimates, curve geometry, activity gaps, reset markers, and consistent demo fixtures. `scripts/check.py` also parses inline scripts from the real and generated interfaces.

Inspect the rendered interface after UI changes: both demo plans, the 4-hour and 5-minute scale endpoints, default/automatic zoom, month-to-day navigation, information popovers, dialogs, and reduced-motion behavior. Do not use personal screenshots as public fixtures.

## Release hygiene

`scripts/audit_public.py` examines tracked or staged files without echoing potential secret values. It rejects private runtime paths, credential artifacts, local deployment IDs, embedded raster payloads, and common key formats. This supplements Gitleaks, not replaces it. CI scans full Git history using a pinned Gitleaks version with redacted output.

Before a release, run checks from a clean checkout, inspect `git diff --cached --stat` and `git ls-files`, and scan the Git history. If a secret was ever committed, removing it from the latest file is insufficient: revoke it and remove it from history before publishing.

## Source ownership

UI icon SVGs and the motion styles are maintained in this project under MIT. Keep new dependencies documented in `THIRD_PARTY_NOTICES.md`. Do not copy proprietary design assets or transition-library source into the repository.

## Localization

`i18n.js` contains four-column source/English/French/Japanese messages, including
accessible labels, tooltips and backend-owned errors. Parameterized messages use
`{0}`, `{1}`, etc. The small presentation layer preserves each text node's source
so live polling and repeated language switches remain reversible; it never
translates HTML, input values, URLs or account payloads. Add complete messages,
not substring replacements. Mark proper language names with `data-no-i18n`.

Dates and times use `calendarI18n.locale` and `calendarI18n.timeOptions` with `Intl`.
`calendarI18n.weekStart` determines calendar ordering, not quota reset rules.
Test both quota layouts, all overview modes, live errors and dialogs, changing
regions independently of language, explicit 12/24-hour time, reload persistence,
and switching back to Chinese. `test_i18n.js` checks catalog completeness,
placeholder parity, localized numbers and backend error coverage.

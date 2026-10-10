# Codex Usage Calendar

- Keep account-connected operation local. The hosted preview is synthetic and must never include real account data.
- Read `docs/development.md` and run `python3 scripts/check.py` for relevant changes. Inspect rendered states for UI work.
- Root UI files are the source; `build-preview.py` generates the preview. Only `preview/preview-data.js` is tracked in that output directory.
- For an authorized upstream preview release, use `python3 deploy-preview.py`. It reads ignored local configuration, waits for Ready, and updates the same alias. Return the stable URL, not a changing deployment URL.
- The upstream alias is `https://codex-usage-calendar-preview.vercel.app`. Forks must configure their own alias; do not change another project's deployment.
- Never commit or upload `data/`, `.vercel/`, local deployment settings, private screenshots, credentials, raw account responses, or research notes containing personal account observations.
- Run `python3 scripts/audit_public.py` before publishing. Preserve unknown history states, account isolation, observed usage gaps, and reduced-motion behavior.

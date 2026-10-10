# Contributing

Start with a bug report or a focused pull request. For larger product changes, describe the problem and intended behavior before doing a broad redesign.

1. Fork and clone the repository. Install Python 3.9+ and Node.js 20+.
2. Work in root source files; rebuild the preview instead of editing generated copies.
3. Run `python3 scripts/check.py` and `python3 scripts/audit_public.py`.
4. Check the rendered synthetic preview for UI changes. Include a synthetic screenshot when useful.
5. Explain what changed, why, and how you verified it. Keep unrelated reformatting out of the PR.

Preserve account isolation, original quota readings, unknown-vs-zero history semantics, idle gaps, reduced-motion support, and the separation between authenticated local use and a fictional hosted preview. Do not hardcode plan prices as quota capabilities.

Never attach `data/`, real account screenshots, browser authorization URLs, logs containing credentials, or local deployment configuration. The public source must not depend on a contributor's absolute filesystem paths, team IDs, or installed proprietary assets.

New contributions are made under the repository's MIT license. Document any third-party dependency and its license. Follow the [code of conduct](CODE_OF_CONDUCT.md). Report vulnerabilities through [Security](SECURITY.md), not a public issue.

# Security policy

## Report a vulnerability

Use [GitHub's private vulnerability reporting](https://github.com/tianxiangcai98-maker/codex_usage_calendar/security/advisories/new). Do not place tokens, authentication URLs, personal data, or exploit details involving a real account in a public issue. Include a minimal synthetic reproduction and relevant version numbers. If you exposed a credential, revoke it with its provider; deleting a post or file alone does not revoke it.

The latest `main` branch and latest release are the maintained versions. This is a community project with no guaranteed response SLA or independent security certification.

## Security boundaries

The Python service binds to 127.0.0.1, validates Host, rejects cross-site fetches, and requires a matching Origin for state-changing requests. Static assets are allowlisted. Account credentials remain in the official runtime's private app-owned home and are not returned by the calendar's API. Errors avoid exposing provider payloads. Login URLs must use an expected HTTPS provider hostname.

The local service is not designed to defend against a malicious process already running as the same OS user. Inline UI scripts/styles currently require corresponding CSP allowances. Do not expose the server through a tunnel, public network interface, or reverse proxy.

## Publication checks

- Exclude runtime homes, databases, authentication files, `.env` files, local deployment settings, and real-data screenshots.
- Scan tracked content and full commit history; do not print detected secret values into CI logs.
- Use synthetic fixtures and a clean first commit when opening an existing private prototype.
- Keep CI permissions read-only, and do not provide account credentials to tests or preview builds.

The initial public release was prepared from an explicit source allowlist and checked with Gitleaks plus project-specific publication checks. Those checks reduce risk; they are not a guarantee against every possible secret format or application vulnerability.

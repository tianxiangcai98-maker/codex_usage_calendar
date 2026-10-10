# Deploying the synthetic preview

The account-connected Python service is loopback-only. Do not deploy it to Vercel, GitHub Pages, or a public host as a multi-user backend. This guide publishes only the fictional interface preview.

## Static build

```sh
python3 build-preview.py
```

The builder copies the UI, browser modules, and application-owned SVGs into `preview/`, alongside the synthetic fixture. It does not copy `data/`, Python code, real screenshots, or deployment credentials. Verify the directory before uploading. Generated output is ignored by Git.

## Vercel and a fixed address

Install and authenticate the Vercel CLI using [Vercel's official instructions](https://vercel.com/docs/cli). Link the preview directory to a project you own:

```sh
cd preview
vercel link
cd ..
```

Create the git-ignored `preview-deploy.local.json`:

```json
{
  "scope": "your-vercel-team-slug",
  "alias": "your-calendar-preview.vercel.app"
}
```

Do not use the upstream project's alias for a fork. Then publish:

```sh
python3 deploy-preview.py
```

The script builds, deploys **only** `preview/` as a preview deployment, waits for Ready, assigns the fixed alias, and verifies that the alias points to the new deployment. A failed build leaves the previous alias in place. If alias assignment fails, the deployment still exists and the CLI reports the error; resolve the domain/project permissions before retrying. The script does not disable existing Vercel access protection.

The upstream demonstration uses [codex-usage-calendar-preview.vercel.app](https://codex-usage-calendar-preview.vercel.app). Its maintainers update that same address for each release. Local project/team IDs, access tokens, and CLI authentication never belong in Git.

## GitHub

The repository hosts source, documentation, tests, and a synthetic screenshot. GitHub Actions runs validation; it does not deploy or request any OpenAI/Vercel credentials. No GitHub Pages OAuth backend is configured. A future Pages workflow would need to account for repository-subpath asset URLs; the current build expects to be served from a domain root.

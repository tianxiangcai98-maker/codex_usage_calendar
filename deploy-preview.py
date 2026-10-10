#!/usr/bin/env python3
"""Build the synthetic preview and update its stable Vercel alias on success."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / 'preview'
# Personal team settings stay in a git-ignored local configuration file.
CONFIG_PATH = ROOT / 'preview-deploy.local.json'
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
SCOPE = CONFIG.get('scope')
ALIAS = CONFIG.get('alias')


def vercel(*args, as_json=False):
    command = ['vercel', *args, '--scope', SCOPE]
    if as_json:
        command += ['--format', 'json']
    result = subprocess.run(command, cwd=PREVIEW, text=True, capture_output=True)
    if result.stderr:
        print(result.stderr, file=sys.stderr, end='', flush=True)
    if result.returncode:
        print(result.stdout, end='', flush=True)
        raise SystemExit(result.returncode)
    if not as_json:
        print(result.stdout, end='', flush=True)
        return None
    return json.loads(result.stdout)


def main():
    linked = json.loads((PREVIEW / '.vercel' / 'project.json').read_text())
    if not linked.get('projectId') or not linked.get('orgId'):
        raise SystemExit('Link preview/ to your Vercel project first.')
    if not SCOPE or not ALIAS or '://' in ALIAS or '/' in ALIAS:
        raise SystemExit('Configure scope and alias in preview-deploy.local.json; see docs/deployment.md.')
    subprocess.run([sys.executable, str(ROOT / 'build-preview.py')], cwd=ROOT, check=True)
    result = vercel('deploy', '.', '--yes', '--no-wait', '--target', 'preview', as_json=True)
    deployment = result.get('deployment', result)
    url = deployment['url']
    print('Build: ' + url, flush=True)
    info = vercel('inspect', url, '--wait', '--timeout', '45s', as_json=True)
    info = info.get('deployment', info)
    if (info.get('readyState') or info.get('state') or info.get('status', '')).upper() != 'READY':
        raise SystemExit('Build is not Ready; the stable preview was not changed.')
    vercel('alias', 'set', url, ALIAS)
    current = vercel('inspect', ALIAS, as_json=True)
    current = current.get('deployment', current)
    if current.get('id') != info.get('id'):
        raise SystemExit('The stable alias does not match the new deployment.')
    print('Stable preview: https://' + ALIAS, flush=True)


if __name__ == '__main__':
    main()

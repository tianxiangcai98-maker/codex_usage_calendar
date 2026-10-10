#!/usr/bin/env python3
"""Check publishable Git content. Report only rule/path/line, never values."""
from pathlib import Path
import argparse
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--staged', action='store_true', help='Inspect index blobs rather than working-tree files')
args = parser.parse_args()
paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
patterns = {
    'private-key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'provider-key': r'\bsk-[A-Za-z0-9_-]{20,}',
    'github-key': r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'jwt': r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    'local-user-path': r'/(?:Users|home)/[A-Za-z0-9._-]+/',
    'deployment-account-id': r'\b(?:prj|team)_[A-Za-z0-9]{16,}',
    'embedded-raster': r'data:image/(?:png|jpeg|webp);base64,',
}
blocked_parts = {'data', '.vercel', '__pycache__', 'node_modules', '.venv'}
blocked_names = {'auth.json', 'credentials.json', 'preview-deploy.local.json', 'HISTORY-API-NOTES.md', 'history_import.py', 'prototype-v1.html'}
findings = []
for name in filter(None, paths):
    p = Path(name)
    if any(part in blocked_parts for part in p.parts) or p.name in blocked_names or p.name.startswith(('.env', 'verified-')) or p.suffix in {'.db', '.sqlite', '.sqlite3', '.pem', '.key', '.log', '.p12', '.pfx'}:
        findings.append((name, 0, 'private-artifact'))
        continue
    if args.staged:
        raw = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
    else:
        raw = (ROOT / name).read_bytes()
    if p.suffix == '.png':
        if name != 'docs/images/demo.png':
            findings.append((name, 0, 'unreviewed-image'))
        continue
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        findings.append((name, 0, 'unreviewed-binary'))
        continue
    for rule, expression in patterns.items():
        for hit in re.finditer(expression, text):
            findings.append((name, text[:hit.start()].count('\n') + 1, rule))
    for hit in re.finditer(r'[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})', text):
        if hit.group(1) not in {'example.test', 'example.com', 'example.org', 'users.noreply.github.com'}:
            findings.append((name, text[:hit.start()].count('\n') + 1, 'personal-email'))
if findings:
    for name, line, rule in findings:
        print(f'{name}:{line}: {rule}')
    sys.exit(1)
print(f'PASS: {sum(bool(p) for p in paths)} tracked files; no publication-policy findings')

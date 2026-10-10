#!/usr/bin/env python3
"""Run credential-free backend, geometry, fixture, and syntax checks."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

run(sys.executable, '-m', 'unittest', 'discover', '-p', 'test_*.py', '-v')
for test in sorted(ROOT.glob('test_*.js')):
    run('node', str(test))
run(sys.executable, 'build-preview.py')
for path in [*ROOT.glob('*.js'), *ROOT.glob('preview/*.js')]:
    run('node', '--check', str(path))
for path in (ROOT / 'index.html', ROOT / 'preview/index.html'):
    for source in re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', path.read_text(), re.S):
        if source.strip():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js') as script:
                script.write(source)
                script.flush()
                run('node', '--check', script.name)
print('PASS: all backend, JavaScript, preview, and syntax checks')

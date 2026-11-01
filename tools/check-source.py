#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""Check local Markdown file links without the site-building dependencies."""

import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

def owned_pages(root):
    if (root / '.git').exists():
        paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                        cwd=root, text=True).split('\0')
        return [root / path for path in sorted(set(paths)) if path.endswith('.md') and (root / path).is_file()]
    return [path for path in root.rglob('*.md') if not any(
        part in ('out', 'target', '.git', '.repo', '.venv', '.agent') for part in path.relative_to(root).parts)]


def check(root):
    root = Path(root).resolve()
    metadata = json.loads((root / 'component.json').read_text())
    generated = {'modules.md'} if metadata.get('documentation', {}).get('catalog') else set()
    for source in owned_pages(root):
        content = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', source.read_text(), flags=re.M | re.S)
        for target in re.findall(r'!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)', content):
            target = target[1:-1] if target.startswith('<') else target.split(' "', 1)[0]
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
                continue
            path = (source.parent / unquote(parsed.path)).resolve()
            if not path.is_relative_to(root):
                raise ValueError(f'{source}: cross-repository links must use their published URL: {target}')
            if not path.exists() and str(path.relative_to(root)) not in generated:
                raise ValueError(f'{source}: missing local link: {target}')


if __name__ == '__main__':
    check(sys.argv[1])
    print('Markdown source links are valid')

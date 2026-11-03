#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""Check local Markdown file links without the site-building dependencies."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from inventory import description, published_pages, source_files

def owned_pages(root):
    return [root / path for path in published_pages(source_files(root), description(root))]


def check(root):
    root = Path(root).resolve()
    metadata = description(root)
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

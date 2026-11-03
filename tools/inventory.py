# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""One source and publication inventory for checking and rendering repositories."""

import json
import os
from pathlib import Path
import subprocess


def source_files(root):
    root = Path(root)
    if (root / '.git').exists():
        paths = subprocess.check_output(
            ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
            cwd=root, text=True).split('\0')
    else:
        paths = []
        for parent, directories, files in os.walk(root):
            directories[:] = [name for name in directories
                              if not name.startswith('.') and name not in ('out', 'target')]
            paths.extend(str((Path(parent) / name).relative_to(root)) for name in files)
    return sorted(name for name in set(paths) if name and (root / name).is_file()
                  and not any(part.startswith('.') for part in Path(name).parts)
                  and not name.startswith(('legacy/', 'third_party/')))


def description(root):
    path = Path(root) / 'component.json'
    return json.loads(path.read_text()) if path.is_file() else {}


def published_pages(files, metadata):
    pages = [name for name in files if name.endswith('.md')]
    selected = metadata.get('documentation', {}).get('pages')
    if selected is not None:
        if (not isinstance(selected, list) or any(not isinstance(name, str) for name in selected)
                or len(selected) != len(set(selected)) or any(name not in pages for name in selected)):
            raise ValueError('documentation.pages must select unique tracked Markdown files')
        pages = selected
    if 'README.md' not in pages:
        raise ValueError('the documentation entry point must be README.md')
    return pages

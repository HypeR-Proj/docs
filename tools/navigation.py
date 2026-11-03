# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""Repository-owned navigation with readable titles for unspecified pages."""

from html.parser import HTMLParser
from pathlib import PurePosixPath
import re

import markdown


class FirstHeading(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.done = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h1' and not self.done:
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'h1' and self.active:
            self.active = False
            self.done = True

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def page_title(path, source):
    if path == 'README.md':
        return 'Overview'
    heading = FirstHeading()
    heading.feed(markdown.markdown(source, extensions=['fenced_code']))
    title = ''.join(heading.parts).strip()
    if title:
        return title
    # Preserve identifiers such as SMMUv3 instead of lowercasing them.
    return re.sub(r'[-_]+', ' ', PurePosixPath(path).stem).strip() or path


def navigation(source, pages, metadata):
    """Map source-relative names to staged Markdown; append unlisted pages."""
    selected = metadata.get('documentation', {}).get('nav', [])
    used = set()

    def entries(items):
        if not isinstance(items, list):
            raise ValueError('documentation.nav must contain ordered lists of title entries')
        result = []
        for item in items:
            if not isinstance(item, dict) or len(item) != 1:
                raise ValueError('each navigation entry must have one title')
            title, value = next(iter(item.items()))
            if not isinstance(title, str) or not title.strip():
                raise ValueError('navigation titles must be nonempty strings')
            if isinstance(value, list):
                if not value:
                    raise ValueError('navigation groups must not be empty')
                result.append({title: entries(value)})
            elif isinstance(value, str) and value in pages and value not in used:
                used.add(value)
                result.append({title: pages[value]})
            else:
                raise ValueError('navigation pages must be unique selected Markdown sources')
        return result

    result = entries(selected)
    community = {'CONTRIBUTING.MD', 'CODE_OF_CONDUCT.MD', 'SECURITY.MD', 'LICENSE.MD', 'CHANGELOG.MD'}
    for original in sorted(pages, key=lambda name: (
            name != 'README.md', PurePosixPath(name).name.upper() in community, name)):
        if original not in used:
            staged = pages[original]
            result.append({page_title(original, (source / staged).read_text()): staged})
    return result

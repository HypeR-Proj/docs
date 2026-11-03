#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""Render the generated documentation's diagrams with browser networking disabled."""

from html.parser import HTMLParser
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


class Diagrams(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'code' and 'language-mermaid' in dict(attrs).get('class', '').split():
            self.count += 1


def check(site):
    pages = []
    for path in sorted(site.rglob('*.html')):
        source = Diagrams()
        source.feed(path.read_text())
        if source.count:
            pages.append((path, source.count))
    if not pages:
        raise ValueError('the browser fixture must contain actual Mermaid diagrams')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(offline=True)
            page = context.new_page()
            page.set_default_timeout(15000)
            for path, expected in pages:
                page.goto(path.resolve().as_uri())
                if page.evaluate('navigator.onLine'):
                    raise ValueError('browser networking was not disabled')
                page.wait_for_function('''count => {
                    const diagrams = document.querySelectorAll('.mermaid[data-processed="true"] svg');
                    return diagrams.length === count && [...diagrams].every(svg => {
                        const bounds = svg.getBoundingClientRect();
                        return bounds.width > 0 && bounds.height > 0
                            && svg.textContent.trim().length > 0
                            && !svg.querySelector('.error-icon, .error-text');
                    });
                }''', arg=expected)
                print(f'offline diagrams rendered: {path.relative_to(site)} ({expected})')
        finally:
            browser.close()


if __name__ == '__main__':
    check(Path(sys.argv[1]))

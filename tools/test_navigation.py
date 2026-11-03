# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
import tempfile
import unittest

from build import build
from navigation import navigation, page_title


class NavigationTests(unittest.TestCase):
    def test_titles_use_first_heading_and_preserve_technical_names(self):
        self.assertEqual(page_title('README.md', '# Long module name'), 'Overview')
        self.assertEqual(page_title('docs/smmuv3.md', '# ARM **SMMUv3** and `I/O`\n'),
                         'ARM SMMUv3 and I/O')
        self.assertEqual(page_title('docs/VM_ABI.md', 'No heading'), 'VM ABI')
        self.assertEqual(page_title('docs/guide.md', '```text\n# Not a heading\n```\n\nReal title\n=========='),
                         'Real title')
        self.assertEqual(page_title('page.md', '# First\n\n# Second'), 'First')

    def test_explicit_groups_order_and_default_append(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            for path, text in [('index.md', '# Root'), ('core.md', '# Native ABI'),
                               ('io.md', '# I/O isolation'), ('extra.md', '# More detail')]:
                (source / path).write_text(text)
            pages = {'README.md': 'index.md', 'core.md': 'core.md', 'io.md': 'io.md', 'extra.md': 'extra.md'}
            metadata = {'documentation': {'nav': [
                {'Start here': 'README.md'}, {'Architecture': [{'IOMMU': 'io.md'}, {'ABI': 'core.md'}]}]}}
            self.assertEqual(navigation(source, pages, metadata), [
                {'Start here': 'index.md'}, {'Architecture': [{'IOMMU': 'io.md'}, {'ABI': 'core.md'}]},
                {'More detail': 'extra.md'}])
            self.assertEqual(navigation(source, pages, {})[0], {'Overview': 'index.md'})
            (source / 'CONTRIBUTING.md').write_text('# Contributing')
            community_pages = {**pages, 'CONTRIBUTING.md': 'CONTRIBUTING.md'}
            self.assertEqual(navigation(source, community_pages, {})[-1],
                             {'Contributing': 'CONTRIBUTING.md'})
            for value in (None, 'README.md', ['README.md'], [{'': 'README.md'}],
                          [{'Missing': 'missing.md'}], [{'Group': []}],
                          [{'One': 'README.md'}, {'Group': [{'Again': 'README.md'}]}],
                          [{'Too': 'README.md', 'Many': 'core.md'}]):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    navigation(source, pages, {'documentation': {'nav': value}})

    def test_real_site_has_selected_labels_and_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'repository'
            root.mkdir()
            (root / 'README.md').write_text('# Test module\n')
            (root / 'io.md').write_text('# I/O isolation\n')
            (root / 'abi.md').write_text('# Native ABI\n')
            (root / 'component.json').write_text(json.dumps({'documentation': {'nav': [
                {'Start here': 'README.md'}, {'Design': [{'IOMMU design': 'io.md'}]}]}}))
            site = build(root, Path(temporary) / 'published', 'example', 'a' * 40)
            text = (site / 'index.html').read_text()
            self.assertLess(text.index('Start here'), text.index('IOMMU design'))
            self.assertLess(text.index('IOMMU design'), text.index('Native ABI'))
            self.assertIn('href="io.html"', text)
            self.assertIn('href="abi.html"', text)


if __name__ == '__main__':
    unittest.main()

# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from build import build
from inventory import description, published_pages, source_files

spec = importlib.util.spec_from_file_location('check_source', Path(__file__).with_name('check-source.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class InventoryTests(unittest.TestCase):
    def fixture(self, root):
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        (root / 'README.md').write_text('# Example\n\n[Guide](guide.md)\n')
        (root / 'guide.md').write_text('# Guide\n\n[Source](code.rs)\n')
        (root / 'code.rs').write_text('// example\n')
        (root / 'vendor').mkdir()
        (root / 'vendor/README.md').write_text('[Missing](missing.md)\n')
        (root / 'component.json').write_text(json.dumps(
            {'documentation': {'pages': ['README.md', 'guide.md']}}))

    def test_source_checker_and_real_builder_share_the_selected_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'repository'
            root.mkdir()
            self.fixture(root)
            checker.check(root)
            site = build(root, Path(temporary) / 'published', 'example', 'a' * 40)
            self.assertTrue((site / 'index.html').is_file())
            self.assertTrue((site / 'guide.html').is_file())
            self.assertFalse((site / 'vendor/README.html').exists())
            self.assertIn('https://github.com/HypeR-Proj/example/blob/' + 'a' * 40 + '/code.rs',
                          (site / 'guide.html').read_text())
            (root / 'guide.md').write_text('# Guide\n\n[Broken](missing.md)\n')
            with self.assertRaisesRegex(ValueError, 'missing local link'):
                checker.check(root)
            with self.assertRaises(subprocess.CalledProcessError):
                build(root, Path(temporary) / 'broken', 'example', 'a' * 40)

    def test_invalid_page_selection_fails_both_entry_points(self):
        for selected in ([], ['guide.md'], ['README.md', 'absent.md'],
                         ['README.md', 'README.md'], 'README.md', [False]):
            with self.subTest(selected=selected), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / 'repository'
                root.mkdir()
                self.fixture(root)
                (root / 'component.json').write_text(json.dumps({'documentation': {'pages': selected}}))
                with self.assertRaises(ValueError):
                    checker.check(root)
                with self.assertRaises(ValueError):
                    build(root, Path(temporary) / 'output', 'example', 'a' * 40)

    def test_default_inventory_excludes_hidden_and_archived_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'README.md').write_text('# Root\n')
            for name in ('legacy', 'third_party', '.private', 'out', 'target'):
                (root / name).mkdir()
                (root / name / 'ignored.md').write_text('[Invalid](missing)')
            self.assertEqual(published_pages(source_files(root), description(root)), ['README.md'])
            checker.check(root)


if __name__ == '__main__':
    unittest.main()
